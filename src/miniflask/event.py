
class event():
    def __init__(self, mf):
        self._mf = mf

    def __getattr__(self, name):
        if name == "_mf":
            return super().__getattribute__(name)
        if name not in self._mf.events:
            raise AttributeError("The Event %s has not been registered yet." % name)
        def fn_wrap(*args,**kwargs):
            return self._mf.events[name](self._mf.state,self._mf.event,*args,**kwargs)
        return fn_wrap


