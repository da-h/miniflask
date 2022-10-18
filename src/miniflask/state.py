import sys
import re
from collections.abc import MutableMapping
from inspect import getsource

from colored import fg, attr

from .util import get_varid_from_fuzzy, highlight_module, get_relative_id
from .exceptions import StateKeyError, RegisterError


class temporary_state:
    def __init__(self, _state, variables):
        self.variables = variables
        self.state = _state
        self.saved = {}
        self.did_not_exist = []
        super().__init__()

    def __enter__(self):
        for key, val in self.variables.items():
            if key in self.state:
                self.saved[key] = self.state[key]
            else:
                self.did_not_exist.append(key)
            self.state[key] = val
        return self.state

    def __exit__(self, _type, _value, _traceback):
        del _type, _value, _traceback
        for key, val in self.saved.items():
            self.state[key] = val
        for key in self.did_not_exist:
            del self.state[key]


relative_import_re = re.compile(r"(\.+)(.*)")


class state(MutableMapping):
    def __init__(self, module_name, internal_state_dict, state_dependencies):  # pylint: disable=super-init-not-called
        r"""!... is a local dict
        Global Variables, but Fancy. ;)

        Every event gets called with a state-Object as its first argument.
        This is the modules **local** and **persistent** variable scope.

        **Local dict**:
        You can use this object like a persistent dict for all events defined in the same module.

        **Fuzzy matching**:  
        The module dict will use local variables first. If however, a variable does not exist locally, miniflask will look in the parent modules as well.
        See [fuzzy matching](./02-dict operations.md).

        **Global dict**:  
        Every variable defined by plain `register_defaults` gets prepended by the modules *unique id*.
        The internaal global variable dict of the program can also be used explicitly by using `state.all`.
        **Note**, however, that the fuzzy matching should be sufficient for most applications.
        Also, this feature, should of course be used with caution, as it may break the modularity of the code.


        Examples:
        Using local variables.
        ```python
        def dosomething(state, event):
            print(state["var"])
            print()
            state["var"] *= 500
            print(state["var"])
            print("This module uses", len(state), "variables.")
            for key in state:
                print("This module is using the variable", key)

        def register(mf):
            mf.register_defaults({
                "var": 42
            })
            mf.register_event('dosomething',dosomething)
        ```

        Global variable state
        ```python
        def dosomethingelse(state, event):

            # this uses the variables of any global
            print(state.all["modules1.var"])
            print()
            state.all["modules1.var"] *= 500
            print(state.all["modules1.var"])

        def register(mf):
            mf.register_event('dosomethingelse',dosomethingelse)
        ```
        """  # noqa: W291

        self.all = internal_state_dict
        self.dependencies = state_dependencies
        self.module_id = module_name
        self.fuzzy_names = {}
        # self.temporary = temporary_state(self)

    def scope(self, module_name):
        r"""
        Working on multiple scopes.

        The default behaviour of state is to work on the local module variables of the module the state is defined in.
        Working on module variables of other modules is easily possible with this command.

        Returns:
        A new `state` variable bound to a given scope.

        Args:
        - `module_name`: The module id to use for the variable.

        Examples:

        Using scopes of distinct modules at the same time:
        ```python
        otherstate = state.scope("other.module.id")
        state["varInThisModule"]
        otherstate["varInOtherModule"]
        ```

        Sharing scopes with another module locally:
        ```python
        def dosomethingelse(state, event):
            state = state.scope("module1")

            # this uses the variables of module1, even though used in module2
            print(state["var"])
            print()
            state["var"] *= 500
            print(state["var"])

        def register(mf):
            mf.register_event('dosomethingelse',dosomethingelse)
        ```
        """  # noqa: W291

        return state(module_name, self.all, self.dependencies)

    def temporary(self, variables):
        r"""
        Change a variables temporarily.

        Instead to change the state before/after an event, you can use the following construction using `state.temporary`:

        Args:
        - `variables`: A dict of variables to change temporarily.

        Examples:
        ```python
        def dosomething(state, event):
            print("in event", state["variable"])

        def main(state, event):

            print("before event", state["variable"])
            with state.temporary({
                "variable": 42:
            }):
                event.dosomething()
            print("after event", state["variable"])

        def register(mf):
            mf.register_defaults({
                "variable": 0
            })
            mf.register_event('dosomething',dosomething)
            mf.register_event('main',main)
        ```
        """  # noqa: W291

        return temporary_state(self, variables)

    def __contains__(self, name):

        # check if key already known from this state-object
        if name in self.fuzzy_names:
            return self.fuzzy_names[name] in self.all

        # intern the string
        name = sys.intern(name)

        # search for fuzzy local variable
        varid, _ = get_relative_id(name, self.module_id, ensure_local=True)
        found_varids = get_varid_from_fuzzy(varid, self.all.keys(), fuzzy_fill=False)

        # if no matching unique varid found, alert user
        if len(found_varids) != 1:

            # search for fuzzy global variable
            found_varids = get_varid_from_fuzzy(name, self.all.keys(), fuzzy_fill=True)
            if len(found_varids) > 1:
                return False

        # no module found with both variants
        if len(found_varids) == 0:
            return False

        # cache for next use
        self.fuzzy_names[name] = found_varids[0]
        return True

    def __delitem__(self, name):

        # check if key already known from this state-object
        if name in self.fuzzy_names:
            del self.all[self.fuzzy_names[name]]
            del self.fuzzy_names[name]
            return

        # intern the string
        name = sys.intern(name)

        # search for fuzzy local variable
        varid, _ = get_relative_id(name, self.module_id, ensure_local=True)
        found_varids = get_varid_from_fuzzy(varid, self.all.keys(), fuzzy_fill=False)

        # if no matching varid found, alert user
        if len(found_varids) != 1:

            # search for fuzzy global variable
            found_varids = get_varid_from_fuzzy(name, self.all.keys(), fuzzy_fill=True)
            if len(found_varids) > 1:
                raise _create_excpetion_notunique(found_varids, name)

        # no module found with both variants
        if len(found_varids) == 0:
            raise _create_excpetion_notfound(self.module_id, varid, name)

        # cache for next use
        del self.all[found_varids[0]]

    def __getitem__(self, name):
        r"""!dict operations
        State dict & its fuzzy variable matching.

        The state dict implements all commonly used `dict` operations.
        - `state["var"]`  
            (i.e.: `__getitem__`)
        - `state["var"] = 42`  
            (i.e.: `__setitem__`)
        - del `state["var"]`  
            (i.e.: `__delitem__`)
        - `"var" in state`  
            (i.e.: `__contains__`)

        Thus, working inside a module with local only variables is straightforward.
        Let us consider the following module structure:
        ```
        parentdir.module1
        parentdir.module1.submodule
        parentdir.module1.submodule.subsubmodule
        parentdir.module2
        parentdir.module2.submodule
        ```

        Currently, we are programming inside of `subsubmodule`.
        Fuzzy matching denotes the order that is used by miniflask to find a variable in the surrounding modules, if we query a variable that, however, does not exist locally. For instance, consider the call `state["var"]` inside the module `subsubmodule`.

        With the features of parent modules (and their automatic loading), miniflask tests all parent modules before proceeding to find the module anywhere in the loaded moduules.
        Thus, the search order is:
        1. as module variable: `parentdir.otherdir.module1.submodule.subsubmodule.var`
        1. as module variable: `parentdir.otherdir.module1.submodule.var`
        1. as module variable: `parentdir.otherdir.module1.var`
        1. as module variable: `parentdir.otherdir.var`
        1. as module variable: `parentdir.var`
        1. as global Variable: `var`
        1. finally, it would search for any variable that contains: `var`  
            (as glob pattern `*.var.*`, `var.*` or `*.var`)

        This scoping scheme allows parent modules to define more basic variables that can be used by their corresponding child modules.

        {.alert}
        **Note**: This scheme makes most uses of [`set_scope`](../../08-API/03-register(mf\)-Object/15-set_scope.md) and [`redefine_scope`](../../08-API/03-register(mf\)-Object/09-redefine_scope.md) obsolete.
        """  # noqa: W291

        # check if key already known from this state-object
        if name in self.fuzzy_names:
            return self.all[self.fuzzy_names[name]]

        # intern the string
        name = sys.intern(name)

        # search for fuzzy local variable
        varid, _ = get_relative_id(name, self.module_id, ensure_local=True)
        found_varids = get_varid_from_fuzzy(varid, self.all.keys(), fuzzy_fill=False)

        # if no matching varid found, alert user
        if len(found_varids) != 1:
            # raise StateKeyError("Variable-Identifier '%s' is not unique. Found %i variables:\n\t%s\n\n    Call:\n        %s" % (highlight_module(name), len(found_varids), "\n\t".join(found_varids), name))

            # search for fuzzy local variable
            found_varids = get_varid_from_fuzzy(name, self.all.keys(), fuzzy_fill=True)
            if len(found_varids) > 1:
                raise _create_excpetion_notunique(found_varids, name)

        # no module found with both variants
        if len(found_varids) == 0:
            raise _create_excpetion_notfound(self.module_id, varid, name)

        # cache for next use
        self.fuzzy_names[name] = found_varids[0]
        return self.all[found_varids[0]]

    def __setitem__(self, name, val):

        # check if key already known from this state-object
        if name in self.fuzzy_names:
            self.all[self.fuzzy_names[name]] = val
            return

        # intern the string
        name = sys.intern(name)

        # search for fuzzy local variable
        varid, _ = get_relative_id(name, self.module_id, ensure_local=True)
        found_varids = get_varid_from_fuzzy(varid, self.all.keys(), fuzzy_fill=False)

        # if no matching varid found, alert user
        if len(found_varids) != 1:

            # search for fuzzy global variable
            found_varids = get_varid_from_fuzzy(name, self.all.keys(), fuzzy_fill=True)
            if len(found_varids) > 1:
                raise _create_excpetion_notunique(found_varids, name)

        # no module found with both variants, assume a internal module variable is meant to be created
        if len(found_varids) == 0:
            found_varids = [self.module_id + "." + name if self.module_id else name]

        # cache for next use
        self.fuzzy_names[name] = found_varids[0]
        self.all[found_varids[0]] = val

    # disables deepcopy(state), as it is tightly bounded to other miniflask objects
    def __deepcopy__(self, memo):
        del memo
        return self

    def __iter__(self):
        return filter(lambda key: key.startswith(self.module_id), self.all)

    def __len__(self):
        return len(list(filter(lambda key: key.startswith(self.module_id), self.all)))


