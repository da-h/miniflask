

def register(mf):
    mf.register_defaults({
        "foo": lambda state: state["..circulardep_error_module3.foo"],
        "bar": lambda state: state["..circulardep_error_module3.bar"],
        "bar2": lambda state: state["..circulardep_error_module1.bar2"]
    })
