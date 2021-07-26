def dummy_fn(*args, altfn=None, **kwargs):
    if callable(altfn):
        return altfn(*args, **kwargs)
    return []


class miniflask_dummy():
    def __init__(self, *args, with_child=True, **kwargs):
        del args, kwargs  # unused
        self.event_objs = {}
        self.modules_avail = {}
        self.modules_loaded = {}
        if with_child:
            self.event = miniflask_dummy(with_child=False)

    def getEvents(self):
        return list(zip(self.event_objs.keys(), self.event_objs.values()))

    def register_event(self, name, fn, unique=True, call_before_after=True):
        del call_before_after  # unused
        self.event_objs[name] = (unique, fn)

    def register_defaults(self, *args, **kwargs):
        pass

    # ignore all other function calls
    def __getattr__(self, name):
        if name in ["event", "modules_avail", "modules_loaded", "register_event", "register_defaults"]:
            return super().__getattribute__(name)
        return dummy_fn
    # def load(self,*args):
    #     pass
    # def showModules(self,*args):
    #     pass
