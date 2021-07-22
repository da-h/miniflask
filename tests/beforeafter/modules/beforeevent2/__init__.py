
def before_dosomething_as_well(event):
    print("before_-event (2) called")
    event.hook["args"][0] += 1


def register(mf):
    mf.register_event('before_dosomething', before_dosomething_as_well, unique=False)
