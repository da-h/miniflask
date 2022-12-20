
def test():
    print("test")


def main(event):
    event.test()
    print(event._data["test"]["modules"])
    print(event._data["test"]["raw_functions"])
    print(event["modules.a"])
    print(event.optional["modules.a"])


def register(mf):
    mf.register_defaults({"test_b": 42})
    mf.register_event('test', test, unique=False)
    mf.register_event('main', main, unique=False)
