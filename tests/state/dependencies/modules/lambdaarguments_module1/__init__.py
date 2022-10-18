

def getvalue(state):
    return state["42"]


def somefunction(val):
    return val * 300 + 2


def register(mf):
    mf.register_defaults({
        "var1": lambda: 42,
        "var2": lambda state: state["var1"],
        "var3": lambda state: state['var2'] + state['var1'],
        "var4": lambda state: somefunction(state["var1"] + 1) * 5,
        "var5": lambda state: somefunction(state["var1"] + 1) * 5 if "var1" in state else state["var3"],
        "var6": lambda state: somefunction(state['var1'] + state["var2"]) * 5 if 'var1' in state and "var2" in state else state['var3'] + state["var4"],
    })
