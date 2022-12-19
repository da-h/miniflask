
def register(mf):
    mf.register_defaults({
        "foo": lambda state: state["foo"],
        "foo2": lambda state: state["foo2bar"],
        "foo2bar": lambda state: state["foo2"],
        "foo3": lambda state: state["foo3barbar"],
        "foo3bar": lambda state: state["foo3"],
        "foo3barbar": lambda state: state["foo3bar"]
    })
