
def after_dosomething(event):
    print("after_-event called")
    event.hook["result"] *= 2


def register(mf):
    mf.register_event('after_dosomething', after_dosomething, unique=False)
