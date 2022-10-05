from miniflask import like


def main(state):
    print("foo:", state["foo"])
    print("foo2:", state["foo2"])
    print("foo3:", state["foo3"])
    print("foo4:", state["foo4"])


def register(mf):
    mf.register_defaults({
        "foo": like("bar", 0),
        "foo2": like("bar2", 1),
        "foo3": like("bar3", 1),
        "foo4": like("bar4", 4)
    })
    mf.register_event('main', main, unique=False)
