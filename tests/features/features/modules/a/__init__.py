
def test():
    print("test")


def main(event):
    event.test()
    print(event._data["test"]["modules"])
    print(event._data["test"]["raw_functions"])
    print(event["modules.a"])
    print(event.optional["modules.a"])
    print(event.optional.test())


def register(mf):
    mf.load_as_child('b')
    mf.register_defaults({"test": 42})
    mf.register_event('test', test)
    mf.register_event('main', main, unique=False)
