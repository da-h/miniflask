
def register(mf):
    mf.load(["cifar10","main_loop"])
    defaults = {
        "num_runs": 2
    }
    mf.register_defaults(defaults)

