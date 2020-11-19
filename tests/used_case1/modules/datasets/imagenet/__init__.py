
def dataset(state, event):
    del state, event  # unused
    return "imagenet"


def register(mf):
    mf.register_event("dataset", dataset, unique=True)
