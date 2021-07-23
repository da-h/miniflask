
# note that this function does not ask for any miniflask variables (state/event/mf)
def dosomething(val):
    print("event called with value: %i" % val)
    return val


def main(event):
    print("event returned value: %i" % event.dosomething(42))


def register(mf):
    mf.register_event('dosomething', dosomething)
    mf.register_event('main', main)
