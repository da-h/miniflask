from colored import fg, bg, attr

class state(dict):
    def __init__(self, module_name, state, state_default):
        self.all = state
        self.default = state_default
        self.module_name = module_name

    def scope(self, module_name, local=False):
        return state(self.module_name+"."+module_name if local else module_name, self.state, self.state_default)

    def __contains__(self, name):
        return self.module_name+"."+name in self.all if len(self.module_name) > 0 else name in self.all
    def __getitem__(self, name):
        return self.all[self.module_name+"."+name if len(self.module_name) > 0 else name]
    def __setitem__(self, name, val):
        self.all[self.module_name+"."+name if len(self.module_name) > 0 else name] = val

    def __getattribute__(self, name):
        return super().__getattribute__(name)

class like:
    def __init__(self, varname, alt):
        self.varname = varname
        self.alt = alt
        self.fn = lambda state,event: state[varname] if varname in state else alt

    def __call__(self, state, event):
        return self.fn(state,event)

    def __str__(self):
        return attr('dim')+"'"+str(self.varname)+"' or '"+str(self.alt)+"' ⟶   "+attr('reset')+str(self.default)

