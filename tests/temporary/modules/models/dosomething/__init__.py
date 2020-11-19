from miniflask.exceptions import StateKeyError


def dosomething(state, event):
    del event  # unused
    print("in event: variable =", state["variable"])
    if "new_variable" in state:
        print("in event: new_variable =", state["new_variable"])


def main(state, event):

    state["new_variable"] = 42
    del state["new_variable"]

    print("before event", state["variable"])
    with state.temporary({
        "variable": 42
    }):
        event.dosomething()
    print("after event", state["variable"])

    try:
        _ = state["new_variable"]
        print("variable 'new_variable' should not exist")
    except StateKeyError:
        pass
    with state.temporary({
        "new_variable": 12345
    }):
        event.dosomething()
    try:
        _ = state["new_variable"]
        print("variable 'new_variable' should not exist")
    except StateKeyError:
        pass


def register(mf):
    mf.register_defaults({
        "variable": 0
    })
    mf.register_event('dosomething', dosomething)
    mf.register_event('main', main)
