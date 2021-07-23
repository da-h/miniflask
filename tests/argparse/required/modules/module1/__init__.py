from enum import Enum


class SIZE(Enum):
    SMALL = 0
    MEDIUM = 1
    LARGE = 2


def print_all(state):
    print("int1:", state["int1"])
    print("int2:", state["int2"])
    print("float1:", state["float1"])
    print("float2:", state["float2"])
    print("float3:", state["float3"])
    print("float4:", state["float4"])
    print("float5:", state["float5"])
    print("float6:", state["float6"])
    print("bool1:", state["bool1"])
    print("bool2:", state["bool2"])
    print("enum1:", state["enum1"])
    print("str1:", state["str1"])
    print("str2:", state["str2"])
    print("str3:", state["str3"])


def print_bool(state):
    print("bool1:", state["bool1"])
    print("bool2:", state["bool2"])


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
    })
    mf.register_event('print_all', print_all, unique=False)
    mf.register_event('print_bool', print_bool, unique=False)
