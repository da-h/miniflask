# package modules
from .event import event, event_obj
from .state import state, like
from .dummy import miniflask_dummy
from .util import getModulesAvail
from .util import highlight_error, highlight_name, highlight_module, highlight_loading, highlight_loading_default, highlight_loaded_none, highlight_loaded, highlight_event, highlight_blue_line, highlight_type, highlight_val, highlight_val_overwrite, str2bool


from .modules import registerPredefined
from .modules.settings import listsettings

# global modules
import sys
from os import path, listdir, linesep
from colored import fg, bg, attr
from importlib import import_module
from copy import copy
from argparse import ArgumentParser, SUPPRESS as argparse_SUPPRESS
from queue import Queue
import re

def print_info(*args,color=fg('green'),msg="INFO"):
    print(color+attr('bold')+msg+attr('reset')+color+": "+attr('reset'),*args,attr('reset'))

# ================ #
# MiniFlask Kernel #
# ================ #

class miniflask():
    def __init__(self, module_dirs):
        if not module_dirs:
            return

        # module dir to be read from
        if not isinstance(module_dirs,list):
            self.module_dirs = [module_dirs]
        else:
            self.module_dirs = module_dirs
        for dir in self.module_dirs:
            sys.path.insert(0,dir)

        # arguments from cli-stdin
        self.settings_parser = ArgumentParser(usage=sys.argv[0]+" modulelist [optional arguments]")
        self.settings_parse_later = {}
        self.settings_parse_later_overwrites = {}
        self.settings_parser_required_arguments = []
        self.default_modules = []

        # internal
        self.halt_parse = False
        self.event_objs = {}
        self.event_optional = event(self, optional=True, unique=False)
        self.event_optional_unique = event(self, optional=True, unique=True)
        self.event = event(self, optional=False, unique=False)
        self.event.optional = self.event_optional
        self.event.optional_unique = self.event_optional_unique
        self.state = {}
        self.state_default = {}
        self.modules_loaded = {}
        self.modules_avail = getModulesAvail(self.module_dirs)
        self.miniflask_objs = {} # local modified versions of miniflask
        registerPredefined(self.modules_avail)



    # ==================== #
    # module introspection #
    # ==================== #

    # module event
    def getModuleEvents(self, module, dummy=None):
        if not dummy:
            dummy = miniflask_dummy()

        # load module
        mod = import_module(self.modules_avail[module])
        if not hasattr(mod,"register"):
            return []

        mod.register(dummy)
        return dummy.getEvents()

    # pretty print of all available modules
    def showModules(self, dir=None, prepend="", id_pre="", with_event=True):
        if not dir:
            if len(self.module_dirs) == 1:
                dir = self.module_dirs[0]
            else:
                for dir in self.module_dirs:
                    self.showModules(dir, prepend=prepend, id_pre=id_pre, with_event=with_event)
                return

        if len(prepend) == 0:
            print()
            print(highlight_name(path.basename(dir)))
        dirs = [d for d in listdir(dir) if path.isdir(path.join(dir,d)) and not d.startswith("_")]
        for i, d in enumerate(dirs):
            if d.startswith("."):
                continue
            if path.exists(path.join(dir,d,".ignoredir")):
                continue

            is_module = path.exists(path.join(dir,d,".module"))
            is_module_without_shortid = path.exists(path.join(dir,d,".noshortid"))

            module_id = id_pre + "." + d if id_pre != "" else d
            if i == len(dirs)-1:
                tree_symb = "└── "
                is_last = True
            else:
                tree_symb = "├── "
                is_last = False
            append = " "+fg('blue')+"("+module_id+")"+attr('reset') if is_module_without_shortid else ""
            append += attr('dim')+" (short-id not unique)"+attr('reset') if is_module and not d in self.modules_avail else ""
            print(prepend+tree_symb+(highlight_name(d) if is_module else d)+append)

            tree_symb_next = "     " if is_last else "│    "
            if is_module:
                if with_event:
                    events = self.getModuleEvents(module_id)
                    if len(events) > 0:
                        for e in events:
                            unique_flag = "!" if e[1] else ">"
                            print(prepend+tree_symb_next+unique_flag+" "+highlight_event(e[0]))
                continue
            self.showModules(path.join(dir,d),prepend=prepend+tree_symb_next, id_pre=module_id, with_event=with_event)

    # pretty print loaded modules
    def __str__(self):
        if len(self.modules_loaded) == 0:
            return highlight_loaded_none("No Loaded Modules")
        return highlight_loaded("Loaded Modules:", self.modules_loaded.keys())


    # =================== #
    # module registration #
    # =================== #

    # get unique id of a moodule
    def getModuleId(self, module):
        if not module in self.modules_avail:
            raise ValueError(highlight_error()+"Module '%s' not known." % highlight_module(module))
        return self.modules_avail[module]

    # get short id of a moodule
    def getModuleShortId(self, module):
        if not module in self.modules_avail:
            raise ValueError(highlight_error()+"Module '%s' not known." % highlight_module(module))
        uniqueId = self.modules_avail[module]
        shortid = uniqueId.split(".")[-1]
        return shortid if shortid in self.modules_avail and self.modules_avail[shortid] == module else None

    # maps 'folder.subfolder.module.list.of.vars' to 'folder.subfoldder.module'
    def _getModuleIdFromVarId(self, varid_list, scope=None):
        if scope is not None and scope in self.modules_avail:
            return scope
        for i in range(len(varid_list)-1,0,-1):
            test_id = ".".join(varid_list[:i])
            if test_id in self.modules_avail:
                return test_id
        return None

    # loads module (once)
    def load(self, module_name, verbose=True, loading_text=highlight_loading):

        # load list of modules
        if isinstance(module_name,list):
            for m in module_name:
                self.load(m)
            return

        # get id
        module_name = self.getModuleId(module_name)

        # check if module_name exists or is already loaded
        if not module_name in self.modules_avail:
            raise ValueError(highlight_error()+"module_name '%s' not known." % module_name)
        if module_name in self.modules_loaded:
            return

        # load module
        prepend = self._loadprepend if hasattr(self,'_loadprepend') else ""
        print(prepend+loading_text(self.modules_avail[module_name]))
        mod = import_module(self.modules_avail[module_name])
        if not hasattr(mod,"register"):
            raise ValueError(highlight_error()+"Module '%s' does not register itself." % module_name)

        # remember loaded modules
        self.modules_loaded[self.modules_avail[module_name]] = mod

        # register events
        mod.miniflask_obj = miniflask_wrapper(module_name, self)
        mod.miniflask_obj._loadprepend = prepend + "  ├── "
        mod.register(mod.miniflask_obj)

    # register default module that is loaded if none of glob is matched
    def register_default_module(self, glob, module):
        self.default_modules.append((glob, module))

    # saves function to a given (event-)name
    def register_event(self,name,fn,unique=False):

        # check if is unique event. if yes, check if event already registered
        if name in self.event_objs and (unique or self.event_objs[name].unique):
            eobj = self.event_objs[name].modules if not self.event_objs[name].unique else [self.event_objs[name].modules]
            raise ValueError(highlight_error()+"Event '%s' is unique, and thus, cannot be imported twice.\n\t(Imported by %s)" % (highlight_event(name),", ".join(["'"+highlight_module(e.module_name)+"'" for e in eobj])))

        # register event
        if name in self.event_objs:
            self.event_objs[name].fn.append(fn)
            self.event_objs[name].modules.append(self)
        else:
            self.event_objs[name] = event_obj(fn, unique, self)

    # overwrite state defaults
    # Note: the problem lies in the fact that the true id of a variable is defined as scope.key,
    #       however scope can be empty if key is meant as a reference in the global scope=="".
    #       Otherwise, this function would be a lot simpler.
    def register_defaults(self, defaults, scope="", overwrite=False, cliargs=True, parsefn=True):
        if scope is None:
            scope = ""

        for key, val in defaults.items():

            # unique & full varname is fully defined using scope
            varname = scope+"."+key if len(scope) > 0 else key
            key_split = varname.split(".")

            # short name is only given iff corresponding module has a unique short id
            varname_short = None
            module_id = self._getModuleIdFromVarId(key_split,scope=scope)
            if module_id is not None and module_id in self.modules_avail:

                # retrieve real local key name
                key = varname[len(module_id)+1:]
                module_short_id = self.getModuleShortId(module_id)
                if module_short_id is not None:
                    varname_short = module_short_id+"."+key

            # ignore if short varname is varname
            if varname_short == varname:
                varname_short = None

            # pre-initialize variable for possible lambda expressions in second pass
            if hasattr(self.state,"all"):
                self.state.all[varname] = val
            else:
                self.state[varname] = val

            # actual initialization is done when all modules has been parsed
            if overwrite:
                self.settings_parse_later_overwrites[varname] = (varname_short, val, cliargs, parsefn)
            else:
                self.settings_parse_later[varname] = (varname_short, val, cliargs, parsefn)

    def _settings_parser_add(self, varname, varname_short, val, nargs=None, default=None):

        # lists are just multiple arguments
        if isinstance(val,list):
            self._settings_parser_add(varname, varname_short, val[0], nargs="+", default=val)
            return

        # get argument type from value (this an be int, but also 42 for instance)
        if type(val) == type:
            argtype = val if val != bool else str2bool
        else:
            argtype = type(val) if type(val) != bool else str2bool
        kwarg_long  = {'dest': varname, 'type': argtype, 'nargs': nargs}
        kwarg_short = {'dest': varname, 'type': argtype, 'nargs': nargs, 'help': argparse_SUPPRESS}

        # we know the default argument, if the value is given
        # otherwise the value is a required argument (to be tested later)
        if type(val) != type:
            kwarg_long["default"] = kwarg_short["default"] = default if default is not None else val
        else:
            if varname_short:
                self.settings_parser_required_arguments.append([varname,varname_short])
            else:
                self.settings_parser_required_arguments.append([varname])

        # for bool: enable --varname as alternative for --varname true
        if argtype == str2bool and nargs != '+':
            kwarg_long["nargs"]  = kwarg_short["nargs"] = '?'
            kwarg_long["const"]  = kwarg_short["const"] = True

        # define the actual arguments
        if argtype in [int,str,float,str2bool]:
            self.settings_parser.add_argument( "--"+varname, **kwarg_long)
            if varname_short:
                self.settings_parser.add_argument( "--"+varname_short, **kwarg_short)
        else:
            raise ValueError("Type '%s' not supported. (Used for setting '%s')" % (type(val), varname))

        # for bool: enable --no-varname as alternative for --varname false
        # Note: this has to be defined AFTER --varname
        if argtype == str2bool and nargs != '+':
            self.settings_parser.add_argument('--no-'+varname, dest=varname, action='store_false')
            if varname_short:
                self.settings_parser.add_argument('--no-'+varname_short, dest=varname, action='store_false', help=argparse_SUPPRESS)

    # ======= #
    # runtime #
    # ======= #
    def stop_parse(self):
        self.halt_parse = True

    def parse_args(self, argv=None, optional=True):
        self.halt_parse = False

        if not argv:
            argv = sys.argv#[1:]
        else:
            argv = [None]+argv

        parser = ArgumentParser()
        parser.add_argument('cmds', default='info', nargs=1 if not optional else "?")
        args = parser.parse_args(argv[1:2])

        # load modules
        if args.cmds:
            if optional:
                cmds = args.cmds.split(',')
            else:
                cmds = args.cmds[0].split(',')
            for cmd in cmds:
                if self.halt_parse:
                    break

                # try:
                self.load(cmd)
                # except Exception as e:
                #     print(e)

        # ensure default_modules are loaded
        keys = self.modules_loaded.keys()
        for glob, module in self.default_modules:
            found = [x for x in keys if re.search(glob, x)]
            if len(found) == 0:
                self.load(module, loading_text=lambda x: highlight_loading_default(glob,x))

        # add variables to argparse and remember defaults
        for settings in [self.settings_parse_later,self.settings_parse_later_overwrites]:
            overwrite = settings == self.settings_parse_later_overwrites 
            for varname, (varname_short, val, cliargs, parsefn) in settings.items():

                # check if exists
                if overwrite and varname not in self.settings_parse_later:
                    raise ValueError("Variable '%s' is not registered yet, however it seems like you wold like to overwrite it." % varname)

                if callable(val) and type(val) != type and parsefn:
                    the_val = val(self.state,self.event)
                else:
                    the_val = val

                if cliargs:

                    # add to argument parser
                    # Note: the the last value (an overwrite-variable) should be the one that generates the argparser)
                    if overwrite or varname not in self.settings_parse_later_overwrites:
                        self._settings_parser_add(varname, varname_short, the_val)

                    # remember default state
                    if isinstance(val,like):
                        val.default = the_val
                        self.state_default[varname] = val
                    else:
                        self.state_default[varname] = the_val

        # add help message
        self.settings_parser.print_help = lambda: (print("usage: modulelist [optional arguments]"),print(),print("optional arguments (and their defaults):"),print(listsettings(state("",self.state,self.state_default),self.event)))

        # parse user overwrites (first time, s.t. lambdas change adaptively)
        settings_args = self.settings_parser.parse_args(argv[2:])
        for varname, val in vars(settings_args).items():
            self.state[varname] = val

        # check if required arguments are given by now
        missing_arguments = []
        for variables  in self.settings_parser_required_arguments:
            if self.state[variables[0]] is None:
                missing_arguments.append(variables)
        if len(missing_arguments) > 0:
            self.settings_parser.error(linesep+linesep.join(["The following argument is required: "+" or ".join(["--"+arg for arg in reversed(args)]) for args in missing_arguments]))

        # finally parse lambda-dependencies
        for varname, (varname_short, val, cliargs, parsefn) in self.settings_parse_later.items():

            # Note: if current state equals state_default it has not been overwritten by user, thus lambda can be evaluated again
            while callable(val) and type(val) != type and parsefn and (not cliargs or self.state[varname] == self.state_default[varname]):
                val = val(self.state,self.event)
                self.state[varname] = val

        print(highlight_blue_line("-"*50))

    def run(self, call="main"):
        # check if all requested modules are loaded
        if not self.halt_parse:

            # optional init event
            self.event.optional.init()

            # call event if exists
            if hasattr(self.event, call):
                getattr(self.event, call)()
            else:
                print("No event '{0}' registered. "
                      "Please make sure to register the event '{0}', "
                      "or provide a suitable event to call.".format(call))


