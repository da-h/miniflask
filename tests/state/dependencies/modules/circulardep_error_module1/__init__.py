
def register(mf):
    mf.register_defaults({
        "foo": lambda state: state["..circulardep_error_module2.foo"],
        "bar": lambda state: state["..circulardep_error_module2.bar"],
        "bar2": lambda state: state["..circulardep_error_module3.bar2"]
    })
