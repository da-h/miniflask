
# note that this function does not ask for any miniflask variables (state/event/mf)
def dosomething():
    print("event called")


def before_dosomething():
    print("before_-event called")


def after_dosomething():
    print("after_-event called")


def main(event):
    event.dosomething()


def register(mf):
    mf.register_event('dosomething', dosomething, unique=False)
    mf.register_event('before_dosomething', before_dosomething, unique=False)
    mf.register_event('after_dosomething', after_dosomething, unique=False)
    mf.register_event('main', main, unique=False)