def _create_excpetion_notfound(module_id, varid, name):
    varid_split = varid.split(".")
    tried_text = "\n\t".join(["- as module variable: '%s'" % (fg('green') + ".".join(varid_split[:-i]) + "." + varid_split[-1] + attr('reset')) for i in range(1, len(varid_split))])
    return StateKeyError("Variable '%s' not known.\n(Module %s attempted to access this variable.)\n\nI tried the following interpretations in that order:\n\t%s\n\t- as global Variable: '%s'\n\t- finally, I tried any ordered selection that contains the keys: [%s]." % (fg('green') + name + attr('reset'), highlight_module(module_id), tried_text, fg('green') + name + attr('reset'), ', '.join("'" + fg('green') + n + attr('reset') + "'" for n in name.split("."))))


def _create_excpetion_notunique(found_varids, name):
    return StateKeyError("Variable-Identifier '%s' is not unique. Found %i variables:\n\t%s\n\n    Call:\n        %s" % (highlight_module(name), len(found_varids), "\n\t".join(found_varids), name))


class as_is_callable():  # pylint: disable=too-few-public-methods
    def __init__(self, obj):
        self.obj = obj

    def __call__(self, *args, **kwargs):
        return self.obj(*args, **kwargs)


class optional:
    def __init__(self, variable_type):
        self.type = variable_type

    def __call__(self, state, event):  # pylint: disable=redefined-outer-name
        return self.type

    def str(self, asciicodes=True, color_attr=attr):
        if not asciicodes:
            color_attr = lambda x: ''  # noqa: E731 no-lambda
        return color_attr('dim') + "'" + str(self.type) + "' or '" + "None" + "' ⟶   " + color_attr('reset') + str(self.dependencies)

    def __str__(self):
        return self.str()


