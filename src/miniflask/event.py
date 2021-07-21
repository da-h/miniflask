import inspect
from typing import Callable, List
from dataclasses import dataclass


class outervar:  # pylint: disable=too-few-public-methods
    pass


@dataclass
class event_obj:
    fn: Callable or List[Callable]
    unique: bool
    modules: str or List[str]
    call_before_after: bool = True

    def __post_init__(self):
        if not self.unique:
            self.fn = [self.fn]
            self.modules = [self.modules]


class event(dict):
    def __init__(self, mf, optional=False):
        self._mf = mf
        self.optional_value = optional
        super().__init__()

    def make_dummy_fn(self, name, call_before_after=True):
        # automatic before/after events
        name_before = 'before_' + name
        name_after = 'after_' + name
        has_before = name_before in self._mf.event_objs and call_before_after
        has_after = name_after in self._mf.event_objs and call_before_after
        fn_after = getattr(self._mf.event, name_after) if has_after else None
        fn_before = getattr(self._mf.event, name_before) if has_before else None

        def dummy_fn(*args, altfn=None, **kwargs):
            if callable(altfn):
                if has_before:
                    for fn_b in fn_before.subevents:
                        args, kwargs = fn_b(*args, **kwargs)
                res = altfn(*args, **kwargs)
                if has_after:
                    for fn_a in fn_after.subevents:
                        res, args, kwargs = fn_a(res, *args, **kwargs)
                return res
            return []

        return dummy_fn

    def __getattr__(self, name):  # noqa: C901 too-complex  pylint: disable=too-many-statements
        r"""!event calling
        Events can be called using the event object, i.e. in another event or after initialization of miniflask using the global mf.event object.

        There are two types of calls.

        **Mandatory Calls**  
        You expect this event to exist and to be called using a self-specified interface.
        E.g.:

        ```python
        event.main()
        result = event.required_function("some argument")
        ```

        *Note*: This code will raise an Exception, if one of the two events `main` or `required_function` are not defined (or differ in their interface to the expectation of the call).

        **Optional Calls**  
        You want an event to be called if it is defined, but if it isn't you don't mind? Then use the following call:
        E.g.:

        ```python
        event.optional.main()
        result = event.optional.name_of_event("some argument")
        result = event.optional.name_of_event("some argument", altfn=lambda s: s+" (no optional event used)")
        ```
        \n

        # Note {.alert}
        - `event.optional.eventname()` treats the event like a `nonunique` event, thus it returns an list of results.
        - `event.optional.eventname(..., altfn=...)` treats the event like a `unique` event, but in case no event was defined, it uses altfn to parse the arguments.
        # .{.end}


        ### Performance Note {.alert}
        Leaving the `event`, `state` and `mf` arguments out from an event function definition removes an extra function wrapper around every function. Thus, without them the time consumption should not differ at all from a normal function call.

        Appendix:
        # Note on deepcopying{.alert}
        As the event-object is tightly bounded to miniflask `deepcopy(event)` will not copy the whole internal miniflask state but only copy the view. This allows saving the `event` object as member inside any other class without the need to worry about deep copying the internal miniflask structure.  
        In case deep copying the event object including miniflasks internal state is a desired behavior use the follwing code snippet.
        ```python
        mfcopy = deepcopy(mf)
        eventcopy = mfcopy.event
        ```
        """  # noqa: W291

        if name not in self._mf.event_objs:
            if not self.optional_value:
                raise AttributeError("The Event '%s' has not been registered yet." % name)
            fn_wrap = self.make_dummy_fn(name, call_before_after=True)

        else:

            eobj = self._mf.event_objs[name]
            call_before_after = eobj.call_before_after

            # fn_wrap_scope creates a function wrap of fn that passes also state and event of eobj
            # additionally, if outervar is defined as a default, it queries that from the last outer scope
            def fn_wrap_scope(fn, _mf, _state, _event, module, needed_locals=None, miniflask_args=None, skip_twice=False, call_before_after=call_before_after):  # pylint: disable=too-many-statements
                del module  # unused
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
                name_before = 'before_' + name
                name_after = 'after_' + name
                has_before = name_before in self._mf.event_objs and call_before_after
                has_after = name_after in self._mf.event_objs and call_before_after
                fn_after = getattr(self._mf.event, name_after) if has_after else None
                fn_before = getattr(self._mf.event, name_before) if has_before else None

                # get index of "state" / "event"
                for i in range(min(len(arg_names), 3)):
                    for var, varname in [(_mf, "mf"), (_state, "state"), (_event, "event")]:
                        if arg_names[i] == varname:
                            miniflask_args.append(var)
                            break

                # if no outervar found, just pass state and event
                if len(needed_locals) > 0:
                    def fn_wrap(*args, altfn=None, **kwargs):
                        outer_locals = {}
                        if skip_twice:
                            all_outer_locals = inspect.currentframe().f_back.f_back.f_locals
                        else:
                            all_outer_locals = inspect.currentframe().f_back.f_locals
                        outer_locals = {k: all_outer_locals[k] for k in needed_locals if k not in kwargs}
                        if has_altfn:
                            kwargs["altfn"] = altfn
                        if has_before:
                            for fn_b in fn_before.subevents:
                                args, kwargs = fn_b(*args, **kwargs)
                        res = fn(*miniflask_args, *args, **outer_locals, **kwargs)
                        if has_after:
                            for fn_a in fn_after.subevents:
                                res, args, kwargs = fn_a(res, *args, **kwargs)
                        return res
                elif len(miniflask_args) > 0:
                    def fn_wrap(*args, altfn=None, **kwargs):
                        if has_altfn:
                            kwargs["altfn"] = altfn
                        if has_before:
                            for fn_b in fn_before.subevents:
                                args, kwargs = fn_b(*args, **kwargs)
                        res = fn(*miniflask_args, *args, **kwargs)
                        if has_after:
                            for fn_a in fn_after.subevents:
                                res, args, kwargs = fn_a(res, *args, **kwargs)
                        return res
                elif has_altfn or has_before or has_after:
                    def fn_wrap(*args, altfn=None, **kwargs):
                        if has_altfn:
                            kwargs["altfn"] = altfn
                        if has_before:
                            for fn_b in fn_before.subevents:
                                args, kwargs = fn_b(*args, **kwargs)
                        res = fn(*miniflask_args, *args, **kwargs)
                        if has_after:
                            for fn_a in fn_after.subevents:
                                res, args, kwargs = fn_a(res, *args, **kwargs)
                        return res
                else:
                    # it would be nice to let the user know, if the definition may be wrong at this point,
                    # however, we cannot know, if the call will contain the altfn-argument
                    # (up until we have a clean concept for this, we do not catch these definition errors)
                    # catching this would look like this:
                    # if not has_altfn and self.optional_value:
                    #     raise RegisterError(("The event %s was called using `event.optional(..., alftn=...)`, but the function does not catch this argument.\n\n"+fg('red')+"Possible Solutions:"+attr('reset')+"\n  - add `**kwargs` or `altfn=None` to your event-function definition.\n  - Alternatively, add either `event` or `state` or both to the event-function definition. In that case miniflask can catch altfn itself, however, this may adversely affect performance if this function is callled often.") % (fg('red')+name+attr('reset')))

                    # in case before_ or after_ events are registered, wrap the function as well
                    return fn, has_signature, miniflask_args
                return fn_wrap, has_signature, miniflask_args

            if eobj.unique:
                fn_wrap, has_signature, mf_args = fn_wrap_scope(eobj.fn, eobj.modules, eobj.modules.state, eobj.modules.event, eobj.modules)
                if has_signature:
                    setattr(fn_wrap, 'mf_modules', [eobj.modules.module_id])
                    setattr(fn_wrap, 'subevents', [fn_wrap])
                    setattr(fn_wrap, 'fns', [eobj.fn])
                    setattr(fn_wrap, 'fns_args', [mf_args])
            else:
                def multiple_fn_wrap_scope(orig_fns, modules=eobj.modules):
                    fns, have_signature, mf_args = zip(*[fn_wrap_scope(fn, _mf=module, _state=module.state, _event=module.event, module=module, skip_twice=True) for fn, module in zip(orig_fns, modules)])

                    def fn_wrap(*args, altfn=None, **kwargs):
                        del altfn  # unused
                        results = []
                        for fn in fns:
                            results.append(fn(*args, **kwargs))
                        return results

                    return fn_wrap, fns, have_signature, mf_args

                fn_wrap, fns, have_signature, mf_args = multiple_fn_wrap_scope(eobj.fn)
                setattr(fn_wrap, 'mf_modules', [m.module_id for m, has_sig in zip(eobj.modules, have_signature) if has_sig])
                setattr(fn_wrap, 'subevents', [fn for fn, has_sig in zip(fns, have_signature) if has_sig])
                setattr(fn_wrap, 'fns', eobj.fn)
                setattr(fn_wrap, 'fns_args', [mf_args])

        setattr(self, name, fn_wrap)
        return fn_wrap

    # disables deepcopy(event), as it is tightly bounded to other miniflask objects
    def __deepcopy__(self, memo):
        del memo
        return self

    def outervar(self):  # pylint: disable=no-self-use
        r"""!outervar
        For debbuging mainly: Changing the variables an event is called with.

        Event-Functions are called with a fixed number of variables.
        This function permits the called event to specify which variables it shall be called with from the caller.

        **Note**: This changes the way one typicalle constructs programs. This feature is intended to be a quick way to test architectural changes without changing the rest of the code. Thus, the typical used case is and should be only: **debugging**.

        ### Performance Note {.alert}
        To enable such a feature, we use python's inspection module. In every call that implys outervar variables we inspect the variable scope of the caller for the queried variables.
        """
        return outervar
