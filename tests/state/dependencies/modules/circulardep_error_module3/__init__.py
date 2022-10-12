

def register(mf):
    mf.register_defaults({
        "foo": lambda state: state["..circulardep_error_module1.foo"],
        "bar": lambda state: state["bar2"],
        "bar2": lambda state: state["..circulardep_error_module2.bar2"]
    })
