

def getvalue(state):
    return state["42"]

def register(mf):
    mf.register_defaults({
        "foo": lambda: 42,
        "bar": lambda state: state["foo"] + 1,
        "foobar": lambda event: event.getvalue() + 2,
        "foobar2": lambda mf: mf.event.getvalue() + 3,
        "foofoobar": lambda state, event: (event.getvalue() + 2) * (state["foo"] + 1),
    })
