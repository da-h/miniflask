
def test(i):
    print("test", i)


def add_test(mf):
    def add_test_print(i):
        print("added to test", i)
    mf.register_event("test", add_test_print, unique=False)


def main(event):
    event.test(0)
    event.add_test()
    event.test(1)


def register(mf):
    mf.register_event("test", test, unique=False)
    mf.register_event("add_test", add_test, unique=False)
    mf.register_event("main", main, unique=False)
