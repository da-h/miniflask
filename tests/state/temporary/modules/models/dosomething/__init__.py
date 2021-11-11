import pytest  # pylint: disable=import-error
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

    # Check if global state iterator has all variables that we expect
    assert len(state.all) == 4, "Found global Variables %i" % len(state.all)

    # Check if local state iterator has all variables that we expect
    assert len(state) == 1, "Found lokal Variables %i" % len(state)

    # Checking if variable can be temporarily overwritten
    with state.temporary({
        "variable": 42,
    }):
        assert len(state) == 1, "Found Variables %i" % len(state)
    print("after event", state["variable"])
    assert len(state) == 1, "Found Variables %i" % len(state)

    # Checking if variable can be temporarily defined
    with pytest.raises(StateKeyError):
        _ = state["new_variable"]
        print("variable 'new_variable' should not exist")
    with state.temporary({
        "new_variable": 12345
    }):
        assert len(state) == 2, "Found Variables %i" % len(state)
        event.dosomething()
    with pytest.raises(StateKeyError):
        _ = state["new_variable"]
        print("variable 'new_variable' should not exist")
    assert len(state) == 1, "Found Variables %i" % len(state)

    # Checking if iterating keys works as well
    assert ",".join(iter(state)) == "modules.models.dosomething.variable", "Found variables:" + ",".join(iter(state))
    with state.temporary({
        "variable2": 42,
        "variable3": 42,
        "variable4": 42
    }):
        assert ", ".join(iter(state)) == "modules.models.dosomething.variable, modules.models.dosomething.variable2, modules.models.dosomething.variable3, modules.models.dosomething.variable4", "Found variables:" + ", ".join(iter(state))
    print("after event", state["variable"])
    assert ",".join(iter(state)) == "modules.models.dosomething.variable", "Found variables:" + ",".join(iter(state))


def register(mf):
    mf.load("addingvariables")
    mf.register_defaults({
        "variable": 0
    })
    mf.register_event('dosomething', dosomething, unique=False)
    mf.register_event('main', main, unique=False)
