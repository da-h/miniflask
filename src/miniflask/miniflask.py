# global modules
import sys
import re
import inspect
import traceback
from functools import partial
from os import path, listdir, linesep, get_terminal_size
from importlib import import_module
from pathlib import Path
from enum import Enum, EnumMeta
from argparse import ArgumentParser, REMAINDER as ARGPARSE_REMAINDER
from typing import List
from pkgutil import resolve_name
import random

from colored import fg, attr

# package modules
from .exceptions import (
    save_traceback,
    format_traceback_list,
    RegisterError,
    StateKeyError,
)
from .event import event, event_obj
from .state import state, as_is_callable, optional as optional_default, state_node
from .dummy import miniflask_dummy
from .util import getModulesAvail, EnumAction, get_relative_id, Unit, UnitValue, make_unitvalue_argparse
from .util import (
    highlight_error,
    highlight_name,
    highlight_module,
    highlight_loading,
    highlight_loading_default,
    highlight_loaded_default,
    highlight_loading_module,
    highlight_loaded_none,
    highlight_loaded,
    highlight_event,
    str2bool,
    get_varid_from_fuzzy,
    get_full_base_module_name,
)
from .settings import listsettings


def print_info(*args, color=fg("green"), msg="INFO"):
    print(
        color + attr("bold") + msg + attr("reset") + color + ": " + attr("reset"),
        *args,
        attr("reset"),
    )


def get_default_args(func):
    signature = inspect.signature(func)
    return {
        k: v.default
        for k, v in signature.parameters.items()
        if v.default is not inspect.Parameter.empty and v.default is not None
    }


def registerPredefined(modules_avail):
    for m in ["modules", "events", "info", "settings", "definitions"]:
        module_name_id = "miniflask." + m
        importname = "miniflask." + m
        modules_avail[module_name_id] = {
            "id": module_name_id,
            "importname": importname,
            "lowpriority": False,
        }


