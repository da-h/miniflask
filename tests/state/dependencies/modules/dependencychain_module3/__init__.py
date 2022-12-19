

def register(mf):
    mf.register_defaults({
        "foo1": lambda: 101,
        "foo2": lambda: 200,
        "foo3": lambda: 300,
        "foo4": lambda: 400,
        "foo5": lambda state: 12 * state["..dependencychain_module4.foo5"] if "..dependencychain_module4.foo5" in state else (state["..dependencychain_module1.foo3"] // 100),
    })
