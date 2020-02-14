
def dataset(state, event):
    return "cifar10"

def register(mf):
    mf.register_event("dataset", dataset, unique=True)
