
def dosomething(state, event):
    print("in event", state["variable"])

def main(state, event):

    print("before event", state["variable"])
    with state.temporary({
        "variable": 42
    }):
        event.dosomething()
    print("after event", state["variable"])

def register(mf):
    mf.register_defaults({
        "variable": 0
    })
    mf.register_event('dosomething',dosomething)
    mf.register_event('main',main)

