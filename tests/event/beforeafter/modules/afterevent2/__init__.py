
def after_dosomething_as_well(event):
    print("after_-event (2) called")
    event.hook["result"] += 1


def register(mf):
    mf.register_event('after_dosomething', after_dosomething_as_well, unique=False)
