from .dummy import dummy_fn

class event_obj():
    def __init__(self, fn, unique, module):
        self.unique = unique
        self.modules = [module]
        if unique:
            self.fn = fn
        else:
            self.fn = [fn]

class event():
    def __init__(self, mf, optional=False):
        self._mf = mf
        self.optional_value = optional

    def __getattr__(self, name):
        if name == "_mf":
            return super().__getattribute__(name)
        elif name == "optional_value":
            return super().__getattribute__(name)
        elif name == "optional":
            return super().__getattribute__("_mf").event_optional
        if name not in self._mf.event_objs:
            if not self.optional_value:
                raise AttributeError("The Event %s has not been registered yet." % name)
            else:
                return dummy_fn
        def fn_wrap(*args,**kwargs):
            eobj = self._mf.event_objs[name]
            if eobj.unique:
                return eobj.fn(self._mf.state,self._mf.event,*args,**kwargs)
            else:
                return [fn(self._mf.state,self._mf.event,*args,**kwargs) for fn in eobj.fn]
        return fn_wrap


