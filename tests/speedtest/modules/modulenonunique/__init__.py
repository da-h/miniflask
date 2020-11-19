def func(state, event, x):
    del state, event  # unused
    return x


def register(mf):
    mf.register_event('func', func, unique=False)
