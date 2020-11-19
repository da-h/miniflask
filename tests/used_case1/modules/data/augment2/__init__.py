from random import randrange


def augment(state, event, ds):
    del state, event  # unused
    d = list(ds)
    i = randrange(0, len(d))
    d[i] = "·"
    return "".join(d)


def register(mf):
    mf.register_defaults({
        "remove": "a"
    })
    mf.register_event("dataset_augment", augment, unique=True)
