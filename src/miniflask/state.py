import sys
import re

from colored import fg, attr

from .util import get_varid_from_fuzzy, highlight_module, get_relative_id
from .exceptions import StateKeyError


class temporary_state(dict):
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


class state(dict):
    def __init__(self, module_name, internal_state_dict, state_default):  # pylint: disable=super-init-not-called
        self.all = internal_state_dict
        self.default = state_default
        self.module_id = module_name
        self.fuzzy_names = {}
        # self.temporary = temporary_state(self)

    def scope(self, module_name, local=False):
        return state(self.module_id + "." + module_name if local else module_name, self.all, self.default)

    def temporary(self, variables):
        return temporary_state(self, variables)

    def __contains__(self, name):

        # check if key already known from this state-object
        if name in self.fuzzy_names:
            return True

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


def _create_excpetion_notfound(module_id, varid, name):
    varid_split = varid.split(".")
    tried_text = "\n\t".join(["- as module variable: '%s'" % (fg('green') + ".".join(varid_split[:-i]) + "." + varid_split[-1] + attr('reset')) for i in range(1, len(varid_split))])
    return StateKeyError("Variable '%s' not known.\n(Module %s attempted to access this variable.)\n\nI tried the following interpretations in that order:\n\t%s\n\t- as global Variable: '%s'\n\t- finally, I tried any ordered selection that contains the keys: [%s]." % (fg('green') + name + attr('reset'), highlight_module(module_id), tried_text, fg('green') + name + attr('reset'), ', '.join("'" + fg('green') + n + attr('reset') + "'" for n in name.split("."))))


def _create_excpetion_notunique(found_varids, name):
    return StateKeyError("Variable-Identifier '%s' is not unique. Found %i variables:\n\t%s\n\n    Call:\n        %s" % (highlight_module(name), len(found_varids), "\n\t".join(found_varids), name))


class like:
    def __init__(self, varname, alt, scope=None, scope_name=None):
        if scope_name is None:
            scope_name = scope
        global_varname = varname if scope is None else scope + "." + varname
        self.varname = scope_name + "." + varname if scope_name is not None else varname
        self.alt = alt
        self.fn = lambda state, event: state[global_varname] if global_varname in state else alt  # noqa: E731 no-lambda

    def __call__(self, state, event):  # pylint: disable=redefined-outer-name
        return self.fn(state, event)

    def str(self, asciicodes=True, color_attr=attr):
        if not asciicodes:
            color_attr = lambda x: ''  # noqa: E731 no-lambda
        return color_attr('dim') + "'" + str(self.varname) + "' or '" + str(self.alt) + "' ⟶   " + color_attr('reset') + str(self.default)

    def __str__(self):
        return self.str()
