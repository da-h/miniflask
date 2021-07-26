from miniflask import outervar


def before_main(*args, var_a=outervar, **kwargs):
    print("before_main")
    print("outervar:", var_a)
    return args, kwargs


def main(event):
    del event
    print("main")


def register(mf):
    mf.register_event('before_main', before_main, unique=False)
    mf.register_event('main', main)
