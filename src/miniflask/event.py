import inspect
from typing import Callable, List
from dataclasses import dataclass


class outervar:  # pylint: disable=too-few-public-methods
    pass


class no_result_given:  # pylint: disable=too-few-public-methods
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
        self.hook = {}
        self._data = mf.event_data
        super().__init__()

    def make_dummy_fn(self, name, call_before_after=True):  # noqa: C901 too-complex  pylint: disable=too-many-statements
        # automatic before/after events
        name_before = 'before_' + name
        name_after = 'after_' + name
        has_before = name_before in self._mf.event_objs and call_before_after
        has_after = name_after in self._mf.event_objs and call_before_after

        # ensure attached events are created
        if has_before:
            getattr(self._mf.event, name_before)
        if has_after:
            getattr(self._mf.event, name_after)

        def dummy_fn(*args, altfn=None, _event_overwrite=None, **kwargs):
            if callable(altfn):

                # call before_-event functions
                if has_before:
                    for fn_b in self._data[name_before]["wrapped_single_events"]:
                        if fn_b.needs_event_obj:
                            event_call = eventCall(self, name, args, kwargs)
                            fn_b(_event_overwrite=event_call)
                            args, kwargs = event_call.hook["args"], event_call.hook["kwargs"]
                        else:
                            fn_b()

                # actual function call
                result = altfn(*args, **kwargs)

                # call after_-event functions
                if has_after:
                    for fn_a in self._data[name_after]["wrapped_single_events"]:
                        if fn_a.needs_event_obj:
                            event_call = eventCall(self, name, args, kwargs, result=result)
                            fn_a(_event_overwrite=event_call)
                            result, args, kwargs = event_call.hook["result"], event_call.hook["args"], event_call.hook["kwargs"]
                        else:
                            fn_a()

                return result
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

        # Internal Event Data
        The `event` object contains a hidden `_data` dictionary that saves the information needed to construct the events from the actual code.
        In more detail:
        - `event._data[eventname]` contains the dictionary with all information required to construct the events
        - `event._data[eventname]["modules"]`: list of modules that define the event `eventname`
        - `event._data[eventname]["wrapped_event"]`: symlink to `event.eventname`
        - `event._data[eventname]["wrapped_single_events"]`: list of all wrapped events in case of non-unique event `eventname`
        - `event._data[eventname]["raw_functions"]`: list of all raw functions (as defined in code) in the modules given above (same order as in the modules list)
        - `event._data[eventname]["raw_function_args"]`: the `mf`, `state` and `event` objects arguments needed for the raw functions

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
        if name == "optional" and self.optional_value:
            return self
        if name not in self._mf.event_objs:
            if not self.optional_value:
                raise AttributeError("The Event '%s' has not been registered yet." % name)
            fn_wrap = self.make_dummy_fn(name, call_before_after=True)
            modules_of_single_events = ["dummy-module"]
            wrapped_single_events = [fn_wrap]
            raw_events = [lambda:[]]
            mf_args = []

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
                miniflask_args_event_i = -1

                # ensure attached events are created
                if has_before:
                    getattr(self._mf.event, name_before)
                if has_after:
                    getattr(self._mf.event, name_after)

                # get index of "state" / "event"
                for i in range(min(len(arg_names), 3)):
                    for var, varname in [(_mf, "mf"), (_state, "state"), (_event, "event")]:
                        if arg_names[i] == varname:

                            # remember event id (as this may need to get replaced later)
                            if varname == "event":
                                miniflask_args_event_i = len(miniflask_args)

                            # save miniflask_args list so that these can be passed automatically to the function
                            miniflask_args.append(var)
                            break

                # if no outervar found, just pass state and event
                if len(needed_locals) > 0:
                    def fn_wrap(*args, altfn=None, _event_overwrite=None, **kwargs):
                        outer_locals = {}
                        if skip_twice:
                            all_outer_locals = inspect.currentframe().f_back.f_back.f_locals
                        else:
                            all_outer_locals = inspect.currentframe().f_back.f_locals
                        outer_locals = {k: all_outer_locals[k] for k in needed_locals if k not in kwargs}
                        if has_altfn:
                            kwargs["altfn"] = altfn

                        # call before_-event functions
                        if has_before:
                            for fn_b in self._data[name_before]["wrapped_single_events"]:
                                if fn_b.needs_event_obj:
                                    event_call = eventCall(self, name, args, kwargs)
                                    fn_b(_event_overwrite=event_call)
                                    args, kwargs = event_call.hook["args"], event_call.hook["kwargs"]
                                else:
                                    fn_b()

                        # replace event-overwrite if required
                        if _event_overwrite is not None:
                            _miniflask_args = miniflask_args[:miniflask_args_event_i] + [_event_overwrite] + miniflask_args[miniflask_args_event_i + 1:]
                        else:
                            _miniflask_args = miniflask_args

                        # actual function call
                        result = fn(*_miniflask_args, *args, **outer_locals, **kwargs)

                        # call after_-event functions
                        if has_after:
                            for fn_a in self._data[name_after]["wrapped_single_events"]:
                                if fn_a.needs_event_obj:
                                    event_call = eventCall(self, name, args, kwargs, result=result)
                                    fn_a(_event_overwrite=event_call)
                                    result, args, kwargs = event_call.hook["result"], event_call.hook["args"], event_call.hook["kwargs"]
                                else:
                                    fn_a()
                        return result

                # wrap so that event/state/mf objects can be passed automatically on every call
                elif len(miniflask_args) > 0:
                    def fn_wrap(*args, altfn=None, _event_overwrite=None, **kwargs):
                        if has_altfn:
                            kwargs["altfn"] = altfn

                        # call before_-event functions
                        if has_before:
                            for fn_b in self._data[name_before]["wrapped_single_events"]:
                                if fn_b.needs_event_obj:
                                    event_call = eventCall(self, name, args, kwargs)
                                    fn_b(_event_overwrite=event_call)
                                    args, kwargs = event_call.hook["args"], event_call.hook["kwargs"]
                                else:
                                    fn_b()

                        # replace event-overwrite if required
                        if _event_overwrite is not None:
                            _miniflask_args = miniflask_args[:miniflask_args_event_i] + [_event_overwrite] + miniflask_args[miniflask_args_event_i + 1:]
                        else:
                            _miniflask_args = miniflask_args

                        # actual function call
                        result = fn(*_miniflask_args, *args, **kwargs)

                        # call after_-event functions
                        if has_after:
                            for fn_a in self._data[name_after]["wrapped_single_events"]:
                                if fn_a.needs_event_obj:
                                    event_call = eventCall(self, name, args, kwargs, result=result)
                                    fn_a(_event_overwrite=event_call)
                                    result, args, kwargs = event_call.hook["result"], event_call.hook["args"], event_call.hook["kwargs"]
                                else:
                                    fn_a()
                        return result

                # in case before_ or after_ events are registered, wrap the function as well
                elif has_altfn or has_before or has_after:
                    def fn_wrap(*args, altfn=None, _event_overwrite=None, **kwargs):

                        # as no miniflask_args are queried, there cannot be any _event_overwrite-query
                        del _event_overwrite

                        if has_altfn:
                            kwargs["altfn"] = altfn

                        # call before_-event functions
                        if has_before:
                            for fn_b in self._data[name_before]["wrapped_single_events"]:
                                if fn_b.needs_event_obj:
                                    event_call = eventCall(self, name, args, kwargs)
                                    fn_b(_event_overwrite=event_call)
                                    args, kwargs = event_call.hook["args"], event_call.hook["kwargs"]
                                else:
                                    fn_b()

                        # actual function call
                        result = fn(*args, **kwargs)

                        # call after_-event functions
                        if has_after:
                            for fn_a in self._data[name_after]["wrapped_single_events"]:
                                if fn_a.needs_event_obj:
                                    event_call = eventCall(self, name, args, kwargs, result=result)
                                    fn_a(_event_overwrite=event_call)
                                    result, args, kwargs = event_call.hook["result"], event_call.hook["args"], event_call.hook["kwargs"]
                                else:
                                    fn_a()

                        return result

                # no need to wrap if no miniflask features are used
                else:
                    # it would be nice to let the user know, if the definition may be wrong at this point,
                    # however, we cannot know, if the call will contain the altfn-argument
                    # (up until we have a clean concept for this, we do not catch these definition errors)
                    # catching this would look like this:
                    # if not has_altfn and self.optional_value:
                    #     raise RegisterError(("The event %s was called using `event.optional(..., alftn=...)`, but the function does not catch this argument.\n\n"+fg('red')+"Possible Solutions:"+attr('reset')+"\n  - add `**kwargs` or `altfn=None` to your event-function definition.\n  - Alternatively, add either `event` or `state` or both to the event-function definition. In that case miniflask can catch altfn itself, however, this may adversely affect performance if this function is callled often.") % (fg('red')+name+attr('reset')))

                    fn_wrap = fn

                # save argument names
                fn_wrap.arg_names = arg_names
                fn_wrap.needs_event_obj = miniflask_args_event_i >= 0

                return fn_wrap, has_signature, miniflask_args

            if eobj.unique:
                fn_wrap, has_signature, mf_args = fn_wrap_scope(eobj.fn, eobj.modules, eobj.modules.state, eobj.modules.event, eobj.modules)
                if has_signature:
                    modules_of_single_events = [eobj.modules.module_id]
                    wrapped_single_events = [fn_wrap]
                    raw_events = [eobj.fn]
            else:
                def multiple_fn_wrap_scope(orig_fns, modules=eobj.modules):
                    fns, have_signature, mf_args = zip(*[fn_wrap_scope(fn, _mf=module, _state=module.state, _event=module.event, module=module, skip_twice=True, call_before_after=False) for fn, module in zip(orig_fns, modules)])

                    # automatic before/after events
                    name_before = 'before_' + name
                    name_after = 'after_' + name
                    has_before = name_before in self._mf.event_objs and call_before_after
                    has_after = name_after in self._mf.event_objs and call_before_after

                    # ensure attached events are created
                    if has_before:
                        getattr(self._mf.event, name_before)
                    if has_after:
                        getattr(self._mf.event, name_after)

                    def fn_wrap(*args, altfn=None, **kwargs):
                        del altfn  # unused

                        # call before_-event functions
                        if has_before:
                            for fn_b in self._data[name_before]["wrapped_single_events"]:
                                if fn_b.needs_event_obj:
                                    event_call = eventCall(self, name, args, kwargs)
                                    fn_b(_event_overwrite=event_call)
                                    args, kwargs = event_call.hook["args"], event_call.hook["kwargs"]
                                else:
                                    fn_b()

                        # actual function call
                        results = []
                        for fn in fns:
                            results.append(fn(*args, **kwargs))

                        # call after_-event functions
                        if has_after:
                            for fn_a in self._data[name_after]["wrapped_single_events"]:
                                if fn_a.needs_event_obj:
                                    event_call = eventCall(self, name, args, kwargs, result=results)
                                    fn_a(_event_overwrite=event_call)
                                    results, args, kwargs = event_call.hook["result"], event_call.hook["args"], event_call.hook["kwargs"]
                                else:
                                    fn_a()

                        return results

                    return fn_wrap, fns, have_signature, mf_args

                fn_wrap, fns, have_signature, mf_args = multiple_fn_wrap_scope(eobj.fn)
                modules_of_single_events = [m.module_id for m, has_sig in zip(eobj.modules, have_signature) if has_sig]
                wrapped_single_events = [fn for fn, has_sig in zip(fns, have_signature) if has_sig]
                raw_events = eobj.fn

        self._data[name] = {
            "modules": modules_of_single_events,
            "wrapped_event": fn_wrap,
            "wrapped_single_events": wrapped_single_events,
            "raw_function_args": mf_args,
            "raw_functions": raw_events,
        }
        setattr(self, name, fn_wrap)
        return fn_wrap

    def named_call(self, event_name, *args, **kwargs):
        r"""
        Retrieve the names of the modules together with the results.

        **Note**:
        Can be combined with `event.optional` functionality to return an empty dict if the event has not been registered, yet.

        Args:
        - `event_name`: (required)  
            Event to be called.
        - `*args`, `**kwargs`:  
            Arguments to be passed to the event call.

        Examples:
        ```python
        for module_id, result in event.named_call('myevent', the_argument=42):
            print(f"Module with id {module_id} has returned", result)
        ```
        """  # noqa: W291
        eobj = self._mf.event_objs[event_name]
        results = getattr(self, event_name)(*args, **kwargs)
        if eobj.unique:
            results = [results]
        return dict(zip(self._data[event_name]["modules"], results))

    def exists(self, event_name):
        r"""
        Check if an event has been registered.

        Args:
        - `event_name`: (required)  
            Eventname to check.

        Examples:
        ```python
        if event.exists('to_be_called'):
            event.to_be_called()
        ```
        """  # noqa: W291
        return event_name in self._mf.event_objs

    # disables deepcopy(event), as it is tightly bounded to other miniflask objects
    def __deepcopy__(self, memo):
        del memo
        return self

    def outervar(self):
        r"""!outervar
        For debbuging mainly: Changing the variables an event is called with.

        Event-Functions are called with a fixed number of variables.
        This function permits the called event to specify which variables it shall be called with from the caller.

        **Note**: This changes the way one typicalle constructs programs. This feature is intended to be a quick way to test architectural changes without changing the rest of the code. Thus, the typical used case is and should be only: **debugging**.

        ### Performance Note {.alert}
        To enable such a feature, we use python's inspection module. In every call that implys outervar variables we inspect the variable scope of the caller for the queried variables.
        """
        return outervar


# this event object is used for every call of before_/after_ events to simplify their call api
class eventCall:  # pylint: disable=R0903 (too-few-public-methods)

    def __init__(self, ev, fn_name, args, kwargs, result=no_result_given):
        self._ev = ev
        self.hook = {
            "name": fn_name,
            "args": list(args),
            "kwargs": kwargs
        }
        if result is not no_result_given:
            self.hook["result"] = result

    def __getattr__(self, name):
        return getattr(self._ev, name)
