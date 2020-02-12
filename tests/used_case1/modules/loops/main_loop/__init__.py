import module3

def loop(state, event):
    for i in range(state["num_runs"]):
        print(i)
    print(event.dataset())

def register(mf):
    defaults = {
        "num_runs": 42
    }
    mf.register_defaults(defaults)
    mf.register_event("main", loop, unique=True)
