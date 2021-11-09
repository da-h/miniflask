from ..module1 import SIZE  # noqa: E0401


def main(state, event):
    del event  # unused
    if state["size"] not in list(SIZE):
        raise ValueError("Enums do not match.")


def register(mf):
    mf.load("module1")
    mf.register_event('main', main, unique=False)
