
# note that this function does not ask for any miniflask variables (state/event/mf)
def dosomething():
    print("event called")


def before_dosomething(*args, **kwargs):
    print("before_-event called")
    return args, kwargs


def after_dosomething(res, *args, **kwargs):
    print("after_-event called")
    return res, args, kwargs


def main(event):
    event.dosomething()


def register(mf):
    mf.register_event('dosomething', dosomething)
    mf.register_event('before_dosomething', before_dosomething)
    mf.register_event('after_dosomething', after_dosomething)
    mf.register_event('main', main)