# ================ #
# MiniFlask Kernel #
# ================ #
class miniflask:
    def __init__(self, *module_repositories, debug=False):
        r"""miniflask.init
        Initializes miniflask with a module repository.

        Miniflask searches for folders of a specific format, named modules.
        By initializing miniflask, we have to define the folders miniflask will look in.

        Args:
        - `module_repositories`: a string, a list python packages to search module repositories in.
            - **String**: specifies a single import path to the module repository to use.
                (The directory name will also be repository name / module prefix for all modules inside that folder.)
            - **List**: specifies multiple import path to the module repository to use.
                (The directory names will also be repository names / module prefixes for all modules inside that folders.)
        - `debug`: Debug Mode
            Debug Mode disables catching/printing + beautifying Exceptions. Also, it disables truncating the traceback messages of internal miniflask functions.

        Examples:
        ```python
        # Single Module Repository (named "allmodules")
        # -> modules inside of allmodules will get the prefix "allmodules."
        mf = miniflask.init("allmodules")

        # Multiple Module Repositories (named "publicmodules" and "privatemodules")
        mf = miniflask.init(["privatemodules", "publicmodules"])
        ```

        """  # noqa: W291
        self._instance_id = str(random.getrandbits(128))
        self.debug = debug
        if not module_repositories:
            return

        # module dir to be read from
        self.module_repositories = {m.split(".")[-1]: m for m in module_repositories}

        # arguments from cli-stdin
        self.settings_parser = ArgumentParser(
            usage=sys.argv[0] + " modulelist [optional arguments]"
        )
        self.cli_required_arguments = []
        self.default_modules = []
        self.default_modules_overwrites = []
        self.bind_events = True

        # internal
        self.halt_parse = False
        self.argparse_called = False
        self.event_objs = {}
        self.event_data = {}
        self.event = event(self, optional=False)
        self.event.optional = event(self, optional=True)
        self.state = {}
        self.state_registrations = (
            {}
        )  # saves the information of the respective variables (initial value, registration, etc.)
        self._state_overwrites_list = []
        self.units = {}
        self.modules_loaded = {}
        self.modules_ignored = []
        self.modules_avail = getModulesAvail(self.module_repositories)
        registerPredefined(self.modules_avail)
        self._varid_list = []
        self._recently_loaded = []
        try:
            self._consolecolumns, self._consolerows = get_terminal_size(0)
        except:  # noqa: E722  pylint: disable=bare-except
            self._consolecolumns, self._consolerows = 80, 40

    # ------- #
    # helpers #
    # ------- #
    def print_heading(self, *args, color=fg("blue"), margin=8):
        line = "—" * self._consolecolumns
        if len(args) > 0:
            s = " ".join(args)
            line = line[:margin] + " " + s + " " + line[margin + len(s) + 2:]
        print()
        print(color + attr("bold") + line + attr("reset"))

    def print_recently_loaded(self, prepend="", loading_text=highlight_loading):
        last = ""
        last_formatted = ""
        for i, mod in enumerate(self._recently_loaded):
            module_id = (
                module_id_formatted
            ) = module_id = mod.miniflask_obj.module_id_initial

            # if previously printed parent, make the module_id shorter
            if module_id.startswith(last):
                module_id_formatted = last_formatted + module_id[len(last):]

            is_last = i == len(self._recently_loaded) - 1
            has_children = len(mod.miniflask_obj._recently_loaded) > 0
            part_of_next = i < len(self._recently_loaded) - 1 and self._recently_loaded[
                i + 1
            ].miniflask_obj.module_id_initial.startswith(module_id)
            if is_last:
                tree_symb = "    "  # noqa: E221
                tree_symb_current = "╰── "  # "└── "
            elif has_children:
                tree_symb = "│   "  # noqa: E221
                tree_symb_current = "│   "
            else:
                tree_symb = "│   "  # noqa: E221
                tree_symb_current = "├── "  # "├── "
            if not part_of_next:
                if prepend == "":
                    print(loading_text(module_id_formatted))
                else:
                    print(
                        prepend + tree_symb_current + loading_text(module_id_formatted)
                    )
            if len(mod.miniflask_obj._recently_loaded) > 0:
                mod.miniflask_obj.print_recently_loaded(
                    prepend + tree_symb, loading_text
                )
            last = module_id
            last_formatted = (
                loading_text(module_id_formatted) if part_of_next else module_id
            )

    # ==================== #
    # module introspection #
    # ==================== #

    def import_module(self, module_name):
        module_spec = self.modules_avail[module_name]
        return import_module(module_spec["importname"])

    # module event
    def getModuleEvents(self, module_id, mf=None):
        r"""
        Retrieve List of Events defined by specified module.

        Args:
        - `module_id`: (required)
            unique module id
        - `mf`:
            Internal variable to specify the miniflask object to register the events into. If set to `None` no events will be registered.
        """  # noqa: W291
        if not mf:
            mf = miniflask_dummy()

        # load module
        mod = self.import_module(module_id)
        if not hasattr(mod, "register"):
            return []

        mod.register(mf)
        return mf.getEvents()

    # pretty print of all available modules
    def showModules(
        self,
        directory=None,
        prepend="",
        id_pre=None,
        with_event=True,
        direct_print=True,
        visited=None,
    ):  # noqa: C901 too-complex pylint: disable=inconsistent-return-statements

        out = ""
        any_module_found = False

        if visited is None:
            visited = set()

        if not directory:
            for basename, base_module_path in self.module_repositories.items():
                if base_module_path.startswith("."):
                    stack_frame = inspect.stack()[
                        2
                    ]  # the frame in which miniflask.init has been called
                    callee_module_path = Path(stack_frame.filename).parent
                    base_module_path = (
                        get_full_base_module_name(callee_module_path) + base_module_path
                    )
                if base_module_path.startswith("miniflask"):
                    continue

                module = resolve_name(base_module_path)
                directory = module.__path__[0]

                self.showModules(
                    directory,
                    prepend=prepend,
                    id_pre=basename if id_pre is None else id_pre + "." + basename,
                    with_event=with_event,
                )
            return

        if id_pre is None:
            id_pre = path.basename(directory)
        if len(prepend) == 0:
            out += "\n"
            out += highlight_name(path.basename(id_pre)) + "\n"
        dirs = [
            d
            for d in listdir(directory)
            if path.isdir(path.join(directory, d)) and not d.startswith("_")
        ]
        visited_next = visited.union(
            set(path.realpath(path.join(directory, d)) for d in dirs)
        )
        for i, d in enumerate(dirs):
            if d.startswith("."):
                continue
            if path.exists(path.join(directory, d, ".ignoredir")):
                continue
            if path.realpath(path.join(directory, d)) in visited:
                continue
            module_id = id_pre + "." + d if id_pre != "" else d

            is_module = path.exists(path.join(directory, d, ".module"))
            is_lowpriority_module = path.exists(path.join(directory, d, ".lowpriority"))
            if is_module:
                shortestid = self.getModuleShortId(module_id)
                any_module_found = True
            has_shortid = is_module and shortestid == d

            if i == len(dirs) - 1:
                tree_symb = "└── "
                is_last = True
            else:
                tree_symb = "├── "
                is_last = False
            append = (
                " " + fg("blue") + "(" + shortestid + ")" + attr("reset")
                if is_module and not has_shortid
                else ""
            )
            append += (
                attr("dim") + " (low-priority module)" + attr("reset")
                if is_lowpriority_module
                else ""
            )
            out += (
                prepend
                + tree_symb
                + (highlight_name(d) if is_module else d)
                + append
                + "\n"
            )

            tree_symb_next = "     " if is_last else "│    "
            if is_module:
                if with_event:
                    events = self.getModuleEvents(module_id)
                    if len(events) > 0:
                        for e in events:
                            unique_flag = "!" if e[1] else ">"
                            print(
                                prepend
                                + tree_symb_next
                                + unique_flag
                                + " "
                                + highlight_event(e[0])
                            )

            out_sub, module_found_sub = self.showModules(
                path.join(directory, d),
                prepend=prepend + tree_symb_next,
                id_pre=module_id,
                with_event=with_event,
                direct_print=False,
                visited=visited_next,
            )
            if module_found_sub:
                out += out_sub
        if direct_print:
            print(out)
            return
        return out, any_module_found

    # pretty print loaded modules
    def __str__(self):
        if len(self.modules_loaded) == 0:
            return highlight_loaded_none("No Loaded Modules")
        return highlight_loaded("Loaded Modules:", self.modules_loaded.keys())

    # =================== #
    # module registration #
    # =================== #

    # get unique id of a moodule
    def getModuleId(self, module_id):
        r"""
        Performs a fuzzy search on a module identifier.

        # Note {.alert}
        - Raises `ValueError` if either the module identifier is non-unique or not known.
        - Otherwise returns the full module id.
        """
        module_ids = self.modules_avail.keys()
        module = module_id.replace(".", r"\.(.*\.)*")

        # first, try direct identifier
        r = re.compile(r"^(.*\.)?%s$" % module)
        found_modules = list(filter(r.match, module_ids))

        # if no default module found, check for related identifier
        if len(found_modules) == 0:
            r = re.compile(r"^(.*\.)?%s(\..*)?$" % module)
            found_modules = list(filter(r.match, module_ids))

        # if more than one module found, exclude all low-priority modules
        if len(found_modules) > 1:
            found_modules = list(
                filter(
                    lambda mid: not self.modules_avail[mid]["lowpriority"],
                    found_modules,
                )
            )

        # if more than one module found let the user know
        if len(found_modules) > 1:
            raise ValueError(
                highlight_error()
                + "Module-Identifier '%s' is not unique. Found %i modules:\n\t%s"
                % (
                    highlight_module(module_id),
                    len(found_modules),
                    "\n\t".join(found_modules),
                )
            )

        # no module found with both variants
        if len(found_modules) == 0:
            raise ValueError(
                highlight_error()
                + "Module '%s' not known." % highlight_module(module_id)
            )

        # module_id is a unique identifier
        module = found_modules[0]
        return self.modules_avail[module]["id"]

    # get short id of a moodule
    def getModuleShortId(self, module_id):
        r"""
        Given the full unique module id this method returns the shortest module id that is still uniquely assignable by miniflask.
        """
        if module_id not in self.modules_avail:
            raise ValueError(
                highlight_error()
                + "Module '%s' not known." % highlight_module(module_id)
            )
        uniqueId = self.modules_avail[module_id]["id"].split(".")

        # find the shortest substring to match a module uniquely
        for i in range(len(uniqueId) - 1, 0, -1):
            shortid = ".".join(uniqueId[i:])
            try:
                if module_id == self.getModuleId(shortid):
                    return shortid
            except ValueError:
                pass
        return module_id

    # maps 'folder.subfolder.module.list.of.vars' to 'folder.subfoldder.module'
    def _getModuleIdFromVarId(
        self, varid, varid_list=None, scope=None
    ):  # noqa: C901 too-complex

        # try to use scope as module id
        if scope is not None:
            try:
                module_id = self.getModuleId(scope)
                if varid.startswith(scope):
                    varid = varid[len(scope) + 1:]
                return module_id, varid
            except ValueError:
                pass

        # no we have to work out which module may be meant
        if varid_list is None:
            varid_list = varid.split(".")
        for i in range(len(varid_list) - 1, 0, -1):
            test_id = ".".join(varid_list[:i])
            try:
                return self.getModuleId(test_id), ".".join(varid_list[i:])
            except ValueError:
                pass

        # no id could be derived
        return None, ".".join(varid_list)

    # loads module (once)
    def load(
        self,
        module_name,
        verbose=True,
        auto_query=True,
        loading_text=highlight_loading,
        as_id=None,
        bind_events=True,
    ):  # noqa: C901 too-complex  pylint: disable=too-many-statements
        r"""
        Directly load a module by name

        # Note {.alert}
        - This loads all parent modules automatically *before* actual loading.
        - To prevent this, add the global variable `register_parents = False` to the modules `__init__.py`.

        Args:
        - `module_name`: (required)
            Module name to be loaded directly.
            - Prepending the module name with a `-` sign lets miniflask ignore the module.
            - Can be a fuzzy or complete module identifier
            - Can be a `str`, a python `list` or string containing a list of modules seperated by a comma.
        - `verbose`: (default: `True`)
            Visualizes the module tree that has been loaded during this call.
        - `auto_query`: (default: `True`)
            Enables/Disables fuzzy search.
        - `as_id`: (default: `None`)
            The module id to be used to register the module upon loading.
        - `bind_events`: (default: `None`)
            Registers all events of the module to be loaded.

        Examples:
        ```python
        # using fuzzy module names
        mf.load("mymodule")

        # ignore future calls to load mymodule
        mf.load("-mymodule")

        # allows fuzzy module queries as long as the query returns a unique module
        mf.load("the.full.module.id")
        mf.load("the.module.id")
        mf.load("the.full.id")
        mf.load("the.id")
        mf.load("full.id")
        mf.load("module.id")
        ```
        """  # noqa: W291

        # load list of modules
        if isinstance(module_name, str) and "," in module_name:
            module_name = module_name.split(",")
        if isinstance(module_name, list):
            for m in module_name:
                self.load(
                    m,
                    verbose=verbose,
                    auto_query=auto_query,
                    loading_text=loading_text,
                    as_id=as_id,
                    bind_events=bind_events,
                )
            return

        if module_name.startswith("-"):
            self.modules_ignored.append(module_name[1:])
            return
        if module_name in self.modules_ignored:
            return

        # get id
        if auto_query:
            module_name = self.getModuleId(module_name)
        elif module_name not in self.modules_avail:
            raise ValueError(
                highlight_error()
                + "Module '%s' not known." % highlight_module(module_name)
            )

        # check if already loaded
        if module_name in self.modules_loaded and as_id is None:
            return

        # load module
        mod = self.import_module(module_name)
        if not hasattr(mod, "register"):
            raise ValueError(
                highlight_error()
                + "Module '%s' does not register itself." % module_name
            )
        module_name = module_name if as_id is None else as_id
        mod.miniflask_obj = miniflask_wrapper(module_name, self)
        mod.miniflask_obj.bind_events = bind_events
        self.modules_loaded[module_name] = mod

        # first load all parents
        # (starting with root parent, specializing with every step)
        if not hasattr(mod, "register_parents") or mod.register_parents:
            module_path = module_name.split(".")
            for depth in range(1, len(module_path)):
                parent_module = ".".join(module_path[:depth])
                if (
                    parent_module in self.modules_avail
                    and parent_module not in self.modules_loaded
                ):
                    parent_as_id = (
                        None if as_id is None else ".".join(as_id.split(".")[:-1])
                    )
                    self.load(
                        parent_module,
                        verbose=False,
                        auto_query=False,
                        loading_text=loading_text,
                        as_id=parent_as_id,
                        bind_events=bind_events,
                    )

        # remember loaded modules
        self._recently_loaded.append(mod)

        # register events
        mod.register(mod.miniflask_obj)
        self.event[module_name] = mod.miniflask_obj._defined_events
        self.event.optional[module_name] = mod.miniflask_obj._defined_events

        # loading message
        if verbose:
            self.print_recently_loaded(prepend="", loading_text=loading_text)
            self._recently_loaded = []

    # register default module that is loaded if none of glob is matched
    def register_default_module(
        self, module, required_event=None, required_id=None, overwrite_globals=None
    ):
        r"""
        Specify modules to load if specific behaviour is not yet matched by already loaded modules.

        In more detail, this allows modules to be loaded depending on the choice of loaded modules upon start of the whole script.
        Typically, the requirement will be tested after parsing the modules given using cli-arguments.

        # Note {.alert}
        - It is only possibly to specify a requirement based on an event name *or* a module id regex.
        - In case of multiple `register_default_module` calls with the same dependency (i.e. the same required event), the calls are parsed as follows:
            - in case the given default-modules differ in these calls
                - the latest settings (i.e. `overwrite_globals`-dict) are used
                - the settings of the unrealised calls are ignored
            - in case the given default-modules are equal, all those calls are realized, and thus
                - all settings are loaded, but
                - the latest settings overwrite the older settings

        Args:
        - `module`: (required)
            Module name to be loaded if the specified requirement is not met.
            - Can be fuzzy or complete
            - Can be a python list of module names.
        - `required_event`:
            Specifies the event name to be used as a condition to be met, otherwise the specified modules will be loaded.
        - `required_id`:
            Specifies a regular expression that shall be used as a test condition. If there was no match against all loaded module ids, the specified modules will be loaded.
        - `overwrite_globals`:
            This argument takes a `dict` and binds a `register_globals` call to be called after the specified have been called.
            (If no modules are loaded due to already fulfilled conditions, the dict will be discarded.)

        Examples:
        ```python
        # loads mymodule if no module registered a myevent event
        mf.register_default_module("mymodule", required_event="myevent")

        # loads mymodule & mymodule2 if no module registered a myevent event
        mf.register_default_module(["mymodule","mymodule2"], required_event="myevent")

        # loads mymodule if no module matches against the regular expression
        mf.register_default_module("mymodule", required_id="my\.folder\..*")

        # loads mymodule if no module matches against the regular expression
        # & overwrites some default values in case mymodule gets loaded
        mf.register_default_module("mymodule", required_id="my\.folder\..*", overwrite_globals={
            "othermodule.value": 42
        })
        ```
        """  # noqa: W291
        if overwrite_globals is None:
            overwrite_globals = {}
        if required_event and required_id:
            raise RegisterError(
                "Default Modules should depend either on a event interface OR a regular expression. However, both are given"
            )
        if not required_event and not required_id:
            raise RegisterError(
                "Default Modules should depend either on a event interface OR a regular expression. However, none are given"
            )
        self.default_modules.append(
            (module, required_event, required_id, overwrite_globals, save_traceback())
        )
        self.default_modules_overwrites.append(
            (module, required_event, required_id, overwrite_globals, save_traceback())
        )

    # saves function to a given (event-)name
    def register_event(self, name, fn, unique=True, call_before_after=True):
        r"""
        Specify a function to register using a given name.

        {.alert}
        Note, that `init`, `main` and `final` are predefined event names that are called automatically on every [`mf.run()`](../../08-API/02-miniflask-Instance/10-run.md) call.

        Args:
        - `name`: (required)
            Event name to bind the function with.
        - `fn`: (required)
            The function to be bound to the name.

            **Function Signatures**:
            - There are no requirements to the function signatures for plain events.
                However, it is possible to prepend the argument list using the keywords: `state`, `event` and/or `mf` in any order.
                Miniflask will look for these keywords in any event signature and pass the module specific objects,
                - `state`, (see also the API-Reference for [state](../05-state))
                - `event` (see also the API-Reference for [event](../04-event)) and
                - `mf` (the same that is passed during module registration process, see also the API-Reference for [`register(mf)` Object]("../03-register(mf)-Object").
                objects.
            - **Before events**:
                These events get called in between the argument passing of any event and the function call.

                To register such an event, prepend the event name with the keywords `before_`.

                ```python
                def before_fn():
                    ...
                ```

                It is of course possible to modify the function arguments (see below). The important part is that a before-event specifies the arguments that are passed to the actual event call, both positional and non-positional arguments.

                In case the before event is non-unique, the arguments will be passed from one after event to the next until their result will be passed to the actual event call.
            - **After events**:
                These events get called in between the function call and the pass of its return statement.

                To register such an event, prepend the event name with the keywords `after_`.

                ```python
                def after_fn():
                    ...
                ```

                It is of course possible to modify the function arguments or the function result (see below). The important part is, as above, that a after-event specifies the return value that is passed to callee of the event.

                In case the after event is non-unique, the results and arguments will be passed from one after event to the next.
            - **Manipulating arguments & results of events**:
                - Any `before_`/`after_` event gets called with a unique event object, that behaves just like the *normal* event object.
                - This new event-object has a dict-attribute `.hook`
                - **`before_`-events can read and manipulate** the function call arguments *before* the actual event will be called using `event.hook["args"]` and `event.hook["kwargs"]`
                - **`after_`-events can read** the function call arguments *after* the actual event has been called with (including the changes of potential `before_`-hooks using `event.hook["args"]` and `event.hook["kwargs"]`
                   (**Note**: Any modification will only change the arguments for future `after_`-events but not for the function call itself.)
                - `after_`-events can additionally alternate the return value of the event by modifying `event.hook["result"]`.
                - both event types can access the name of the actual event-name using `event.hook["name"]`
        - `unique`: (Default: `True`)
            - Unique functions can only be registered by exactly one module.
              **Note**: Miniflask will throw an error if multiple modules register the same event.
            - Non-Unique events will be called in sequence of registration. The result of such an event is a list of all return values.
            - **Note**: Before/After events will be called only **once for non-unique event calls**.
        - `call_before_after`: (Default: `True`)
            Turning this flag off will disable the possibility to hook to this function using before/after events.
            This is especially useful, if the before/after event shall be directly defined.

        Examples:
        **Simple Example**:
        ```python
        def fn(var):
            return var * (var + 1)

        mf.register_event("myevent", fn)

        # this line may be placed anywhere in the code basis
        print(mf.event.myevent(6)) # you know already the result, don't ya?
        ```

        **Example using signatures & before/after events**:
        ```python
        def dosomething(val):
            print("event called with value: %i" % val)
            return val

        def main(event):
            print("event returned value: %i" % event.dosomething(42))

        def before_dosomething(event):
            print("before_-event called")
            event.hook["args"][0] *= 2

        def after_dosomethingl(event):
            print("after_-event called")
            event.hook["result"] += 1

        def register(mf):
            mf.register_event('dosomething', dosomething)
            mf.register_event('main', main)
            mf.register_event('before_dosomething', before_dosomething, unique=False)
            mf.register_event('after_dosomething', after_dosomething, unique=False)
        ```

        """  # noqa: W291
        if not self.bind_events:
            return

        # check if is unique event. if yes, check if event already registered
        if name in self.event_objs and (unique or self.event_objs[name].unique):
            eobj = (
                self.event_objs[name].modules
                if not self.event_objs[name].unique
                else [self.event_objs[name].modules]
            )

            # catch some user errors
            if not unique and self.event_objs[name].unique:
                raise RegisterError(
                    highlight_error()
                    + "Event '%s' has been registered as `unique` before, but as `non-unique` now. Please check the registrations.\n\t(Imported by %s)"
                    % (
                        highlight_event(name),
                        ", ".join(
                            ["'" + highlight_module(e.module_name) + "'" for e in eobj]
                        ),
                    )
                )
            if unique and not self.event_objs[name].unique:
                raise RegisterError(
                    highlight_error()
                    + "Event '%s' has been registered as `non-unique` before, but as `unique` now. Please check the registrations.\n\t(Imported by %s)"
                    % (
                        highlight_event(name),
                        ", ".join(
                            ["'" + highlight_module(e.module_name) + "'" for e in eobj]
                        ),
                    )
                )

            raise RegisterError(
                highlight_error()
                + "Event '%s' is unique, and thus, cannot be imported twice.\n\t(Imported by %s)"
                % (
                    highlight_event(name),
                    ", ".join(
                        ["'" + highlight_module(e.module_name) + "'" for e in eobj]
                    ),
                )
            )

        # register event
        if name in self.event_objs:
            self.event_objs[name].fn.append(fn)
            self.event_objs[name].modules.append(self)
        else:
            self.event_objs[name] = event_obj(fn, unique, self, call_before_after)

    # overwrite state defaults
    # Note: the problem lies in the fact that the true id of a variable is defined as scope.key,
    #       however scope can be empty if key is meant as a reference in the global scope=="".
    #       Otherwise, this function would be a lot simpler.
    def register_defaults(
        self,
        defaults,
        scope="",
        overwrite=False,
        cliargs=True,
        parsefn=True,
        caller_traceback=None,
        missing_argument_message=None,
    ):
        r"""
        Register variables bound to a module.

        The variable registration process is the miniflask feature to
        - allow users to overwrite *default parameters* based on the value types defined during registration using the cli,
            (See the section [Modules/Register Settings](../../03-Modules/02-Register-Settings.md) in the documentation for details how to overwrite registered variables using the CLI.)
        - allow variables to form *dependency chains* in between modules
            (”if one variable is like this then the other variable should be like that“)
        - but also to allow *other modules* to be predefined sets of default parameters themselves.

        In case of unexpected redefinition of a variable, miniflask will raise an error.

        ## Supported Variable Types
        - Integer (`int`)
        - Floats (`float`)
        - Strings (`string`)
        - Boolean (`bool`)
        - Enums (`Enum`)
        - One-dimensional lists of basic types (e.g. `[int]`)
        - One-dimensional tuples of basic types (e.g. `(int,int)`)
        - Lambda Expressions of the form `lambda state, event: ...`.
            - As with events, lambdas can take a `state`-argument. Miniflask will automatically find out what variables are required when parsing the expressions.
            - Miniflask will also automatically detect circular dependencies and missing arguments in the variable dependency graph.
            - Note that only "simple" if-statements of the following form are implemented for Lambda-Expressions. See below for examples of what is supported.
            - Examples:
                ```
                lambda: somefunction("arguments")
                lambda state: state["myvariable"]
                lambda state: (state["myvariable"] * 5) + state["othervariable"]
                lambda state: somefunction(state["myvariable"]) + state["othervariable"]
                lambda state: state["myvariable"] * 5 if "myvariable" in state else state["othervariable"]
                lambda state: state["myvariable"] * state["othervariable"] if "myvariable" in state and "othervariable" in state else state["yetanothervariable"]
        - [**Units**](../../08-API/02-miniflask-Instance/10-register_unit.md) (`Units`)  
            Units are custom numbers with multiple representations.

        Note:
        This method is the base method for variable registrations.
        Consider also the specializations for local `mf` objects:
        - [`register_defaults`](../../08-API/03-register(mf\)-Object/11-register_defaults.md)
        - [`register_globals`](../../08-API/03-register(mf\)-Object/13-register_globals.md)
        - [`register_helpers`](../../08-API/03-register(mf\)-Object/14-register_helpers.md)
        - [`overwrite_defaults`](../../08-API/03-register(mf\)-Object/06-overwrite_defaults.md)
        - [`overwrite_globals`](../../08-API/03-register(mf\)-Object/08-overwrite_globals.md)

        Args:
        - `defaults`: (required)
            Dict of variables to define under the defined scope (variable name -> value).
        - `scope`:
            Scope to define variables in.
            (Defaults to global scope. This is the main difference to the local mf-object variants.)
        - `overwrite`:
            Setting to `True` enables redefinition of predefined variables. Raises error if the variables to overwrite are not known.
        - `cliargs`:
            Setting to `False` disables to change that variable using CLI.
        - `parsefn`:
            Setting to `False` disables function parsing if the value is a method itself. Doing so may be required if the value to be saved is a function itself. By default miniflask will call function values to set the value dynamically as part of the variable dependency chain.
        - `caller_traceback`:
            The traceback to use when an error occurs during registration of any of the listed variables. (Defaults to current traceback).
        - `missing_argument_message`:
            String to show the user whenever one of the given (and required) arguments are not present after CLI-parsing.

        Examples:
        ```python
        def register(mf):
            class TESTENUM(Enum):
                VALUEA = 0
                VALUEB = 1

            mf.register_defaults({
                "variableA": 42,
                "variableB": "Hello",
                "variableC": True,
                "variableD": [1,2,3,5,8,13] # only lists of same type are supported
                "variableEnum": TESTENUM.VALUEA
                "variableEnum2": TESTENUM   # rquires the user to specify the value by name
            })
        ```
        """  # noqa: W291
        if scope is None:
            scope = ""

        # save exception for later
        if not caller_traceback:
            caller_traceback = save_traceback()

        # ensures that self.state is also usable for miniflask-wrapper
        if hasattr(self.state, "all"):
            local_state = self.state.all
        else:
            local_state = self.state

        # now register every key-value pair
        for key, val in defaults.items():

            # unique & full varname is fully defined using scope
            varname = scope + "." + key if len(scope) > 0 else key
            key_split = varname.split(".")

            # get module id from global varname identifier
            module_id, key = self._getModuleIdFromVarId(varname, key_split, scope=scope)
            if module_id is not None:

                # recreate actual key
                module_id = self.getModuleId(module_id)
                varname = module_id + "." + key

            # overwrite parsefn for as_is_callable object
            if isinstance(val, (as_is_callable, optional_default)):
                parsefn = False

            # pre-initialize variables using an intermediate representation
            # note:
            #   - some registrations need to be deferred, because we do not want overwrite-registrations to be dependent on module-call-orderings
            #     thus, this enables to have base-settings loaded before the actual to-be-overwritten module is loaded by the user
            #   - we need to remember overwrites for later because we need to check if the variables to overwrite actually exist
            #    (we can only be sure, that the varname is a unique varid if we are not overwriting here)
            #   - actual initialization is done when all modules have been parsed
            #   - design decision is here to have the dependency nodes in a seperate dict and only the state actually store data
            #   - we also save all tracebacks implicitly in case we need this information due to an error
            is_dependency = (
                callable(val)
                and not isinstance(val, type)
                and not isinstance(val, EnumMeta)
                and not isinstance(val, Unit)
                and parsefn
            )
            node = state_node(
                varid=varname,
                mf=self,
                caller_traceback=caller_traceback,
                cliargs=cliargs,
                parsefn=parsefn,
                is_ovewriting=overwrite,
                missing_argument_message=missing_argument_message,
                fn=val if is_dependency else None,
            )
            if overwrite:
                self._state_overwrites_list.append((varname, val, node))
            else:
                local_state[varname] = val

                if varname not in self.state_registrations:
                    self.state_registrations[varname] = []
                self.state_registrations[varname].append(node)

    def _settings_parser_add(
        self,
        varname,
        val,
        caller_traceback,
        nargs=None,
        default=None,
        is_optional=False,
    ):  # noqa: C901 too-complex

        # lists are just multiple arguments
        if isinstance(val, (list, tuple)):
            if len(val) == 0:
                if isinstance(val, list):
                    val_type, start_del, end_del = "list", "[", "]"
                else:
                    val_type, start_del, end_del = "tuple", "(", ",)"
                raise RegisterError(
                    f'Variable \'%s\' is registered as {val_type} of length 0 (see exception below), however it is required to define the type of the {val_type} arguments for it to become accessible from cli.\n\nYour options are:\n\t- define a default {val_type}, e.g. {start_del}"a", "b", "c"{end_del}\n\t- define the {val_type} type, e.g. {start_del}str{end_del}\n\t- define the variable as a helper using register_helpers(...)'
                    % (fg("red") + varname + attr("reset")),
                    traceback=caller_traceback,
                )
            return self._settings_parser_add(
                varname,
                val[0],
                caller_traceback,
                nargs="*" if isinstance(val, list) else len(val),
                default=val,
                is_optional=is_optional,
            )

        # get argument type from value (this can be int, but also 42 for instance)
        if isinstance(val, Enum):
            argtype = Enum
        elif isinstance(val, EnumMeta):
            argtype = Enum
        elif isinstance(val, (type, EnumMeta)):
            argtype = val if val != bool else str2bool
        else:
            argtype = type(val) if not isinstance(val, bool) else str2bool
        kwarg = {"dest": varname, "type": argtype, "nargs": nargs}

        # we know the default argument, if the value is given
        # otherwise the value is a required argument (to be tested later)
        if is_optional:
            kwarg["default"] = None if nargs is None else []
        elif not isinstance(val, type) and not isinstance(val, EnumMeta) and not isinstance(val, Unit):
            kwarg["default"] = default if default is not None else val
        else:
            self.cli_required_arguments.append([varname])

        # for bool: enable --varname as alternative for --varname true
        if argtype == Enum:
            kwarg["action"] = EnumAction
            kwarg["type"] = val if isinstance(val, EnumMeta) else type(val)
        elif (
            argtype == str2bool and nargs != "*"
        ):  # pylint: disable=comparison-with-callable
            kwarg["nargs"] = "?"
            kwarg["const"] = True

        # define the actual arguments
        if argtype == UnitValue or argtype == Unit:
            kwarg["type"] = make_unitvalue_argparse(val)
        if argtype in [int, str, float, str2bool, Enum, UnitValue, Unit]:
            self.settings_parser.add_argument("--" + varname, **kwarg)
        else:
            raise ValueError(
                "Type '%s' not supported. (Used for setting '%s')"
                % (type(val), varname)
            )

        # for bool: enable --no-varname as alternative for --varname false
        # Note: this has to be defined AFTER --varname
        if (
            argtype == str2bool and nargs != "*"
        ):  # pylint: disable=comparison-with-callable
            self.settings_parser.add_argument(
                "--no-" + varname, dest=varname, action="store_false"
            )

        # remember the varname also for fuzzy searching
        self._varid_list.append(varname)

        return kwarg

    def register_unit(self, unit_id, get_converter, set_converter, units):
        r"""
        Custom numbers with multiple representations.

        Args:
        - `unit_id`: Unique id to distinguish different units.
        - `converter`: A method with the signature `(src_value: Number, src_unit: str, dest_unit: str)`
        - `units`: A list of lists. Each list specifies synonymes for units.

        Examples:

        **First, we define `time` to be a unit with four different representations with getter/setter functions to convert between these.**:  
        (Note that you can save arbitrary data to `unitvalue.data` and define yourself how units behave).
        ```python


        # define how to transform data when initializing a unit
        def init_time_unit(data):
            units = list(data.keys())
            assert len(units) == 1, f"Unitvalue should contain exactly one data point, but found {units}."
            unit = units[0]
            value = list(data.values())[0]
            data = {"computation_list": []}
            if unit == "m":
                return {"s": 60 * value, **data}
            elif unit == "h":
                return {"s": 60 * 60 * value, **data}
            elif unit == "d":
                return {"s": 24 * 60 * 60 * value, **data}
            raise ValueError(f"Could not determine initial values from {repr(data)}.")


        def get_time_unit(unitvalue, targetunit):

            # we use seconds as base unit und convert any start to that value
            if "s" not in unitvalue.data:
                unitvalue.data = init_time_unit(unitvalue.data)

            unitvalue.data["computation_list"].append(targetunit)

            if targetunit == "s":
                return unitvalue.data["s"]
            if targetunit == "m":
                return unitvalue.data["s"] / 60
            elif targetunit == "h":
                return unitvalue.data["s"] / 60 / 60
            elif targetunit == "d":
                return unitvalue.data["s"] / 60 / 60 / 24

            raise ValueError(f"Could not query {targetunit} from {repr(unitvalue)}")


        def set_time_unit(unitvalue, targetunit, newvalue):

            # we use seconds as base unit und convert any start to that value
            if "s" not in unitvalue.data:
                unitvalue.data = init_time_unit(unitvalue.data)

            unitvalue.data["computation_list"].append(targetunit)

            if targetunit == "s":
                unitvalue.data["s"] += newvalue
                return
            elif targetunit == "m":
                unitvalue.data["s"] += 60 * newvalue
                return
            elif targetunit == "h":
                unitvalue.data["s"] += 60 * 60 * newvalue
                return
            elif targetunit == "d":
                unitvalue.data["s"] += 24 * 60 * 60 * newvalue
                return

            raise ValueError(f"Could not query {targetunit} from {repr(unitvalue)}")

        time = mf.register_unit("time", get_time_unit, set_time_unit, [
            ["m", "minute", "minutes"],
            ["h", "hour", "hours"],
            ["s", "second", "seconds"],
            ["d", "day", "days"]
        ])
        ```

        **In CLI, we can overwrite this unit using**:
        - `--time 1.5d` (1.5 days)
        - `--time 24h` (24 hour)
        - `--time 500m` (500 minutes)

        **Using `u in v` Notation, we can specify the base unit to convert all calculations to.**:
        - `--time 12h in d` (0.5 days)
        - `--time 1.5d in h` (18 hours)

        **To register a unit, pass it to `register_defaults` as follows**:
        ```python
        mf.register_defaults({
            "time": time(6.0, "h"),
            "time2": time(6.0, "h in d"), # in notation works here as well
        })
        ```

        **Querying other representations can be done easily, once defined:**
        ```python
        state["time"].unit # the base unit name
        state["time"].second
        state["time"].minute
        state["time"].hour
        state["time"].day
        ```
        """  # noqa: W291
        if unit_id in self.units:
            raise ValueError(f"Unit with name {unit_id} is already defined.")

        u = Unit(unit_id, get_converter, set_converter, units)
        self.units[unit_id] = u
        return u

    # ======= #
    # runtime #
    # ======= #

    def stop_parse(self):
        r"""
        Stops loading of any new modules immediately and halts any further executions.
        """  # noqa: W291
        self.halt_parse = True

    def parse_args(
        self,  # noqa: C901 too-complex  pylint: disable=too-many-statements
        argv: List[str] or str = None,
        optional: bool = True,
        fuzzy_args: bool = True,
    ):
        r"""
        Parse CLI-Arguments.

        # Note {.alert}
        Typically you would call the run()-method instead. You will need this method only, if [run](./10-run.md) does not fit your needs.

        Args:
        - `argv`: (can also be `str`)
            Arguments to parse. If is `None` will use CLI arguments (`sys.argv[1:]`).
        - `optional`:
            If set to `False` disables the requirement to any modules to load. This option is interesting if your launch script is intended to use a predefined set of modules only.
        - `fuzzy_args`:
            If set to `False` disables fuzzy variable name search for the module arguments.
        """  # noqa: W291
        if self.argparse_called:
            raise SystemError(
                "The function `parse_args` has been called already. Did you maybe called `mf.parse_args()` and `mf.run()` in the same script? Solutions are:\n\t- Please use only one of those functions.\n\t- If you actually need both functions, please do not hesitate to write an issue on\n\t\thttps://github/da-h/miniflask/issues\n\t  to explain yout used case.\n\t  (It's not hard to implement, but I need to know, if and when this functionality is needed. ;) )"
            )

        has_module_args = argv is None or argv == sys.argv
        if argv is None:  # check if 'argv' is passed
            argv = sys.argv[1:]
        elif isinstance(argv, list):  # check if passed 'argv' is a list
            pass
        elif isinstance(
            argv, str
        ):  # check if passed 'argv' is a str (split by whitespace)
            argv = argv.split(" ")
        else:  # unknown passed variable (don't pass on any arguments)
            argv = []

        # actually parse the input
        if has_module_args:
            parser = ArgumentParser()
            parser.add_argument("cmds", type=str, nargs=1 if not optional else "?")
            parser.add_argument("module_arguments", nargs=ARGPARSE_REMAINDER)
            args = parser.parse_args(argv)

            # save remainder for module setting parser
            argv = args.module_arguments

            # load modules
            if args.cmds:
                if optional:
                    cmds = args.cmds.split(",")
                else:
                    cmds = args.cmds[0].split(",")
                for cmd in cmds:
                    if self.halt_parse:
                        break

                    # try:
                    self.load(cmd)
                    # except Exception as e:
                    #     print(e)

        # ensure default_modules are loaded
        keys = self.modules_loaded.keys()
        if len(self.default_modules) > 1:
            self.print_heading("Loading Automatically Requested Default Modules")

        # the default_module list gives us the order (last-in, first-out) of the default-modules to call
        # we assume that newer default modules are meant to overwrite older ones
        while len(self.default_modules) > 0:
            (
                module,
                evt,
                glob,
                overwrite_globals,
                caller_traceback,
            ) = self.default_modules.pop()
            del overwrite_globals, caller_traceback

            if evt:
                if not isinstance(module, list):
                    module = [module]
                modules_already_loaded = all(
                    self.getModuleId(m) in self.modules_loaded for m in module
                )
                if not modules_already_loaded and evt not in self.event_objs:
                    self.load(
                        module, loading_text=partial(highlight_loading_default, evt)
                    )
                else:
                    found = self.event_objs[evt].modules
                    if not isinstance(found, list):
                        found = [found]
                    found = [f.module_id for f in found]
                    print(highlight_loaded_default(found, evt))

            elif glob:
                found = [
                    highlight_loading_module(x) for x in keys if re.search(glob, x)
                ]
                if len(found) == 0:
                    self.load(
                        module, loading_text=partial(highlight_loading_default, glob)
                    )
                elif len(found) > 1:
                    print(highlight_loaded_default(found, glob))
                else:
                    print(highlight_loaded_default(found, glob))

        # in case a default module / overwrite_global-combination is used in two places in the loading-tree,
        # we assume that we want to overwrite the older values with the newer values
        for (
            module,
            _,
            _,
            overwrite_globals,
            caller_traceback,
        ) in self.default_modules_overwrites:
            if not isinstance(module, list):
                module = [module]
            if all(self.getModuleId(m) in self.modules_loaded for m in module):
                self.register_defaults(
                    overwrite_globals,
                    scope="",
                    overwrite=True,
                    caller_traceback=caller_traceback,
                )

        # check fuzzy matching of overwrites
        for varname, val, node in self._state_overwrites_list:
            if varname not in self.state_registrations:
                found_varids = get_varid_from_fuzzy(
                    varname, self.state_registrations.keys()
                )
                if len(found_varids) == 0:
                    raise RegisterError(
                        "Variable '%s' is not registered yet, however it seems like you wold like to overwrite it (see exception below)."
                        % (fg("red") + varname + attr("reset")),
                        traceback=node.caller_traceback,
                    )
                if len(found_varids) > 1:
                    raise RegisterError(
                        "Variable-Identifier '%s' is not unique. Found %i variables:\n\t%s\n\n    Call:\n        %s"
                        % (
                            highlight_module(found_varids),
                            len(found_varids),
                            "\n\t".join(found_varids),
                            " ".join(found_varids),
                        ),
                        traceback=node.caller_traceback,
                    )

                varname = found_varids[0]

                # this is important: the deferred node could not not know to this point what variable it manages
                node.varid = varname

            # apply the deferred initialization
            self.state[varname] = val
            self.state_registrations[varname].append(node)

        # first we build the reversed graph of dependency, i.e. the graph of what nodes are affected by each node
        last_state_registrations = {
            varid: nodes[-1] for varid, nodes in self.state_registrations.items()
        }

        # sort nodes topologically, check for circular_dependencies & dependency errors for variables
        (
            topolically_sorted_state_nodes,
            circular_dependencies,
            unresolved_dependencies,
        ) = state_node.topological_sort(last_state_registrations)
        registration_errors = []
        if len(circular_dependencies) > 0:
            registration_errors.append(
                'Circular dependencies found! (A → B means "A depends on B")\n\n'
                + "\n".join(
                    [
                        "\n    → ".join(highlight_loading_module(str(c)) for c in cycle)
                        for cycle in circular_dependencies
                    ]
                )
            )
        if len(unresolved_dependencies) > 0:
            registration_errors.append(
                'Dependency not found! (A → B means "A depends on B")\n\n'
                + "\n".join(
                    [
                        "\n    → ".join(highlight_loading_module(str(c)) for c in cycle)
                        + highlight_error(" ← not found")
                        for cycle in unresolved_dependencies
                    ]
                )
            )

        if len(registration_errors) > 0:
            registration_errors_str = "\n\n\n".join(
                [highlight_error() + r for r in registration_errors]
            )
            raise RegisterError(
                f"The registration of state variables has led to the following errors:\n\n{registration_errors_str}"
            )

        # evaluate the dependency-graph into state
        state_node.evaluate(topolically_sorted_state_nodes, self.state)

        # register user-changeable variables
        for varid, node in last_state_registrations.items():
            if node.cliargs:
                node.pre_cli_value = self.state[varid]
                val = (
                    self.state[varid]
                    if not isinstance(self.state[varid], optional_default)
                    else self.state[varid].type
                )
                argparse_kwargs = self._settings_parser_add(
                    varid,
                    val,
                    node.caller_traceback,
                    is_optional=isinstance(self.state[varid], optional_default),
                )
                if "default" in argparse_kwargs:
                    self.state[varid] = argparse_kwargs["default"]

        # add help message
        print_help = False
        if "-h" in argv:
            argv.remove("-h")
            print_help = True
        if "--help" in argv:
            argv.remove("--help")
            print_help = True

        # split `--varname=value` expressions to `--varname value`
        # (argparse does only allow the `key=value`-syntax for single-dash definitions)
        argv = [
            v
            for val in argv
            for v in (val.split("=", 1) if val.startswith("--") else [val])
        ]  # pylint: disable=superfluous-parens

        # parse nested expressions
        argv_flat = []
        namespaces = [""]
        len_argv = len(argv)
        for i, arg in enumerate(argv):

            # here the actual nesting takes place, remember any new level by adding to the namespace list
            if arg == "[":
                namespaces.append("")
                continue
            if arg == "]":
                namespaces.pop()
                if len(namespaces) == 0:
                    raise ValueError(
                        "Nesting-Error during parse of CLI-Arguments. Did you forget to include an '[' ?"
                    )
                continue

            # all non-arguments are values and thus should be retained
            if not arg.startswith("--"):
                argv_flat.append(arg)
                continue

            # remember argument as possible namespace in case of following nested arguments
            namespaces[-1] = arg[2:]

            # skip argument if is just a namespace
            if i + 1 < len_argv and argv[i + 1] == "[":
                continue

            # actual name is name with namespace
            if arg.startswith("--no-"):
                namespaces[-1] = namespaces[-1][3:]
                arg = "--no-" + ".".join(namespaces)
            else:
                arg = "--" + ".".join(namespaces)
            argv_flat.append(arg)
        argv = argv_flat

        # remember varids from user-args & fuzzy matching the settings
        user_varids = {}
        for i, varid in enumerate(argv):

            # no need to process actual values
            if not varid.startswith("--"):

                # special case: negative scientific notation currently does not work for argparse
                if (
                    varid.startswith("-")
                    and "e" in varid
                    and varid[1:].replace("e", "").isnumeric()
                ):
                    try:
                        argv[i] = str(float(varid))
                    except ValueError:
                        pass
                continue

            # extract varid from argument
            varid = varid[2:]
            was_false_bool = False
            if varid.startswith("no-"):
                varid = varid[3:]
                was_false_bool = True

            # check for global direct match first
            if varid in self._varid_list:
                # remember this varid has been overwritten by the user
                user_varids[varid] = True
                continue

            if fuzzy_args:

                # fuzzy match with all variable ids
                found_varids = get_varid_from_fuzzy(varid, self._varid_list)

                # if no matching varid found, check for fuzzy identifier
                if len(found_varids) > 1:
                    argv[i] = highlight_module(argv[i])
                    raise ValueError(
                        highlight_error()
                        + "Variable-Identifier '--%s' is not unique. Found %i variables:\n\t%s\n\n    Call:\n        %s"
                        % (
                            highlight_module(varid),
                            len(found_varids),
                            "\n\t".join(found_varids),
                            " ".join(argv),
                        )
                    )

                # no module found with both variants
                if len(found_varids) == 0:
                    argv[i] = highlight_module(argv[i])
                    raise ValueError(
                        highlight_error()
                        + "Variable '--%s' not known.\n\n    Call:\n       %s"
                        % (highlight_module(varid), " ".join(argv))
                    )

                varid = found_varids[0]

                # replace with fuzzy-found varid
                argv[i] = ("--no-" if was_false_bool else "--") + found_varids[0]

            # remember this varid has been overwritten by the user
            user_varids[varid] = True

        # parse user overwrites (first time, s.t. lambdas change adaptively)
        settings_args = vars(self.settings_parser.parse_args(argv))
        for varid in user_varids:
            val = settings_args[varid]
            self.state[varid] = val
            self.state_registrations[varid][-1].cli_overwritten = True

        # check if required arguments are given by now
        missing_arguments = []
        for variables in self.cli_required_arguments:
            if not self.state_registrations[variables[0]][-1].cli_overwritten:
                missing_arguments.append(variables)
        if len(missing_arguments) > 0:
            args_err_strs = []
            error_message_str = ""
            for args in missing_arguments:
                arg_err_str = "\t" + " or ".join(
                    [highlight_module("--" + arg) for arg in reversed(args)]
                )
                if args[0] in self.state_registrations:
                    for node in self.state_registrations[args[0]]:
                        summary = next(
                            filter(
                                lambda t: not t.filename.endswith(
                                    "miniflask/miniflask.py"
                                ),
                                reversed(node.caller_traceback),
                            )
                        )
                        adj = (
                            fg("blue") + "Defined"
                            if not node.is_ovewriting
                            else fg("yellow") + "Overwritten"
                        ) + attr("reset")
                        arg_err_str += (
                            linesep
                            + "\t  "
                            + adj
                            + " in line %s in file '%s'."
                            % (
                                highlight_event(str(summary.lineno)),
                                attr("dim")
                                + path.relpath(summary.filename)
                                + attr("reset"),
                            )
                        )
                        if isinstance(node.missing_argument_message, str):
                            error_message_str = (
                                linesep * 2
                                + attr("bold")
                                + node.missing_argument_message
                                + attr("reset")
                            )
                args_err_strs.append(arg_err_str)
            raise ValueError(
                "Missing CLI-arguments or unspecified variables during miniflask call."
                + linesep
                + linesep.join(args_err_strs)
                + error_message_str
            )

        # re-evaluate the dependency-graph with the user-cli arguments
        state_node.evaluate(topolically_sorted_state_nodes, self.state)

        # print help message when everything is parsed
        self.settings_parser.print_help = lambda: (
            print("usage: modulelist [optional arguments]"),
            print(),
            print("optional arguments (and their defaults):"),
            print(
                listsettings(
                    state("", self.state, self.state_registrations), self.event
                )
            ),
        )
        if print_help:
            self.settings_parser.parse_args(["--help"])

        # mark this instance as run
        self.argparse_called = True

    def run(
        self,
        modules: List[str] or str = None,
        call: str = "main",
        argv: List[str] or str = None,
    ):  # noqa: C901 too-complex  pylint: disable=too-many-statements
        r"""
        Entrypoint of most miniflask programs.

        Procedure of this Method:
        1. Loading of predefined modules.
        2. Parsing CLI-args. This includes:
            - first loading of modules called in CLI
            - setting default values to those defined in CLI
        3. If any module called `stop_parse`, the program halts.
        4. Execution of `init` event (if it exists)
        5. Execution of `main` event (if it exists)
        6. Execution of `final` event (if it exists)

        This method also pretty prints
        - the distinct phases described above
        - uncatched exceptions that occur during any event.
            (This method strips any miniflask-related exceptinos from the traceback. In case a debugger is used or the `debug` flag is set for the miniflask instance, the full exception traceback is shown.)

        Args:
        - `modules`:
            List or String of modules
        - `call`:
            The name of the default “main” event.
        - `argv`:
            Arguments to parse. If is `None` will use CLI arguments (`sys.argv[1:]`).
        """  # noqa: W291
        if modules is None or (isinstance(modules, list) and len(modules) == 0):
            modules = ["settings"]
        try:

            self.print_heading("Loading Modules")

            # load required modules
            self.load(modules)

            # parse command line arguments & overwrite default parameters
            self.parse_args(argv=argv)

            # check if all requested modules are loaded
            if not self.halt_parse:

                # optional init event
                if hasattr(self.event, "init"):
                    self.print_heading("init Event")
                    self.event.optional.init()

                # call event if exists
                if hasattr(self.event, call):

                    # call the event
                    # (this is only for nicer exception output)
                    self.print_heading("%s Event" % call)
                    if call == "main":
                        self.event.main()
                    else:
                        getattr(self.event, call)()
                else:
                    print(
                        "No event '{0}' registered. "
                        "Please make sure to register the event '{0}', "
                        'or provide a suitable event to call with mf.run(call="myevent").'.format(
                            call
                        )
                    )

                # optional final event
                if hasattr(self.event, "final"):
                    self.print_heading("final Event")
                    self.event.optional.final()

        except (RegisterError, StateKeyError) as e:
            gettrace = getattr(sys, "gettrace", None)

            # check if debugger will catch this
            if not self.debug and (not gettrace or not gettrace()):
                tb = traceback.extract_tb(e.__traceback__)
                print()
                print(
                    fg("red")
                    + "Uncatched Exception occured. Traceback:"
                    + attr("reset")
                )
                print(format_traceback_list(tb, exc=e, ignore_miniflask=False))
                sys.exit(1)
            else:
                raise
        except Exception as e:  # pylint: disable=broad-except
            gettrace = getattr(sys, "gettrace", None)

            # check if debugger will catch this
            if not self.debug and (not gettrace or not gettrace()):
                tb = traceback.extract_tb(e.__traceback__)
                print()
                print(
                    fg("red")
                    + "Uncatched Exception occured. Traceback:"
                    + attr("reset")
                )

                # nicer version of: print(traceback.format_exc())
                print(format_traceback_list(tb, exc=e, ignore_miniflask=not self.debug))
                sys.exit(1)
            else:
                raise


