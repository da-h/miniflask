def func(x):
    return x

def register(mf):
    mf.register_event('func', func, unique=True)