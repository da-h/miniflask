
def printVal(state, name):
    val = state[name]
    print("%s:" % state.fuzzy_names[name], val)


def print_all(state):
    printVal(state, "var_default")
    printVal(state, "var_default_override")
    printVal(state, "var_default_override_twice")
    printVal(state, "var_default_override_twice_and_cli")


def register(mf):
    mf.register_defaults({
        "var_default": 1,
        "var_default_override": 2,
        "var_default_override_twice": 3,
        "var_default_override_twice_and_cli": 4
    })
    mf.register_event('print_all', print_all, unique=False)
