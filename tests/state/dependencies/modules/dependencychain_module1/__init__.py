

def print_all(state):
    for k, v in state.all.items():
        if not k.startswith("modules."):
            continue
        print(k + ":", v)


def register(mf):
    mf.register_event("print_all", print_all)
    mf.register_defaults({
        "foo1": lambda state: state["..dependencychain_module2.foo1"],
        "foo2": lambda state: state["..dependencychain_module2.foo2"],
        "foo3": lambda state: 2 * state["..dependencychain_module2.foo3"],
        "foo4": lambda state: 3 * state["..dependencychain_module2.foo4"],
        "foo5": lambda state: 4 * state["..dependencychain_module2.foo5"],
    })
