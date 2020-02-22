def func(state, event, x):
    return x

def register(mf):
    mf.register_event('func', func, unique=False)
