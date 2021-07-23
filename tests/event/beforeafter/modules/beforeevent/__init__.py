
def before_dosomething(event):
    print("before_-event called")
    event.hook["args"][0] *= 2


def register(mf):
    mf.register_event('before_dosomething', before_dosomething, unique=False)
