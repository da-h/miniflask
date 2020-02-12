class event_obj():
    def __init__(self, fn, unique, module):
        self.unique = unique
        self.modules = [module]
        if unique:
            self.fn = fn
        else:
            self.fn = [fn]

class event():
    def __init__(self, mf):
        self._mf = mf

    def __getattr__(self, name):
        if name == "_mf":
            return super().__getattribute__(name)
        if name not in self._mf.event_objs:
            raise AttributeError("The Event %s has not been registered yet." % name)
        def fn_wrap(*args,**kwargs):
            eobj = self._mf.event_objs[name]
            if eobj.unique:
                return eobj.fn(self._mf.state,self._mf.event,*args,**kwargs)
            else:
                return [fn(self._mf.state,self._mf.event,*args,**kwargs) for fn in eobj.fn]
        return fn_wrap