class miniflask_wrapper(miniflask):
    def __init__(self, module_name, mf):  # pylint: disable=super-init-not-called
        """!...is a local miniflask instance

        The local miniflask instance is the specialized object that is passed to any `register(mf)` call directly to a module.
        The global [miniflask object](../02-miniflask-instance/) and the local `mf` object are quite similar with the exception that the local `mf` object allows to change only the behaviour of the currently registered module.

        The object has the following public variables:
        - `module_id`: The internal unique id used for this module.
        - `module_name`: The actual name of the module (the part after the last dot).
        - `state`: The local state object.

        Also as a `miniflask` object itself it inherits all methods described in [miniflask object](../02-miniflask-instance/) with the exceptions listed in this chapter.

        """  # noqa: W291
        self.module_id = module_name
        self.module_id_initial = module_name
        self.module_name = module_name.split(".")[-1]
        self.wrapped_class = mf.wrapped_class if hasattr(mf, "wrapped_class") else mf
        self.state = state(
            module_name,
            self.wrapped_class.state,
            self.wrapped_class.state_registrations,
        )
        self._recently_loaded = []
        self._defined_events = {}

    def _get_relative_module_id(self, possibly_relative_path, offset=1):
        module_name, was_relative = get_relative_id(
            possibly_relative_path, self.module_id, offset=offset
        )
        return module_name, was_relative

    def __getattr__(self, name):
        orig_attr = super().__getattribute__("wrapped_class").__getattribute__(name)
        if callable(orig_attr):

            def hooked(*args, **kwargs):
                result = orig_attr(*args, **kwargs)
                # prevent wrapped_class from becoming unwrapped
                if result == self.wrapped_class:
                    return self
                return result

            return hooked
        return orig_attr

    def redefine_scope(self, new_module_name):
        r"""
        Renames the module internally.

        This method may come in handy if one module shall takes the place of another module if loaded.
        **Note that this replacement is now dependend on the order of the module loading.**

        Args:
        - `new_module_name`: The module id to use internally.
        """  # noqa: W291
        old_module_name = self.module_id
        new_module_name = self.set_scope(new_module_name)
        if new_module_name in self.modules_avail:
            raise ValueError(
                "Scope `%s` already used. Cannot define multiple modules using `redefine_scope`. Did you maybe mean to use `set_scope`?"
                % new_module_name
            )
        m = self.modules_avail[old_module_name]
        del self.modules_avail[old_module_name]
        m["id"] = new_module_name
        self.modules_avail[new_module_name] = m

    def set_scope(self, new_module_name):
        r"""
        Rename the state prefix / Share the state with another module.

        Args:
        - `new_module_name`: The prefix to use with any `state["var"]` call.
        """  # noqa: W291
        new_module_name, _ = self._get_relative_module_id(new_module_name)
        self.module_id = new_module_name
        self.state.module_id = new_module_name
        return new_module_name

    # wrapper for the optional class
    def optional(self, variable_type):
        r"""
        Define optional variables.

        # Note {.alert}
        - Optional variables are `None` if unspecified by the user.
        - Exception are optional list types. These return `[]` if unspecified by the user.

        Args:
        - `variable_type`: The type to ask the user for in cli.

        Examples:
        ```python
        mf.register_defaults({
            "myvar": mf.optional(int)
            "myvarlist": mf.optional([int])
        })
        ```
        """  # noqa: W291
        return optional_default(variable_type)

    def as_is_callable(self, variable):
        r"""
        Wrap variables for register_-calls to ensure they are not parsed during initialization.

        # Note {.alert}
        This function is typically useful in case a module saves a callable object upon initialization inside a helper variable.

        Args:
        - `varname`: The variable to use.

        Examples:

        **Background / When to use this feature?**
        Consider the following variable definitions of `var1` and `var2`, whene `MyClass` is callable, i.e. we can run `state["var1"](*args, **kwargs)`.
        ```python
        mf.register_helpers({
            "var1": MyClass(),
            "var2": mf.as_is_callable(MyClass()),
        })
        ```
        The definition of `var1` may cause problems because miniflask allows to specify functions as variables. This allows dependencies between variables that are ”solved“ during the initialization of the program. To do this, miniflask needs to evaluate the callable variables (also recursively due to possible multi-level dependencies) until their result is not a callable function anymore. Unfortunately, we cannot decide programatically when a callable is intended to be evaluated during initialization to solve variable dependencies, or, as in this case, it is just a class-instance that we want to use in a modules events.
        Same applies to functions: if we want to save a function, we need to specify that it has nothing to do with variable dependencies, i.e. we need to define it using `mf.as_is_callable`.
        """  # noqa: W291
        return as_is_callable(variable)

    # loads module dependencies as child module
    def load_as_child(self, module_name, bind_events=False, **kwargs):
        r"""
        Load another module as a child module.

        Args:
        - `bind_events`: (Default:`False`) Binding events of the module to attach as child-module.

        # Note {alert=warning}
        These kinds of child modules are a preliminary feature of miniflask. Thus, at the moment the function is rather limited:
        No events will be registered to be accessible globally by default. However, it is possible to access the state variables of that module.
        """  # noqa: W291
        self.load(module_name, as_id=".", bind_events=bind_events, **kwargs)

    # enables relative imports
    def load(self, module_name, as_id=None, auto_query=True, **kwargs):
        r"""
        Directly load a module by name. (Allows relative loading.)

        This method behaves just as [`miniflask.load`](../02-miniflask-Instance/05-load.md) with the exception that it also detectc local module names.

        Considering calling `mf.load` during registration (inside the `register(mf)` method) of the module with the unique module id `a.b.c.d`.
        Loading the module:
        - `.child` references `a.b.c.d.child`
        - `..` references the parent `a.b.c`
        - `..sibling` references `a.b.c.sibling`
        - `...` references `a.b`
        - `.` is a noop.

        Examples:
        ```python
        mf.load(".childmodule")
        mf.load("..siblingmodule")
        mf.load("...siblingofparent")
        ```
        """  # noqa: W291

        # if nothing given, ignore
        if module_name is None:
            return

        # if list given, iterate over list
        if isinstance(module_name, str) and "," in module_name:
            module_name = module_name.split(",")
        if isinstance(module_name, list):
            for mname in module_name:
                self.load(mname, as_id=as_id, auto_query=auto_query, **kwargs)
            return

        # if as_id given, determine new module_name
        if as_id:
            if as_id.endswith("."):
                as_id += module_name.split(".")[-1]
            as_id, _ = self._get_relative_module_id(as_id)

        # parse relative imports first
        module_name, was_relative = self._get_relative_module_id(module_name)
        auto_query = not was_relative

        # call load (but ensure no querying is made if relative imports were given)
        if "verbose" in kwargs:
            del kwargs["verbose"]
        super().load(
            module_name, verbose=False, auto_query=auto_query, as_id=as_id, **kwargs
        )

    # checks if child modules are already loaded
    def any_child_loaded(self):
        r"""
        Checks if any child modules of this module are loaded.

        This method is useful if the intented behavior of loading this module shall load another specialized version by default (that is if it is not specialized by the user).


        Examples:
        ```python
        if mf.any_child_loaded():
            mf.load(".childmoduleA")
        ```
        """  # noqa: W291
        return any(
            x for x in self.modules_loaded if re.search(self.module_id + r"\..*", x)
        )

    # register default module that is loaded if none of glob is matched
    # (enables relative imports)
    def register_default_module(self, module, **kwargs):
        r"""
        Specify modules to load if specific behaviour is not yet matched by already loaded modules. (Allows relative module ids).

        Same as  [`miniflask.register_default_module`](../02-miniflask-Instance/11-register_default_module.md) but allows also relative module ids.
        """  # noqa: W291

        # parse relative imports first
        if isinstance(module, list):
            module = [self._get_relative_module_id(m)[0] for m in module]
        else:
            module = self._get_relative_module_id(module)[0]

        super().register_default_module(module, **kwargs)

    def unregister_event(
        self, name: str, only_cache: bool = False, keep_attached_events: bool = True
    ):
        r"""
        Clears an event by name.

        Args:
        - `name`: The event to clear from the event object.
        - `only_cache`:
            - Setting to `True` means that the event cache will be cleared. Upon the next call of `event.name` the cache will be rebuild.
            - Setting to `False` means that the event cache will be cleared *and* the internal event objects will be removed as well. Upon the next call of `event.name` miniflask will not recognize the event anymore.
        - `keep_attached_events`:  By default (`True`), all events that are called together with this event (`before_`/`after_`-events) are kept. Setting to `False` clears those as well.
        """  # noqa: W291
        if hasattr(self.event, name):
            delattr(self.event, name)
            del self.event._data[name]
        if not only_cache and name in self.event_objs:
            del self.event_objs[name]
        if not keep_attached_events and "before_" + name in self.event_objs:
            self.unregister_event("before_" + name, only_cache)
        if not keep_attached_events and "after_" + name in self.event_objs:
            self.unregister_event("after_" + name, only_cache)

    # define event
    def register_event(self, name: str, fn, **kwargs):
        r"""
        Registers a function as an event & clears event-method cache.

        - The API is the same as [`miniflask.register_event`](../02-miniflask-Instance/09-register_event.md)
        - If the event exists already the event will be attached to the event list.
        - If the already existent event is defined as a unique event, miniflask will raise an error. You probably wanted to use [`overwrite_event`](./07-overwrite_event.md).
        """  # noqa: W291
        self.unregister_event(name, only_cache=True)
        self._defined_events[name] = fn
        super().register_event(name, fn, **kwargs)

    # overwrite event definition
    def overwrite_event(
        self, name: str, fn, keep_attached_events: bool = True, **kwargs
    ):
        r"""
        Unregister an existing event & redefine it using another function.

        **Note**:
        The main difference between this function and `register_event` is that this method clears the cache *and* removes the event internally, while `register_event` only clears the cache. (This is especially important if one uses non-unique events).

        Args:
        - `name`: The event to clear from the event object.
        - `only_cache`:
            - Setting to `True` means that the event cache will be cleared. Upon the next call of `event.name` the cache will be rebuild.
            - Setting to `False` means that the event cache will be cleared *and* the internal event objects will be removed as well. Upon the next call of `event.name` miniflask will not recognize the event anymore.
        - `keep_attached_events`:  By default (`True`), all events that are called together with this event (`before_`/`after_`-events) are kept. Setting to `False` clears those as well.
        """  # noqa: W291
        self.unregister_event(
            name, only_cache=False, keep_attached_events=keep_attached_events
        )
        self._defined_events[name] = fn
        super().register_event(name, fn, **kwargs)

    # overwrite state defaults
    def register_defaults(self, defaults, scope=None, **kwargs):
        r"""
        Registers module variables.

        Same as  [`miniflask.register_defaults`](../02-miniflask-Instance/08-register_defaults.md) but allows also relative scope & variable names.
        """  # noqa: W291
        # default behaviour is to use current module-name
        if scope is None:
            scope = self.module_id
        scope, _ = self._get_relative_module_id(scope, offset=1)
        super().register_defaults(defaults, scope=scope, **kwargs)

    # helper variables are not added to argument parser
    def register_helpers(self, defaults, **kwargs):
        r"""
        Registers helper variables (not changeable by CLI).

        Defaults to `cliargs=False` for [`mf.register_defaults`](./11-register_defaults.md)
        """  # noqa: W291
        self.register_defaults(defaults, cliargs=False, **kwargs)

    # does not add scope of module
    def register_globals(self, defaults, **kwargs):
        r"""
        Registers global variables.

        Defaults to `scope=""` for [`mf.register_defaults`](./11-register_defaults.md)
        """  # noqa: W291
        self.register_defaults(defaults, scope="", **kwargs)

    # overwrites previously registered variables
    def overwrite_globals(self, defaults, scope="", **kwargs):
        r"""
        Overwrites previously defined global variables.

        Defaults to `scope=""` and `overwrite=True` for [`mf.register_defaults`](./11-register_defaults.md)
        """  # noqa: W291
        self.register_defaults(defaults, scope=scope, overwrite=True, **kwargs)

    # overwrites previously registered variables
    def overwrite_defaults(self, defaults, scope=None, **kwargs):
        r"""
        Overwrites previously defined variables.

        Defaults to `overwrite=True` for [`mf.register_defaults`](./11-register_defaults.md)
        """  # noqa: W291
        self.register_defaults(defaults, scope=scope, overwrite=True, **kwargs)
