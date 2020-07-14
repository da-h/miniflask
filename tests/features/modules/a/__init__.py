
def test():
    print("test")

def main(state, event):
    print(event.test.modules)
    print(event.test.fns)
    print(event["modules.a"])
    print(event.optional["modules.a"])
    print(event.optional.test())
    # print(event.optional.test(altfn=lambda x:x))

def register(mf):
    mf.load_as_child('b')
    mf.register_defaults({"test":42})
    mf.register_event('test', test, unique=True)
    mf.register_event('main', main)
