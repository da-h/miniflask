# package modules
from .event import event
from .dummy import miniflask_dummy
from .util import getModulesAvail
from .modules import registerPredefined

# global modules
import sys
from os import path, listdir
from colored import fg, bg, attr
from importlib import import_module
import argparse

# coloring
highlight_error = lambda: fg('red')+attr('bold')+"Error:"+attr('reset')+" "
highlight_name = lambda x: fg('blue')+attr('bold')+x+attr('reset')
highlight_module = lambda x: fg('green')+attr('bold')+x+attr('reset')
highlight_loading = lambda x: "Load Module ... "+highlight_module(x)
highlight_loaded_none = lambda x: fg('red')+x+attr('reset')
highlight_loaded = lambda x, y: attr('underlined')+x+attr('reset')+" "+fg('green')+attr('bold')+", ".join(y)+attr('reset')
highlight_event = lambda x: fg('light_yellow')+x+attr('reset')
highlight_blue_line = lambda x: fg('blue')+attr('bold')+x+attr('reset')

# ================ #
# MiniFlask Kernel #
# ================ #

class miniflask():
    def __init__(self, modules_dir, args=None):

        # module dir to be read from
        self.modules_dir = modules_dir
        sys.path.insert(0,self.modules_dir)

        # arguments from cli-stdin
        self.args = args

        # internal
        self.halt_parse = False
        self.events = {}
        self.events_unique = {}
        self.event = event(self)
        self.state = {}
        self.modules_loaded = {}
        self.modules_avail = getModulesAvail(self.modules_dir)
        registerPredefined(self.modules_avail)



    # ==================== #
    # module introspection #
    # ==================== #

    # module event
    def getModuleEvents(self, module, dummy=None):
        if not dummy:
            dummy = miniflask_dummy()

        # load module
        mod = import_module(self.modules_avail[module][1])
        if not hasattr(mod,"register"):
            return []

        mod.register(dummy)
        return dummy.getEvents()

    # pretty print of all available modules
    def showModules(self, dir=None, prepend="", id_pre="", with_event=True):
        if not dir:
            dir = self.modules_dir
        if len(prepend) == 0:
            print(highlight_name("."))
        dirs = [d for d in listdir(dir) if path.isdir(path.join(dir,d)) and not d.startswith("_")]
        for i, d in enumerate(dirs):
            is_last = False
            is_module = path.exists(path.join(dir,d,".module"))
            module_id = id_pre + "." + d if id_pre != "" else d
            if i == len(dirs)-1:
                print(prepend+"└── "+(highlight_name(d) if is_module else d))
                is_last = True
            else:
                print(prepend+"├── "+(highlight_name(d) if is_module else d))
            if is_module:
                if with_event:
                    events = self.getModuleEvents(d)
                    if len(events) > 0:
                        for e in events:
                            unique_flag = "!" if e[1] else ">"
                            tree_symb = "     " if is_last else "│    "
                            print(prepend+tree_symb+unique_flag+" "+highlight_event(e[0]))
                continue
            self.showModules(path.join(dir,d),prepend=prepend+"    " if is_last else "│   ", id_pre=module_id, with_event=with_event)

    # pretty print loaded modules
    def __repr__(self):
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
        return self.modules_avail[module][1]
    
    # loads module (once)
    def load(self, module, verbose=True):

        # load list of modules
        if isinstance(module,list):
            for m in module:
                self.load(m)
            return

        # get id
        module = self.getModuleId(module)

        # check if module exists or is already loaded
        if not module in self.modules_avail:
            raise ValueError(highlight_error()+"Module '%s' not known." % module)
        if module in self.modules_loaded:
            return

        # load module
        print(highlight_loading(self.modules_avail[module][1]))
        mod = import_module(self.modules_avail[module][1])
        if not hasattr(mod,"register"):
            raise ValueError(highlight_error()+"Module '%s' does not register itself." % module)

        # remember loaded modules
        self.modules_loaded[self.modules_avail[module][1]] = mod

        # register events
        mod.register(self)

    # saves function to a given (event-)name
    def register_event(self,name,fn,unique=False):

        # check if is unique event. if yes, check if event already registered
        if name in self.events and (unique or self.events_unique[name]):
            print(self.events[name])
            raise ValueError(highlight_error()+"Event '%s' is unique, and thus, cannot be imported twice.\n\t(Imported by '%s')" % (highlight_event(name),highlight_module("blub")))

        # register event
        self.events_unique[name] = unique
        if name in self.events:
            self.events[name].append(fn)
        else:
            self.events[name] = fn

    # overwrite state defaults
    def register_defaults(self, defaults):
        self.state.update(defaults)


    # ======= #
    # runtime #
    # ======= #
    def stop_parse(self):
        self.halt_parse = True

    def parse_args(self):
        self.halt_parse = False

        parser = argparse.ArgumentParser()
        parser.add_argument('cmds')
        args, unknown = parser.parse_known_args(self.args)

        cmds = args.cmds.split(',')
        for cmd in cmds:
            if self.halt_parse:
                break
            try:
                self.load(cmd)
            except Exception as e:
                print(e)
        print(highlight_blue_line("-"*50))
