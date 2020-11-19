
def loop(state, event):
    for i in range(state["epoch"]):
        print("Epoch " + str(i + 1))
        for b in event.dataloader():
            print(b)


def register(mf):
    defaults = {
        "epoch": 2
    }
    mf.register_defaults(defaults)
    mf.register_event("main", loop)
