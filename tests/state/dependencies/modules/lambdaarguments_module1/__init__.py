def getvalue(state):
    return state["42"]


def some_function(val):
    return val * 300 + 2


class TestClass:  # pylint: disable=too-few-public-methods

    def __init__(self, state):
        self.state = state


lambda_definition = lambda: 42  # noqa  # pylint: disable=unnecessary-lambda-assignment


def register(mf):
    mf.register_defaults({
        "emptydependency": lambda state: state["doesntexists"] if "doesntexists" in state else "cpu",
        "multilevelindex": lambda state: "cuda:" + str(state["gpu"][0]) if state["gpu"][0] >= 0 else "cpu",
        "multileveltag": lambda state: state["var1"]["other"],
        "test_multiple_inline_I": lambda: 1 * 42,
        "test_multiple_inline_II": lambda: 2 * 42,
        "test_lambda_def": lambda_definition,
        "test_class": TestClass,
        "test_line_breaks": lambda state: state[
            "var1"
        ],
        "test_not_cmp": lambda state: some_function(state["var1"] + 1) * 5 if "var3" not in state and "var3" not in state else state["var3"],
        "var1": lambda: 42,
        "var2": lambda state: state["var1"],
        "var3": lambda state: state['var2'] + state['var1'],
        "var4": lambda state: some_function(state["var1"] + 1) * 5,
        "var5": lambda state: some_function(state["var1"] + 1) * 5 if "var1" in state else state["var3"],
        "var6": lambda state: some_function(state['var1'] + state["var2"]) * 5 if 'var1' in state and "var2" in state else state['var3'] + state["var4"],
    })
