
def augment(state, event, ds):
    del event  # unused
    return [state["fn"] + "("] + ds + [")"]


def register(mf):
    mf.register_defaults({
        "fn": "transform"
    })
    mf.register_event("dataset_augment", augment, unique=True)
