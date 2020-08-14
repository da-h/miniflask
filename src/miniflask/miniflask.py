# package modules
from .exceptions import save_traceback, format_traceback_list, RegisterError, StateKeyError
from .event import event, event_obj
from .state import state, like
from .dummy import miniflask_dummy
from .util import getModulesAvail
from .util import highlight_error, highlight_name, highlight_module, highlight_loading, highlight_loading_default, highlight_loaded_default, highlight_loading_module, highlight_loaded_none, highlight_loaded, highlight_event, highlight_type, highlight_val, highlight_val_overwrite, str2bool, get_varid_from_fuzzy


from .modules import registerPredefined
from .modules.settings import listsettings

# global modules
import traceback
import sys
from os import path, listdir, linesep, get_terminal_size
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
    def __init__(self, module_dirs, debug=False):
        self.debug = debug
        if not module_dirs:
            return

        # module dir to be read from
        if isinstance(module_dirs,list):
            self.module_dirs = {path.basename(m):m for m in module_dirs}
        elif isinstance(module_dirs,str):
            self.module_dirs = {path.basename(module_dirs):module_dirs}
        elif isinstance(module_dirs,dict):
            self.module_dirs = module_dirs
        else:
            raise ValueError("Only dict or list allowed for `module_dirs'. Found type '%s'." % type(module_dirs))
        for dir in self.module_dirs.values():
            sys.path.insert(0,dir+path.sep+path.pardir)

        # arguments from cli-stdin
        self.settings_parser = ArgumentParser(usage=sys.argv[0]+" modulelist [optional arguments]")
        self._settings_parse_later = {}
        self._settings_parse_later_overwrites_list = []
        self._settings_parse_later_overwrites = {}
        self.settings_parser_required_arguments = []
        self.default_modules = []
        self.bind_events = True

        # internal
        self.halt_parse = False
        self.argparse_called = False
        self.event_objs = {}
        self.event = event(self, optional=False)
        self.event.optional = event(self, optional=True)
        self.state = {}
        self.state_default = {}
        self.modules_loaded = {}
        self.modules_avail = getModulesAvail(self.module_dirs)
        self.miniflask_objs = {} # local modified versions of miniflask
        registerPredefined(self.modules_avail)
        self._varid_list = []
        self._recently_loaded = []
        try:
            self._consolecolumns, self._consolerows = get_terminal_size(0)
        except:
            self._consolecolumns, self._consolerows = 80, 40



    # ------- #
    # helpers #
    # ------- #
    def print_heading(self,*args,color=fg('green'),margin=8):
        line = "—"*self._consolecolumns
        if len(args) > 0:
            s = " ".join(args)
            line = line[:margin] + " " + s + " " + line[margin+len(s)+2:]
        print()
        print(fg('blue')+attr('bold')+line+attr('reset'))

    def print_recently_loaded(self, prepend="", loading_text=highlight_loading):
        for i, mod in enumerate(self._recently_loaded):
            module_id = mod.miniflask_obj.module_id_initial
            is_last = i == len(self._recently_loaded) - 1
            has_children = len(mod.miniflask_obj._recently_loaded) > 0
            if is_last:
                tree_symb         = "    " #"└── "
                tree_symb_current = "╰── "
            elif has_children:
                tree_symb         = "│   "
                tree_symb_current = "│   "
            else:
                tree_symb         = "│   " #"├── "
                tree_symb_current = "├── "
            if prepend == "":
                print(loading_text(module_id))
            else:
                print(prepend+tree_symb_current+loading_text(module_id))
            if len(mod.miniflask_obj._recently_loaded) > 0:
                mod.miniflask_obj.print_recently_loaded(prepend+tree_symb, loading_text)


    # ==================== #
    # module introspection #
    # ==================== #

    # module event
    def getModuleEvents(self, module, dummy=None):
        if not dummy:
            dummy = miniflask_dummy()

        # load module
        mod = import_module(self.modules_avail[module]["importpath"])
        if not hasattr(mod,"register"):
            return []

        mod.register(dummy)
        return dummy.getEvents()

    # pretty print of all available modules
    def showModules(self, dir=None, prepend="", id_pre=None, with_event=True):
        if not dir:
            for basename, dir in self.module_dirs.items():
                self.showModules(dir, prepend=prepend, id_pre=basename if id_pre is None else id_pre+"."+basename, with_event=with_event)
            return

        if id_pre is None:
            id_pre = path.basename(dir)
        if len(prepend) == 0:
            print()
            print(highlight_name(path.basename(id_pre)))
        dirs = [d for d in listdir(dir) if path.isdir(path.join(dir,d)) and not d.startswith("_")]
        for i, d in enumerate(dirs):
            if d.startswith("."):
                continue
            if path.exists(path.join(dir,d,".ignoredir")):
                continue
            module_id = id_pre + "." + d if id_pre != "" else d

            is_module = path.exists(path.join(dir,d,".module"))
            is_lowpriority_module = path.exists(path.join(dir,d,".lowpriority"))
            if is_module:
                shortestid = self.getModuleShortId(module_id)
            has_shortid = is_module and shortestid == d

            if i == len(dirs)-1:
                tree_symb = "└── "
                is_last = True
            else:
                tree_symb = "├── "
                is_last = False
            append = " "+fg('blue')+"("+shortestid+")"+attr('reset') if is_module and not has_shortid else ""
            append += attr('dim')+" (low-priority module)"+attr('reset') if is_lowpriority_module else ""
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
    def getModuleId(self, module_id):
        module_ids = self.modules_avail.keys()
        module = module_id.replace(".","\.(.*\.)*")

        # first search for a default module
        r = re.compile("^(.*\.)?%s(\..*)?\.(default|%s)$" % (module, module_id.split(".")[-1]))
        found_modules = list(filter(r.match, module_ids))

        # if no default module found, check for direct identifier
        if len(found_modules) == 0:
            r = re.compile("^(.*\.)?%s$" % module)
            found_modules = list(filter(r.match, module_ids))

        # if no default module found, check for related identifier
        if len(found_modules) == 0:
            r = re.compile("^(.*\.)?%s(\..*)?$" % module)
            found_modules = list(filter(r.match, module_ids))

        # if more than one module found, exclude all low-priority modules
        if len(found_modules) > 1:
            found_modules = list(filter(lambda mid: not self.modules_avail[mid]["lowpriority"], found_modules))

        # if more than one module found let the user know
        if len(found_modules) > 1:
            raise ValueError(highlight_error()+"Module-Identifier '%s' is not unique. Found %i modules:\n\t%s" % (highlight_module(module_id), len(found_modules), "\n\t".join(found_modules)))

        # no module found with both variants
        elif len(found_modules) == 0:
            raise ValueError(highlight_error()+"Module '%s' not known." % highlight_module(module_id))

        # module_id is a unique identifier
        module = found_modules[0]
        return self.modules_avail[module]["id"]

    # get short id of a moodule
    def getModuleShortId(self, module):
        if not module in self.modules_avail:
            raise ValueError(highlight_error()+"Module '%s' not known." % highlight_module(module))
        uniqueId = self.modules_avail[module]["id"].split(".")

        # modA.default -> modA
        if uniqueId[-1] == "default":
            uniqueId = uniqueId[:-1]

        # find the shortest substring to match a module uniquely
        for i in range(len(uniqueId)-1,0,-1):
            shortid = ".".join(uniqueId[i:])
            try:
                if module == self.getModuleId(shortid):
                    return shortid
                else:
                    pass
            except ValueError as e:
                pass
        return None

    # maps 'folder.subfolder.module.list.of.vars' to 'folder.subfoldder.module'
    def _getModuleIdFromVarId(self, varid, varid_list=None, scope=None):

        # try to use scope.default as module id
        if scope is not None:
            try:
                module_id = self.getModuleId(scope+".default")
                if varid.startswith(scope):
                    varid = varid[len(scope)+1:]
                return module_id, varid
            except ValueError as e:
                pass

            # try to use scope as module id
            try:
                module_id = self.getModuleId(scope)
                if varid.startswith(scope):
                    varid = varid[len(scope)+1:]
                return module_id, varid
            except ValueError as e:
                pass

        # no we have to work out which module may be meant
        if varid_list is None:
            varid_list = varid.split(".")
        for i in range(len(varid_list)-1,0,-1):
            test_id = ".".join(varid_list[:i])
            try:
                return self.getModuleId(test_id), ".".join(varid_list[i:])
            except ValueError as e:
                pass

        # no id could be derived
        return None, ".".join(varid_list)

    # loads module (once)
    def load(self, module_name, verbose=True, auto_query=True, loading_text=highlight_loading, as_id=None, bind_events=True):

        # load list of modules
        if isinstance(module_name, str) and "," in module_name:
            module_name = module_name.split(",")
        if isinstance(module_name,list):
            for m in module_name:
                self.load(m, verbose=verbose, auto_query=auto_query, loading_text=loading_text, as_id=as_id, bind_events=bind_events)
            return

        # get id
        if auto_query:
            module_name = self.getModuleId(module_name)
        elif not module_name in self.modules_avail:
            raise ValueError(highlight_error()+"Module '%s' not known." % highlight_module(module_name))

        # check if already loaded
        if module_name in self.modules_loaded and as_id is None:
            return

        # load module
        mod = import_module(self.modules_avail[module_name]["importpath"])
        if not hasattr(mod,"register"):
            raise ValueError(highlight_error()+"Module '%s' does not register itself." % module_name)
        module_name = module_name if as_id is None else as_id
        mod.miniflask_obj = miniflask_wrapper(module_name, self)
        mod.miniflask_obj.bind_events = bind_events

        # remember loaded modules
        self.modules_loaded[module_name] = mod
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
    def register_default_module(self, module, required_event=None, required_id=None, overwrite_globals={}):
        if required_event and required_id:
            raise RegisterError("Default Modules should depend either on a event interface OR a regular expression. However, both are given")
        if not required_event and not required_id:
            raise RegisterError("Default Modules should depend either on a event interface OR a regular expression. However, none are given")
        self.default_modules.append((module, required_event, required_id, overwrite_globals))

    # saves function to a given (event-)name
    def register_event(self, name, fn, unique=False, call_before_after=True):
        if not self.bind_events:
            return

        # check if is unique event. if yes, check if event already registered
        if name in self.event_objs and (unique or self.event_objs[name].unique):
            eobj = self.event_objs[name].modules if not self.event_objs[name].unique else [self.event_objs[name].modules]

            # catch some user errors
            if not unique and self.event_objs[name].unique:
                raise RegisterError(highlight_error()+"Event '%s' has been registered as `unique` before, but as `non-unique` now. Please check the registrations.\n\t(Imported by %s)" % (highlight_event(name),", ".join(["'"+highlight_module(e.module_name)+"'" for e in eobj])))
            if unique and not self.event_objs[name].unique:
                raise RegisterError(highlight_error()+"Event '%s' has been registered as `non-unique` before, but as `unique` now. Please check the registrations.\n\t(Imported by %s)" % (highlight_event(name),", ".join(["'"+highlight_module(e.module_name)+"'" for e in eobj])))

            raise RegisterError(highlight_error()+"Event '%s' is unique, and thus, cannot be imported twice.\n\t(Imported by %s)" % (highlight_event(name),", ".join(["'"+highlight_module(e.module_name)+"'" for e in eobj])))

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
    def register_defaults(self, defaults, scope="", overwrite=False, cliargs=True, parsefn=True):
        if scope is None:
            scope = ""

        # save exception for later
        callee_traceback = save_traceback()

        # now register every key-value pair
        for key, val in defaults.items():

            # unique & full varname is fully defined using scope
            varname = scope+"."+key if len(scope) > 0 else key
            key_split = varname.split(".")

            # get module id from global varname identifier
            module_id, key = self._getModuleIdFromVarId(varname,key_split,scope=scope)
            if module_id is not None:

                # retrieve real local key name
                module_short_id = self.getModuleShortId(module_id)

                # recreate actual key
                module_id = self.getModuleId(module_id)
                varname = module_id + "." + key

            # actual initialization is done when all modules has been parsed
            if overwrite:
                self._settings_parse_later_overwrites_list.append((varname, val, cliargs, parsefn, callee_traceback, self) )
            else:

                # pre-initialize variable for possible lambda expressions in second pass
                # (we can only be sure, that the varname is the unique varid if we are not overwriting)
                if hasattr(self.state,"all"):
                    self.state.all[varname] = val
                else:
                    self.state[varname] = val

                self._settings_parse_later[varname] = (val, cliargs, parsefn, callee_traceback, self)

    def _settings_parser_add(self, varname, val, callee_traceback, nargs=None, default=None):

        # lists are just multiple arguments
        if isinstance(val,list):
            if len(val) == 0:
                raise RegisterError("Variable '%s' is registered as list (see exception below), however it is required to define the type of the list arguments for it to become accessible from cli.\n\nYour options are:\n\t- define a default list, e.g. [\"a\", \"b\", \"c\"]\n\t- define the list type, e.g. [str]\n\t- define the variable as a helper using register_helpers(...)" % (fg('red')+varname+attr('reset')), traceback=callee_traceback)
            self._settings_parser_add(varname, val[0], callee_traceback, nargs="+", default=val)
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
            self.settings_parser_required_arguments.append([varname])

        # for bool: enable --varname as alternative for --varname true
        if argtype == str2bool and nargs != '+':
            kwarg_long["nargs"]  = kwarg_short["nargs"] = '?'
            kwarg_long["const"]  = kwarg_short["const"] = True

        # define the actual arguments
        if argtype in [int,str,float,str2bool]:
            self.settings_parser.add_argument( "--"+varname, **kwarg_long)
        else:
            raise ValueError("Type '%s' not supported. (Used for setting '%s')" % (type(val), varname))

        # for bool: enable --no-varname as alternative for --varname false
        # Note: this has to be defined AFTER --varname
        if argtype == str2bool and nargs != '+':
            self.settings_parser.add_argument('--no-'+varname, dest=varname, action='store_false')

        # remember the varname also for fuzzy searching
        self._varid_list.append(varname)

    # ======= #
    # runtime #
    # ======= #
    def stop_parse(self):
        self.halt_parse = True

    def parse_args(self, argv=None, optional=True, fuzzy_args=True):
        if self.argparse_called:
            raise SystemError("The function `parse_args` has been called already. Did you maybe called `mf.parse_args()` and `mf.run()` in the same script? Solutions are:\n\t- Please use only one of those functions.\n\t- If you actually need both functions, please do not hesitate to write an issue on\n\t\thttps://github/da-h/miniflask/issues\n\t  to explain you used case.\n\t  (It's not hard to implement, but I need to know, if and when this functionality is needed. ;) )")

        if not argv:
            argv = sys.argv#[1:]
        else:
            argv = [None]+argv

        # actually parse the input
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
        if len(self.default_modules) > 1:
            self.print_heading("Loading Automatically Requested Default Modules")
        for module, event, glob, overwrite_globals in self.default_modules:
            if event:
                if not isinstance(module,list):
                    module = [module]
                modules_already_loaded = all(self.getModuleId(m) in self.modules_loaded for m in module)
                if not modules_already_loaded and not event in self.event_objs:
                    self.load(module, loading_text=lambda x: highlight_loading_default(event,x))
                    self.register_defaults(overwrite_globals, scope="", overwrite=True)
                else:
                    found = self.event_objs[event].modules
                    if not isinstance(found,list):
                        found = [found]
                    found = [f.module_id for f in found]
                    print(highlight_loaded_default(found,event))

                # overwrite defaults if loaded default module itself or did not load module yet
                if modules_already_loaded:
                    self.register_defaults(overwrite_globals, scope="", overwrite=True)

            elif glob:
                found = [highlight_loading_module(x) for x in keys if re.search(glob, x)]
                if len(found) == 0:
                    self.load(module, loading_text=lambda x: highlight_loading_default(glob,x))
                    self.register_defaults(overwrite_globals, scope="", overwrite=True)
                elif len(found) > 1:
                    print(highlight_loaded_default(found,glob))
                else:
                    print(highlight_loaded_default(found,glob))


        # check fuzzy matching of overwrites
        for varname, val, cliargs, parsefn, callee_traceback, _mf in self._settings_parse_later_overwrites_list:
            if varname not in self._settings_parse_later:
                found_varids = get_varid_from_fuzzy(varname,self._settings_parse_later.keys()) 
                if len(found_varids) == 0:
                    raise RegisterError("Variable '%s' is not registered yet, however it seems like you wold like to overwrite it (see exception below)." % (fg('red')+varname+attr('reset')), traceback=callee_traceback)
                elif len(found_varids) > 1:
                    raise RegisterError("Variable-Identifier '%s' is not unique. Found %i variables:\n\t%s\n\n    Call:\n        %s" % (highlight_module(found_varids), len(found_varids), "\n\t".join(found_varids), " ".join(found_varids)), traceback=callee_traceback)
                else:
                    self._settings_parse_later_overwrites[found_varids[0]] = (val, cliargs, parsefn, callee_traceback, _mf)
            else:
                self._settings_parse_later_overwrites[varname] = (val, cliargs, parsefn, callee_traceback, _mf)

        # add variables to argparse and remember defaults
        settings_recheck = {}
        for settings in [self._settings_parse_later,self._settings_parse_later_overwrites, settings_recheck]:
            overwrite = settings == self._settings_parse_later_overwrites 
            recheck = settings == settings_recheck
            for varname, (val, cliargs, parsefn, callee_traceback, _mf) in settings.items():
                is_fn = callable(val) and type(val) != type and parsefn

                # eval dependencies/like expressions
                if is_fn:
                    try:
                        the_val = val
                        while callable(the_val) and type(the_val) != type:
                            the_val = the_val(_mf.state,self.event)
                    except RecursionError as e:
                        raise RecursionError("In parsing of value '%s'." % varname)
                else:
                    the_val = val

                # remember caculated values for other lambda expressions
                self.state[varname] = the_val

                # register user-changeable variables
                if cliargs:

                    # remember default state for 'settings' module
                    if is_fn:
                        val.default = the_val
                        self.state_default[varname] = val
                    else:
                        self.state_default[varname] = the_val

                    # repeat function parsing later
                    # (in case we have overwritten a dependency during second pass, overwrite == True)
                    if is_fn and not recheck:
                        settings_recheck[varname] = (val, cliargs, parsefn, callee_traceback, _mf)

                    # add to argument parser
                    # Note: the condition ensures that the last value (an overwrite-variable) should be the one that generates the argparser)
                    if recheck or overwrite and varname not in settings_recheck or varname not in self._settings_parse_later_overwrites and varname not in settings_recheck:
                        self._settings_parser_add(varname, the_val, callee_traceback)


        # add help message
        print_help = False
        if "-h" in argv:
            argv.remove("-h")
            print_help = True
        if "--help" in argv:
            argv.remove("--help")
            print_help = True

        # split --varname=value expressions
        argv = [v  for val in argv for v in (val.split("=",1) if val.startswith("--") or val.startswith("-") and not val[1:].isnumeric() else [val])]

        # remember varids from user-args & fuzzy matching the settings
        user_varids = {}
        for i in range(len(argv)):
            varid = argv[i]
            if not varid.startswith("--"):
                if varid.startswith("-") and not varid[1:].replace('.','',1).isdigit():
                    varid = argv[i] = "-"+argv[i]
                else:
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
                    raise ValueError(highlight_error()+"Variable-Identifier '--%s' is not unique. Found %i variables:\n\t%s\n\n    Call:\n        %s" % (highlight_module(varid), len(found_varids), "\n\t".join(found_varids), " ".join(argv)))

                # no module found with both variants
                elif len(found_varids) == 0:
                    argv[i] = highlight_module(argv[i])
                    raise ValueError(highlight_error()+"Variable '--%s' not known.\n\n    Call:\n       %s" % (highlight_module(varid)," ".join(argv)))

                varid = found_varids[0]

                # replace with fuzzy-found varid
                argv[i] = ("--no-" if was_false_bool else "--")+found_varids[0]

            # remember this varid has been overwritten by the user
            user_varids[varid] = True

        # parse user overwrites (first time, s.t. lambdas change adaptively)
        settings_args = self.settings_parser.parse_args(argv[2:])
        for varname, val in vars(settings_args).items():
            self.state[varname] = val

        # check if required arguments are given by now
        missing_arguments = []
        for variables in self.settings_parser_required_arguments:
            if self.state[variables[0]] is None:
                missing_arguments.append(variables)
        if len(missing_arguments) > 0:
            self.settings_parser.error(linesep+linesep.join(["The following argument is required: "+" or ".join(["--"+arg for arg in reversed(args)]) for args in missing_arguments]))

        # finally parse lambda-dependencies
        for varname, (val, cliargs, parsefn, callee_traceback, _mf) in self._settings_parse_later.items():
            # Note: if has not been overwritten by user lambda can be evaluated again
            # Three cases exist in wich lambda expression shall be recalculated:
            # The value is a function AND one of
            # 1. was helper variable, thus no cli-argument can overwrite it anyway
            # 2. the value has not been overwritten by user
            while callable(val) and type(val) != type and parsefn and (not cliargs or varname not in user_varids):
                val = val(_mf.state,_mf.event)
                self.state[varname] = val

        # print help message when everything is parsed
        self.settings_parser.print_help = lambda: (print("usage: modulelist [optional arguments]"),print(),print("optional arguments (and their defaults):"),print(listsettings(state("",self.state,self.state_default),self.event)))
        if print_help:
            self.settings_parser.parse_args(['--help'])

        # mark this instance as run
        self.argparse_called = True

    def run(self, modules=["settings"], call="main"):
        try:

            self.print_heading("Loading Modules")

            # load required modules
            self.load(modules)

            # parse command line arguments & overwrite default parameters
            self.parse_args()

            # check if all requested modules are loaded
            if not self.halt_parse:

                # optional init event
                if hasattr(self.event,'init'):
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
                    print("No event '{0}' registered. "
                          "Please make sure to register the event '{0}', "
                          "or provide a suitable event to call with mf.run(call=\"myevent\").".format(call))
        except (RegisterError,StateKeyError) as e:
            gettrace = getattr(sys, 'gettrace', None)

            # check if debugger will catch this
            if not gettrace or not gettrace():
                tb = traceback.extract_tb(e.__traceback__)
                print()
                print(fg("red")+"Uncatched Exception occured. Traceback:"+attr("reset"))
                print(format_traceback_list(tb, exc=e, ignore_miniflask=False))
                sys.exit(1)
            else:
                raise
        except Exception as e:
            gettrace = getattr(sys, 'gettrace', None)

            # check if debugger will catch this
            if not gettrace or not gettrace():
                tb = traceback.extract_tb(e.__traceback__)
                print()
                print(fg("red")+"Uncatched Exception occured. Traceback:"+attr("reset"))
                print(format_traceback_list(tb, exc=e, ignore_miniflask=not self.debug))
                sys.exit(1)
            else:
                raise

