def func(state, event, x):
    return x


def before_func(state, event, *args, **kwargs):
    return args, kwargs


def register(mf):
    mf.register_event('func', func, unique=True, call_before_after=True)
    mf.register_event('before_func', before_func)
