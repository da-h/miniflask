
def dataset(state, event):
    return "the_fabulous_cifar10_dataset"

def register(mf):
    mf.register_helpers({
        "num_data": 24
    })
    mf.register_event("dataset", dataset, unique=True)
