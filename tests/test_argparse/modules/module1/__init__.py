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
        "int1": 42,
        "int2": -42,
        "float1": 2.345,
        "float2": -2.345,
        "float3": 0.0,
        "float4": -0.0,
        "float5": 1e7,
        "float6": -1e7,
        "bool1": True,
        "bool2": False,
        "enum1": SIZE.MEDIUM,
        "str1": "",
        "str2": "abcd1234",
        "str3": "αβγδ∀⇐Γ∂",
    })
    mf.register_event('print_all', print_all)
    mf.register_event('print_bool', print_bool)
