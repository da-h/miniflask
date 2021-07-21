
def dataset():
    return "imagenet"


def register(mf):
    mf.register_event("dataset", dataset)
