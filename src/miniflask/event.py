from .dummy import dummy_fn, dummy_fn_unique
import collections
import inspect
from functools import partial

class outervar():
    pass



class event_obj():
    def __init__(self, fn, unique, module):
        self.unique = unique
        if unique:
            self.fn = fn
            self.modules = module
        else:
            self.fn = [fn]
            self.modules = [module]

class event():
    def __init__(self, mf, optional=False, unique=False):
        self._mf = mf
        self.optional_value = optional
        self.unique_value = unique
        self.locals = {}

    def __getattr__(self, name):

        if name not in self._mf.event_objs:
            if not self.optional_value:
                raise AttributeError("The Event '%s' has not been registered yet." % name)
            if self.unique_value:
                fn_wrap = dummy_fn_unique
            else:
                fn_wrap = dummy_fn

        else:

            eobj = self._mf.event_objs[name]

            # fn_wrap_scope creates a function wrap of fn that passes also state and event of eobj
            # additionally, if outervar is defined as a default, it queries that from the last outer scope
            def fn_wrap_scope(fn, state, event, needed_locals=[]):

                # get kwargs of fn wit outervar as default
                signature = inspect.signature(fn)
                needed_locals = [
                    k for k, v in signature.parameters.items()
                    if v.default is not inspect.Parameter.empty and v.default is outervar
                ]

                # if no outervar found, just pass state and event
                if len(needed_locals) > 0:
                    def fn_wrap(*args, **kwargs):
                        outer_locals = {}
                        all_outer_locals = inspect.currentframe().f_back.f_locals
                        outer_locals = {k: all_outer_locals[k] for k in needed_locals}
                        return fn(state,event,*args,**outer_locals,**kwargs)
                else:
                    def fn_wrap(*args, **kwargs):
                        return fn(state,event,*args,**kwargs)
                return fn_wrap

            if eobj.unique:
                fn_wrap = fn_wrap_scope(eobj.fn, eobj.modules.state, eobj.modules.event)
            else:
                def multiple_fn_wrap_scope(fns, modules=eobj.modules):
                    fns = [fn_wrap_scope(fn, state=module.state, event=module.event) for fn, module in zip(fns,modules)]
                    def fn_wrap(*args,**kwargs):
                        return [fn(*args, **kwargs) for fn in fns]
                    return fn_wrap
                fn_wrap = multiple_fn_wrap_scope(eobj.fn)

        setattr(self,name, fn_wrap)
        return fn_wrap


