
def dataset(state, event):
    return "imagenet"


def register(mf):
    mf.register_event("dataset", dataset, unique=True)
