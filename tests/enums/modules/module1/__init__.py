from enum import Enum


class SIZE(Enum):
    # The integer values define their order in a tensor
    SMALL = 0
    MEDIUM = 1
    LARGE = 2


def main(state, event):
    del event  # unused
    print("size :", state["size"].name)
    print("sizerequired:", state["sizerequired"].name)
    print("sizelist:", str(" ".join(s.name for s in state["sizelist"])))


def register(mf):
    mf.register_defaults({
        "sizerequired": SIZE,
        "size": SIZE.SMALL,
        "sizelist": [SIZE],
    })
    mf.register_event('main', main)
