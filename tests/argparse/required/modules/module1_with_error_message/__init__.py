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
        "int1": int,
        "int2": int,
        "float1": float,
        "float2": float,
        "float3": float,
        "float4": float,
        "float5": float,
        "float6": float,
        "bool1": bool,
        "bool2": bool,
        "enum1": SIZE,
        "str1": str,
        "str2": str,
        "str3": str,
    }, missing_argument_message="Did you forget something?")
    mf.register_event('print_all', print_all, unique=False)
    mf.register_event('print_bool', print_bool, unique=False)