class miniflask_wrapper(miniflask):
    def __init__(self, module_name, mf):
        self.module_name = module_name
        self.wrapped_class = mf.wrapped_class if hasattr(mf, 'wrapped_class') else mf
        self.state = state(module_name, self.wrapped_class.state, self.wrapped_class.state_default)

    def redefine_scope(self,new_module_name):
        self.modules_avail[self.getModuleShortId(self.module_name)] = new_module_name
        del self.modules_avail[self.module_name]
        self.modules_avail[new_module_name] = new_module_name
        self.set_scope(new_module_name)

    def set_scope(self,new_module_name):
        self.module_name = new_module_name
        self.state.module_name = new_module_name

    def __getattr__(self,attr):
        orig_attr = super().__getattribute__('wrapped_class').__getattribute__(attr)
        if callable(orig_attr):
            def hooked(*args, **kwargs):
                result = orig_attr(*args, **kwargs)
                # prevent wrapped_class from becoming unwrapped
                if result == self.wrapped_class:
                    return self
                return result
            return hooked
        else:
            return orig_attr

    # overwrite state defaults
    def register_defaults(self, defaults, scope=None, **kwargs):
        # default behaviour is to use current module-name
        if scope is None:
            scope = self.module_name
        super().register_defaults(defaults, scope=scope, **kwargs)

    # helper variables are not added to argument parser
    def register_helpers(self, defaults, **kwargs):
        self.register_defaults(defaults, cliargs=False, **kwargs)

    # does not add scope of module
    def register_globals(self, defaults, **kwargs):
        self.register_defaults(defaults, scope="", **kwargs)

    # overwrites previously registered variables
    def overwrite_globals(self, defaults, scope="", **kwargs):
        self.register_defaults(defaults, scope=scope, overwrite=True, **kwargs)

    # overwrites previously registered variables
    def overwrite_defaults(self, defaults, scope=None, **kwargs):
        self.register_defaults(defaults, scope=scope, overwrite=True, **kwargs)

