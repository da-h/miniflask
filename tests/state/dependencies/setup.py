import miniflask  # noqa: E402


def printAll(state):
    for k in state.all:
        print(f"{k}:", state[k])


def setup():
    mf = miniflask.init(".modules")
    mf.register_event("main", printAll, unique=False)
    return mf
