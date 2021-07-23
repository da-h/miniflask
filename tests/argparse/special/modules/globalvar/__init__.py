
def print_all(state):
    val = state["globalvar"]
    print("%s:" % state.fuzzy_names["globalvar"], val)


def register(mf):
    mf.register_globals({
        "globalvar": 1
    })
    mf.register_event('print_all', print_all, unique=False)
