

def getvalue(state):
    return state["42"]


def somefunction(val):
    return val * 300 + 2


def var1_fn(state):
    return 42


def var2_fn(state):
    return state["var1"]


def var3_fn(state):
    return state['var2'] + state['var1']


def var4_fn(state):
    return somefunction(state["var1"] + 1) * 5


def var5_fn(state):
    return somefunction(state["var1"] + 1) * 5 if "var1" in state else state["var3"]


def var6_fn(state):
    return somefunction(state['var1'] + state["var2"]) * 5 if 'var1' in state and "var2" in state else state['var3'] + state["var4"]


def register(mf):
    mf.register_defaults({
        "var1": var1_fn,
        "var2": var2_fn,
        "var3": var3_fn,
        "var4": var4_fn,
        "var5": var5_fn,
        "var6": var6_fn,
    })
