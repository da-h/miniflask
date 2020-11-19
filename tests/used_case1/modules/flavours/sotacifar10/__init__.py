
def register(mf):
    mf.load(["cifar10", "batches", "main_loop", "augment"])
    defaults = {
        "num_runs": 2
    }
    mf.register_defaults(defaults)
