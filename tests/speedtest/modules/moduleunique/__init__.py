def func(state, event, x):
    del state, event  # unused
    return x


def before_func(state, event, *args, **kwargs):
    del state, event  # unused
    return args, kwargs


def register(mf):
    mf.register_event('func', func, unique=True, call_before_after=True)
    mf.register_event('before_func', before_func)
