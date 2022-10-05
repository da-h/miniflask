
def register(mf):
    mf.register_defaults({
        "bar": 11,
        "bar2": lambda state, event: state["foobar2"] if "foobar2" in state else 12,
        "bar3": lambda state, event: state["foobar3"] if "foobar3" in state else 13,
    })
