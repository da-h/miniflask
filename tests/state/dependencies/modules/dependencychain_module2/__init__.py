

def somefunction(value):
    return value + 1


def register(mf):
    mf.register_defaults({
        "foo1": lambda: 100,
        "foo2": lambda state: state["..dependencychain_module3.foo2"],
        "foo3": lambda state: state["..dependencychain_module3.foo3"],
        "foo4": lambda state: somefunction(state["..dependencychain_module3.foo4"])**5 + state["foo1"],
        "foo5": lambda state: state["..dependencychain_module3.foo5"],
    })
