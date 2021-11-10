
def main():
    print("main event")


def before_main():
    print("before main event")


def after_main():
    print("after main event")


def register(mf):
    mf.register_event('main', main, unique=False)
    mf.register_event('before_main', before_main, unique=False)
    mf.register_event('after_main', after_main, unique=False)
