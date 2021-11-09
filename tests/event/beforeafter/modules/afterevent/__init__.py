
def after_dosomething(event):
    print("after_-event called")
    if event.hook["result"] is None:
        return
    event.hook["result"] *= 2


def register(mf):
    mf.register_event('after_dosomething', after_dosomething, unique=False)
