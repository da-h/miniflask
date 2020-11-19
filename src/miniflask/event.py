from .exceptions import RegisterError
import collections
import inspect
from functools import partial
from colored import fg, attr

class outervar():
    pass

class event_obj():
    def __init__(self, fn, unique, module, call_before_after=True):
        self.unique = unique
        self.call_before_after = call_before_after
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

    def make_dummy_fn(self, name, call_before_after=True):
        # automatic before/after events
        name_before = 'before_'+name
        name_after  = 'after_'+name
        has_before  = name_before in self._mf.event_objs and call_before_after
        has_after   = name_after in self._mf.event_objs and call_before_after
        fn_after    = getattr(self._mf.event, name_after) if has_after else None
        fn_before   = getattr(self._mf.event, name_before) if has_before else None

        def dummy_fn(*args, altfn=None, **kwargs):
            if callable(altfn):
                if has_before:
                    for fn_b in fn_before.fns:
                        args, kwargs = fn_b(*args, **kwargs)
                res = altfn(*args, **kwargs)
                if has_after:
                    for fn_a in fn_after.fns:
                        res, args, kwargs = fn_a(res, *args, **kwargs)
                return res
            return []

        return dummy_fn

    def __getattr__(self, name):

        if name not in self._mf.event_objs:
            if not self.optional_value:
                raise AttributeError("The Event '%s' has not been registered yet." % name)
            fn_wrap = self.make_dummy_fn(name, call_before_after=True)

        else:

            eobj = self._mf.event_objs[name]
            call_before_after = eobj.call_before_after

            # fn_wrap_scope creates a function wrap of fn that passes also state and event of eobj
            # additionally, if outervar is defined as a default, it queries that from the last outer scope
            def fn_wrap_scope(fn, state, event, module, needed_locals=None, miniflask_args=None, skip_twice=False, call_before_after=call_before_after):
                if needed_locals is None:
                    needed_locals = []
                if miniflask_args is None:
                    miniflask_args = []

                # get kwargs of fn wit outervar as default
                try:
                    signature = inspect.signature(fn)
                    needed_locals = [
                        k for k, v in signature.parameters.items()
                        if v.default is not inspect.Parameter.empty and v.default is outervar
                    ]
                    arg_names = [k for k, v in signature.parameters.items()]
                    has_altfn = "altfn" in arg_names
                    has_signature = True
                except ValueError:
                    needed_locals = []
                    arg_names = []
                    has_altfn = False
                    has_signature = False

                # automatic before/after events
                name_before = 'before_'+name
                name_after  = 'after_'+name
                has_before  = name_before in self._mf.event_objs and call_before_after
                has_after   = name_after in self._mf.event_objs and call_before_after
                fn_after    = getattr(self._mf.event, name_after) if has_after else None
                fn_before   = getattr(self._mf.event, name_before) if has_before else None

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
                        if has_before:
                            for fn_b in fn_before.fns:
                                args, kwargs = fn_b(*args, **kwargs)
                        res = fn(*miniflask_args,*args,**outer_locals,**kwargs)
                        if has_after:
                            for fn_a in fn_after.fns:
                                res, args, kwargs = fn_a(res, *args, **kwargs)
                        return res
                elif len(miniflask_args) > 0:
                    def fn_wrap(*args, altfn=None, **kwargs):
                        if has_altfn:
                            kwargs["altfn"] = altfn
                        if has_before:
                            for fn_b in fn_before.fns:
                                args, kwargs = fn_b(*args, **kwargs)
                        res = fn(*miniflask_args, *args, **kwargs)
                        if has_after:
                            for fn_a in fn_after.fns:
                                res, args, kwargs = fn_a(res, *args, **kwargs)
                        return res
                else:
                    # it would be nice to let the user know, if the definition may be wrong at this point,
                    # however, we cannot know, if the call will contain the altfn-argument
                    # (up until we have a clean concept for this, we do not catch these definition errors)
                    # if not has_altfn and self.optional_value:
                    #     raise RegisterError(("The event %s was called using `event.optional(..., alftn=...)`, but the function does not catch this argument.\n\n"+fg('red')+"Possible Solutions:"+attr('reset')+"\n  - add `**kwargs` or `altfn=None` to your event-function definition.\n  - Alternatively, add either `event` or `state` or both to the event-function definition. In that case miniflask can catch altfn itself, however, this may adversely affect performance if this function is callled often.") % (fg('red')+name+attr('reset')))
                    return fn, has_signature
                return fn_wrap, has_signature

            if eobj.unique:
                fn_wrap, has_signature = fn_wrap_scope(eobj.fn, eobj.modules.state, eobj.modules.event, eobj.modules)
                if has_signature:
                    setattr(fn_wrap, 'modules', [eobj.modules.module_id])
                    setattr(fn_wrap, 'fns', [fn_wrap])
            else:
                def multiple_fn_wrap_scope(orig_fns, modules=eobj.modules):
                    fns, have_signature = zip(*[fn_wrap_scope(fn, state=module.state, event=module.event, module=module, skip_twice=True) for fn, module in zip(orig_fns,modules)])
                    def fn_wrap(*args, altfn=None, **kwargs):
                        results = []
                        for i,fn in enumerate(fns):
                            results.append(fn(*args, **kwargs))
                        return results
                    return fn_wrap, fns, have_signature
                fn_wrap, fns, have_signature = multiple_fn_wrap_scope(eobj.fn)
                setattr(fn_wrap, 'modules', [m.module_id for m, has_sig in zip(eobj.modules, have_signature) if has_sig])
                setattr(fn_wrap, 'fns', [fn for fn, has_sig in zip(fns, have_signature) if has_sig])

        setattr(self, name, fn_wrap)
        return fn_wrap