state_regex = re.compile(r"state\[(\"|\')((?:\.*\w+)+)\1\]")
string_regex_g2 = r"([\"'])((?:\\\1|(?:(?!\1)).)*)(?:\1)"
if_else_regex = re.compile(r"(.*)if\s+(.*)\s+else(.*)")
state_in_regex = re.compile(string_regex_g2 + r"\s+in\s+state")


class state_node:
    def __init__(self, varid, mf, caller_traceback, cliargs=False, parsefn=False, is_ovewriting=False, missing_argument_message=None, fn=None):
        self.varid = varid
        self.mf = mf
        self.caller_traceback = caller_traceback
        self.cliargs = cliargs
        self.parsefn = parsefn
        self.is_ovewriting = is_ovewriting
        self.cli_overwritten = False
        self.missing_argument_message = missing_argument_message

        self.depends_on = []
        self.depends_alternatives = {}

        self.fn = fn
        self.fn_src = getsource(self.fn) if self.fn is not None else None

        if self.fn_src is not None:
            if "lambda" not in self.fn_src:
                raise RegisterError(f"Expected lambda expression, but found {self.fn_src}")
            fn_lambda_split = self.fn_src.split("lambda")
            if len(fn_lambda_split) > 2:
                raise RegisterError(f"Lambda expression is required to consist of a single lambda-keyword in that line of source, but found: {self.fn_src}")
            self.fn_src = fn_lambda_split[1].strip().rstrip(',')

            # find all state-dependencies in the source code
            self.depends_on = [m[1] for m in state_regex.findall(self.fn_src)]

            # we allow one simple alternative: state[x] if x in state else y
            if_matches = if_else_regex.findall(self.fn_src.split(":")[1]) if self.fn_src else []
            if len(if_matches) > 1:
                raise RegisterError(f"Lambda expression with only one if-else-statement of the form `EXPR(state[x]) if x in state else OTHEREXPR` allowed, but found multiple in: {self.fn_src}")

            # we know parse for lambda expressions of the form:
            # expr1(x,y,...) if x in state and y in state ... else expr2
            if len(if_matches) == 1:
                true_expr_src = if_matches[0][0]
                false_expr_src = if_matches[0][2]
                state_cond_src = if_matches[0][1]
                false_expr_dependencies = [m[1] for m in state_regex.findall(false_expr_src)]
                for bad_keyword in ["or", "not"]:
                    if f" {bad_keyword} " in state_cond_src:
                        raise RegisterError(f"Lambda expression allows only if-else-statements of the form `EXPR(state[x]) if x in state and ... else OTHEREXPR` allowed, but found `{bad_keyword}` in condition of: {self.fn_src}")
                state_cond_vars = [m[1] for cond_src in state_cond_src.split(" and ") for m in state_in_regex.findall(cond_src)]

                # if the condition is also used in the true_expr_src we can ignore it later to check for its alternatives
                for state_cond_var in state_cond_vars:
                    true_expr_regex = re.compile(r"state\s*\[\s*([\"'])" + state_cond_var + r"\1\s*\]")
                    if true_expr_regex.search(true_expr_src):
                        self.depends_alternatives[state_cond_var] = false_expr_dependencies

    def str(self):
        return str(self.varid)

    def __str__(self):
        return self.str()

    def __repr__(self):
        content = [self.str()]
        if self.fn_src is not None:
            content.append(f"fn=λ {self.fn_src}")
        if len(self.depends_on) > 0:
            content.append(f"depends_on={self.depends_on}")
        return f"variable({', '.join(content)})"

    # ------------------- #
    # dependency routines #
    # ------------------- #
    @staticmethod
    def calculate_affects_lists(node_dict):
        for node in node_dict.values():
            node.affects = []
        for node in node_dict.values():
            for depends_on_varid in node.depends_on:
                node_dict[depends_on_varid].affects.append(node.varid)

    @staticmethod
    def topological_sort(node_dict):  # noqa: C901
        nodes = list(node_dict.values())
        varid2index = {node.varid: i for i, node in enumerate(nodes)}
        visited = [False for i in range(len(nodes))]
        sorted_nodes, cycles, unresolved = [], [], []

        # note: rewrite this recursive DFS to while-loop if RecursionError occurs
        def DFS(node_i, parentnodes=None):
            if parentnodes is None:
                parentnodes = []

            node = nodes[node_i]

            if node in parentnodes:
                cycles.append(parentnodes + [node])
                return

            parentnodes = parentnodes + [node]

            if visited[node_i]:
                return

            visited[node_i] = True

            for dependency in node.depends_on:
                if dependency not in node.mf.state:

                    # in case dependency has an alternative, we can ignore this if all alternatives exist
                    if dependency in node.depends_alternatives:
                        alternatives_exist = True
                        for alternative_dependency in node.depends_alternatives[dependency]:
                            if alternative_dependency not in node.mf.state:
                                alternatives_exist = False
                                break
                        if alternatives_exist:
                            continue

                    unresolved.append((node, dependency))
                    continue
                if hasattr(node.mf.state, "fuzzy_names"):
                    dependency_varid = node.mf.state.fuzzy_names[dependency]
                else:
                    dependency_varid = dependency
                dependency_i = varid2index[dependency_varid]
                DFS(dependency_i, parentnodes=parentnodes)

            sorted_nodes.append(node)

        for i in range(len(nodes)):
            DFS(i)

        return sorted_nodes, cycles, unresolved

    @staticmethod
    def evaluate(nodes, global_state):
        for node in nodes:
            varid = node.varid
            if node.cli_overwritten or node.fn_src is None:
                continue
            if node.fn:
                if node.fn_src.split(":")[0].strip() == "state":
                    global_state[varid] = node.fn(node.mf.state)
                else:
                    global_state[varid] = node.fn()
