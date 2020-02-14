
def augment(state, event, ds):
    return state["data.augment.fn"]+"("+ds+")"

def register(mf):
    mf.register_defaults({
        "fn": "transform"
    })
    mf.register_event("dataset_augment", augment, unique=True)
