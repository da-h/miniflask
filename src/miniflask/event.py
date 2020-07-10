from .dummy import dummy_fn
from .exceptions import RegisterError
import collections
import inspect
from functools import partial
from colored import fg, attr

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

class event(dict):
    def __init__(self, mf, optional=False):
        self._mf = mf
        self.optional_value = optional
        self.locals = {}

    def __getattr__(self, name):

        if name not in self._mf.event_objs:
            if not self.optional_value:
                raise AttributeError("The Event '%s' has not been registered yet." % name)
            fn_wrap = dummy_fn

        else:

            eobj = self._mf.event_objs[name]

            # fn_wrap_scope creates a function wrap of fn that passes also state and event of eobj
            # additionally, if outervar is defined as a default, it queries that from the last outer scope
            def fn_wrap_scope(fn, state, event, module, needed_locals=None, miniflask_args=None, skip_twice=False):
                if needed_locals is None:
                    needed_locals = []
                if miniflask_args is None:
                    miniflask_args = []

                # get kwargs of fn wit outervar as default
                signature = inspect.signature(fn)
                needed_locals = [
                    k for k, v in signature.parameters.items()
                    if v.default is not inspect.Parameter.empty and v.default is outervar
                ]
                arg_names = [k for k, v in signature.parameters.items()]
                has_altfn = "altfn" in arg_names

                # get index of "state" / "event"
                if len(arg_names) > 0:
                    if arg_names[0] == "state":
                        miniflask_args.append(state)
                        if len(arg_names) > 1 and arg_names[1] == "event":
                            miniflask_args.append(event)
                    elif arg_names[0] == "event":
                        miniflask_args.append(event)
                        if len(arg_names) > 1 and arg_names[1] == "state":
                            miniflask_args.append(state)

                # if no outervar found, just pass state and event
                if len(needed_locals) > 0:
                    def fn_wrap(*args, altfn=None, **kwargs):
                        outer_locals = {}
                        if skip_twice:
                            all_outer_locals = inspect.currentframe().f_back.f_back.f_locals
                        else:
                            all_outer_locals = inspect.currentframe().f_back.f_locals
                        outer_locals = {k: all_outer_locals[k] for k in needed_locals}
                        if has_altfn:
                            kwargs["altfn"] = altfn
                        return fn(*miniflask_args,*args,**outer_locals,**kwargs)
                elif len(miniflask_args) > 0:
                    def fn_wrap(*args, altfn=None, **kwargs):
                        if has_altfn:
                            kwargs["altfn"] = altfn
                        return fn(*miniflask_args,*args,**kwargs)
                else:
                    if not has_altfn and self.optional_value:
                        raise RegisterError(("The event %s was called using `event.optional(..., alftn=...)`, but the function does not catch this argument.\n\n"+fg('red')+"Possible Solutions:"+attr('reset')+"\n  - add `**kwargs` or `altfn=None` to your event-function definition.\n  - Alternatively, add either `event` or `state` or both to the event-function definition. In that case miniflask can catch altfn itself, however, this may adversely affect performance if this function is callled often.") % (fg('red')+name+attr('reset')))
                    return fn
                return fn_wrap

            if eobj.unique:
                fn_wrap = fn_wrap_scope(eobj.fn, eobj.modules.state, eobj.modules.event, eobj.modules)
                setattr(fn_wrap, 'modules', [eobj.modules.module_id])
                setattr(fn_wrap, 'fns', [fn_wrap])
            else:
                def multiple_fn_wrap_scope(orig_fns, modules=eobj.modules):
                    fns = [fn_wrap_scope(fn, state=module.state, event=module.event, module=module, skip_twice=True) for fn, module in zip(orig_fns,modules)]
                    def fn_wrap(*args, altfn=None, **kwargs):
                        results = []
                        for i,fn in enumerate(fns):
                            results.append(fn(*args, **kwargs))
                        return results
                    return fn_wrap, fns
                fn_wrap, fns = multiple_fn_wrap_scope(eobj.fn)
                setattr(fn_wrap, 'modules', [m.module_id for m in eobj.modules])
                setattr(fn_wrap, 'fns', fns)

        setattr(self,name, fn_wrap)
        return fn_wrap


