from enum import Enum
from miniflask import optional


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
        "int1": optional(int),
        "int2": optional(int),
        "float1": optional(float),
        "float2": optional(float),
        "float3": optional(float),
        "float4": optional(float),
        "float5": optional(float),
        "float6": optional(float),
        "bool1": optional(bool),
        "bool2": optional(bool),
        "enum1": optional(SIZE),
        "str1": optional(str),
        "str2": optional(str),
        "str3": optional(str),
    })
    mf.register_event('print_all', print_all, unique=False)
    mf.register_event('print_bool', print_bool, unique=False)
