

# define how to transform data when initializing a unit
def init_time_unit(data):
    units = list(data.keys())
    assert len(units) == 1, f"Unitvalue should contain exactly one data point, but found {units}."
    unit = units[0]
    value = list(data.values())[0]
    data = {"computation_list": []}
    if unit == "m":
        return {"s": 60 * value, **data}
    if unit == "h":
        return {"s": 60 * 60 * value, **data}
    if unit == "d":
        return {"s": 24 * 60 * 60 * value, **data}
    raise ValueError(f"Could not determine initial values from {repr(data)}.")


def get_time_unit(unitvalue, targetunit):

    # we use seconds as base unit und convert any start to that value
    if "s" not in unitvalue.data:
        unitvalue.data = init_time_unit(unitvalue.data)

    unitvalue.data["computation_list"].append(targetunit)

    if targetunit == "s":
        return unitvalue.data["s"]
    if targetunit == "m":
        return unitvalue.data["s"] / 60
    if targetunit == "h":
        return unitvalue.data["s"] / 60 / 60
    if targetunit == "d":
        return unitvalue.data["s"] / 60 / 60 / 24

    raise ValueError(f"Could not query {targetunit} from {repr(unitvalue)}")


def set_time_unit(unitvalue, targetunit, newvalue):

    # we use seconds as base unit und convert any start to that value
    if "s" not in unitvalue.data:
        unitvalue.data = init_time_unit(unitvalue.data)

    unitvalue.data["computation_list"].append(targetunit)

    if targetunit == "s":
        unitvalue.data["s"] += newvalue
        return
    if targetunit == "m":
        unitvalue.data["s"] += 60 * newvalue
        return
    if targetunit == "h":
        unitvalue.data["s"] += 60 * 60 * newvalue
        return
    if targetunit == "d":
        unitvalue.data["s"] += 24 * 60 * 60 * newvalue
        return

    raise ValueError(f"Could not query {targetunit} from {repr(unitvalue)}")


def register(mf):
    time = mf.register_unit("time", get_time_unit, set_time_unit, [
        ["m", "minute", "minutes"],
        ["h", "hour", "hours"],
        ["s", "second", "seconds"],
        ["d", "day", "days"]
    ])
    mf.register_defaults({
        "time": time(6.0, "h"),
        "time2": time(6.0, "d"),
    })
