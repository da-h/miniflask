
def main(state):
    print("foo:", state["foo"])
    print("foo2:", state["foo2"])
    print("foo3:", state["foo3"])
    print("foo4:", state["foo4"])


def register(mf):
    mf.register_defaults({
        "foo": lambda state, event: state["bar"] if "bar" in state else 0,
        "foo2": lambda state, event: state["bar2"] if "bar2" in state else 1,
        "foo3": lambda state, event: state["bar3"] if "bar3" in state else 1,
        "foo4": lambda state, event: state["bar4"] if "bar4" in state else 4,
    })
    mf.register_event('main', main, unique=False)
