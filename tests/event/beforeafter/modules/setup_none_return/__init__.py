
# note that this function does not ask for any miniflask variables (state/event/mf)
def dosomething(val):
    print("event called with value: %i" % val)


def main(event):
    out = event.dosomething(42)
    print("event returned value: %s" % str(out))


def register(mf):
    mf.register_event('dosomething', dosomething)
    mf.register_event('main', main)
