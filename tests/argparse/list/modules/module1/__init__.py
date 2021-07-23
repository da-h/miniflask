from enum import Enum


class SIZE(Enum):
    SMALL = 0
    MEDIUM = 1
    LARGE = 2


def printVal(state, name):
    val = state[name]
    print("%s:" % state.fuzzy_names[name], val)


def print_all(state):
    printVal(state, "int1")
    printVal(state, "int2")
    printVal(state, "float1")
    printVal(state, "float2")
    printVal(state, "float3")
    printVal(state, "float4")
    printVal(state, "float5")
    printVal(state, "float6")
    printVal(state, "bool1")
    printVal(state, "bool2")
    printVal(state, "enum1")
    printVal(state, "str1")
    printVal(state, "str2")
    printVal(state, "str3")


def print_bool(state):
    printVal(state, "bool1")
    printVal(state, "bool2")


def register(mf):
    mf.register_defaults({
        "int1": [42],
        "int2": [-42],
        "float1": [2.345],
        "float2": [-2.345],
        "float3": [0.0],
        "float4": [-0.0],
        "float5": [1e7],
        "float6": [-1e7],
        "bool1": [True],
        "bool2": [False],
        "enum1": [SIZE.MEDIUM],
        "str1": [""],
        "str2": ["abcd1234"],
        "str3": ["αβγδ∀⇐Γ∂"],
    })
    mf.register_event('print_all', print_all, unique=False)
    mf.register_event('print_bool', print_bool, unique=False)