relative_import_re = re.compile("(\.+)(.*)")
class miniflask_wrapper(miniflask):
    def __init__(self, module_name, mf):
        self.module_id = module_name
        self.module_id_initial = module_name
        self.module_name = module_name.split(".")[-1]
        self.module_base = module_name.split(".")[0]
        self.wrapped_class = mf.wrapped_class if hasattr(mf, 'wrapped_class') else mf
        self.state = state(module_name, self.wrapped_class.state, self.wrapped_class.state_default)
        self._recently_loaded = []
        self._defined_events = {}

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

    def redefine_scope(self,new_module_name):
        old_module_name = self.module_id
        new_module_name = self.set_scope(new_module_name)
        if new_module_name in self.modules_avail:
            raise ValueError("Scope `%s` already used. Cannot define multiple modules using `redefine_scope`. Did you maybe mean to use `set_scope`?" % new_module_name)
        m = self.modules_avail[old_module_name]
        del self.modules_avail[old_module_name]
        m["id"] = new_module_name
        self.modules_avail[new_module_name] = m

    def set_scope(self,new_module_name):
        new_module_name, was_relative = self._get_relative_module_id(new_module_name)
        if not was_relative:
            new_module_name = self.module_base + "." + new_module_name
        self.module_id = new_module_name
        self.state.module_id = new_module_name
        return new_module_name

    # like with relative imports
    def like(self, varname, alt, scope="."):
        scope_name = scope
        if scope is not None:
            scope, was_relative = self._get_relative_module_id(scope)
        return like(varname, alt, scope=scope, scope_name=scope_name)

    # loads module dependencies as child module
    def load_as_child(self, module_name, **kwargs):
        self.load(module_name, as_id='.', bind_events=False, **kwargs)

    # enables relative imports
    def load(self, module_name, as_id=None, auto_query=True, **kwargs):

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
            as_id, _ = self._get_relative_module_id(as_id, offset=1)

        # parse relative imports first
        module_name, was_relative = self._get_relative_module_id(module_name)
        auto_query = not was_relative

        # call load (but ensure no querying is made if relative imports were given)
        super().load(module_name, auto_query=auto_query, verbose=False, as_id=as_id, **kwargs)

    # overwrite state defaults
    def register_event(self, name, fn, **kwargs):
        self._defined_events[name] = fn
        super().register_event(name, fn, **kwargs)

    # overwrite state defaults
    def register_defaults(self, defaults, scope=None, **kwargs):
        # default behaviour is to use current module-name
        if scope is None:
            scope = self.module_id
        scope, was_relative = self._get_relative_module_id(scope, offset=1)
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

