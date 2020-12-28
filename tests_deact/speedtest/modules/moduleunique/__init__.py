def func(state, event, x):
    del state, event  # unused
    return x


def before_func(state, event, *args, **kwargs):
    del state, event  # unused
    return args, kwargs


def get_state_var(state, varname):
    return state[varname]


def register(mf):
    mf.register_event('func', func, unique=True, call_before_after=True)
    mf.register_event('before_func', before_func)
    mf.register_event('get_state_var', get_state_var, unique=True)
    mf.register_defaults({
        "a": 42
    })
