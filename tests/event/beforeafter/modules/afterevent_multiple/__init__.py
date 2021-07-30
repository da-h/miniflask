
def after_dosomething(event):
    print("after_-event called")
    for i, _ in enumerate(event.hook["result"]):
        event.hook["result"][i] *= i


def register(mf):
    mf.register_event('after_dosomething', after_dosomething, unique=False)
