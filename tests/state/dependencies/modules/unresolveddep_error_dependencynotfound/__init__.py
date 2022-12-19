
def register(mf):
    mf.register_defaults({
        "foo": lambda state: state["varnotfound"],
    })
