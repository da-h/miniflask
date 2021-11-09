
def after_dosomething(event):
    print("after_-event (2) called")
    if event.hook["result"] is None:
        return
    for i, _ in enumerate(event.hook["result"]):
        event.hook["result"][i] += (i + 1)


def register(mf):
    mf.register_event('after_dosomething', after_dosomething, unique=False)
