
def print_all(state):
    val = state["helpervar"]
    print("%s:" % state.fuzzy_names["helpervar"], val)


def register(mf):
    mf.register_helpers({
        "helpervar": 1
    })
    mf.register_event('print_all', print_all, unique=False)
