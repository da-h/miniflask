def func(x, **kwargs):
    del kwargs  # unused
    return x


def register(mf):
    mf.register_event('func', func, unique=True)
