from random import randrange


def augment(ds):
    d = list(ds)
    i = randrange(0, len(d))
    d[i] = "·"
    return "".join(d)


def register(mf):
    mf.register_defaults({
        "remove": "a"
    })
    mf.register_event("dataset_augment", augment)
