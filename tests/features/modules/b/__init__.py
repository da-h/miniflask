
def test(state):
    del state  # unused
    print("test")


def main(state, event):
    del state  # unused
    print(event.test.mf_modules)
    print(event.test.fns)
    print(event["modules.a"])
    print(event.optional["modules.a"])


def register(mf):
    mf.register_defaults({"test_b": 42})
    mf.register_event('test', test, unique=False)
    mf.register_event('main', main)
