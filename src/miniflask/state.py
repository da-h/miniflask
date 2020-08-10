import sys
from colored import fg, bg, attr
import re
from .util import get_varid_from_fuzzy, highlight_error, highlight_module
from .exceptions import StateKeyError

relative_import_re = re.compile("(\.+)(.*)")
class state(dict):
    def __init__(self, module_name, state, state_default):
        self.all = state
        self.default = state_default
        self.module_id = module_name
        self.fuzzy_names = {}

    def scope(self, module_name, local=False):
        return state(self.module_id+"."+module_name if local else module_name, self.state, self.state_default)

    def __contains__(self, name):
        # check if key already known from this state-object
        if name in self.fuzzy_names:
            return True

        # intern the string
        name = sys.intern(name)

        # check if is internal variable
        module_name = self.module_id+"."+name
        if module_name in self.all:
            self.fuzzy_names[name] = module_name
            return True

        # check if is global variable
        if name in self.all:
            self.fuzzy_names[name] = name
            return True

        # search for fuzzy global variable
        found_varids = get_varid_from_fuzzy(name, self.all.keys())

         # if no matching varid found, alert user
        if len(found_varids) > 1:
            raise StateKeyError("Variable-Identifier '%s' is not unique. Found %i variables:\n\t%s\n\n    Call:\n        %s" % (highlight_module(name), len(found_varids), "\n\t".join(found_varids), " ".join(name)))

        # no module found with both variants
        elif len(found_varids) == 0:
            return False

        # cache for next use
        self.fuzzy_names[found_varids[0]] = name
        return True

    def __getitem__(self, name):

        # check if key already known from this state-object
        if name in self.fuzzy_names:
            return self.all[self.fuzzy_names[name]]

        # intern the string
        name = sys.intern(name)

        # check if is internal variable
        module_name = self.module_id+"."+name
        if module_name in self.all:
            self.fuzzy_names[name] = module_name
            return self.all[module_name]

        # check if is global variable
        if name in self.all:
            self.fuzzy_names[name] = name
            return self.all[name]

        # search for fuzzy global variable
        found_varids = get_varid_from_fuzzy(name, self.all.keys())

         # if no matching varid found, alert user
        if len(found_varids) > 1:
            raise StateKeyError("Variable-Identifier '%s' is not unique. Found %i variables:\n\t%s\n\n    Call:\n        %s" % (highlight_module(name), len(found_varids), "\n\t".join(found_varids), " ".join(name)))

        # no module found with both variants
        elif len(found_varids) == 0:
            raise StateKeyError("Variable '%s' not known. (Module %s attempted to access this variable.)\n\nI tried the following interpretations:\n\t- as module variable: '%s'\n\t- as global Variable: '%s'\n\t- finally, I tried any ordered selection that contains the keys: [%s]." % (fg('green')+name+attr('reset'),highlight_module(self.module_id),fg('green')+module_name+attr('reset'),fg('green')+name+attr('reset'),', '.join("'"+fg('green')+n+attr('reset')+"'" for n in name.split("."))))

        # cache for next use
        self.fuzzy_names[found_varids[0]] = name
        return self.all[found_varids[0]]

    def __setitem__(self, name, val):

        # check if key already known from this state-object
        if name in self.fuzzy_names:
            self.all[self.fuzzy_names[name]] = val
            return

        # intern the string
        name = sys.intern(name)

        # check if is internal variable
        module_name = self.module_id+"."+name
        if module_name in self.all:
            self.fuzzy_names[name] = module_name
            self.all[module_name] = val
            return

        # check if is global variable
        if name in self.all:
            self.fuzzy_names[name] = name
            self.all[name] = val
            return

        # search for fuzzy global variable
        found_varids = get_varid_from_fuzzy(name, self.all.keys())

         # if no matching varid found, alert user
        if len(found_varids) > 1:
            raise StateKeyError("Variable-Identifier '%s' is not unique. Found %i variables:\n\t%s\n\n    Call:\n        %s" % (highlight_module(name), len(found_varids), "\n\t".join(found_varids), " ".join(name)))

        # no module found with both variants, assume a internal module variable is meant to create
        elif len(found_varids) == 0:
            found_varids = [module_name]

        # cache for next use
        self.fuzzy_names[found_varids[0]] = name
        self.all[found_varids[0]] = val

    def __getattribute__(self, name):
        return super().__getattribute__(name)

    def _get_relative_module_id(self, module_name, offset=0):
        was_relative = False
        m = relative_import_re.match(module_name)
        if m is not None:
            upmodule = len(m[1])
            relative_module = m[2]
            if upmodule == offset:
                module_name = self.module_id + ("." + relative_module if relative_module else "")
            else:
                module_name = ".".join(self.module_id.split(".")[:-upmodule+offset]) + ("." + relative_module if relative_module else "")
            was_relative = True
        return module_name, was_relative


class like:
    def __init__(self, varname, alt, scope=None, scope_name=None):
        if scope_name is None:
            scope_name = scope
        global_varname = varname if scope is None else scope + "." + varname
        self.varname = scope_name+"."+varname if scope_name is not None else varname
        self.alt = alt
        self.fn = lambda state,event: state[global_varname] if global_varname in state else alt

    def __call__(self, state, event):
        return self.fn(state,event)

    def str(self, asciicodes=True):
        if not asciicodes:
            attr = lambda x: ''
        return attr('dim')+"'"+str(self.varname)+"' or '"+str(self.alt)+"' ⟶   "+attr('reset')+str(self.default)
    def __str__(self):
        return self.str()

