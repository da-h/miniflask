
def dataset(state, event):
    print("this is cifar10")

def register(mf):

    defaults = {
        "num_runs": 42
    }
    mf.register_defaults(defaults)
    mf.register_event("dataset", dataset, unique=True)
