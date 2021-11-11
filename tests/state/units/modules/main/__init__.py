
def add50minutes(state):
    print("-------------")
    print("changing time")
    print("-------------")
    state["time"].minute += 50
    state["time2"].minute += 50


def main(state, event):
    print("time data", state["time"])
    print("--------------")
    print("time %.2f [minute]" % state["time"].minute)
    print("time %.2f [minute] (re-access)" % state["time"].minute)
    print("time %.2f [minute] (re-access)" % state["time"].minute)
    print("time %.2f [hour]" % state["time"].hour)
    print("time %.2f [hour] (re-access)" % state["time"].hour)
    print("time %.2f [second]" % state["time"].second)
    print("time %.2f [day]" % state["time"].day)
    print("time computation list %s" % ",".join(state["time"].computation_list))
    print("time data", state["time"])
    print()
    print("time2 data", state["time2"])
    print("--------------")
    print("time2 %.2f [minute]" % state["time2"].minute)
    print("time2 %.2f [hour]" % state["time2"].hour)
    print("time2 %.2f [second]" % state["time2"].second)
    print("time2 %.2f [day]" % state["time2"].day)
    print("time2 computation list %s" % ",".join(state["time2"].computation_list))
    print("time2 data", state["time2"])
    print()
    event.add50minutes()
    print()
    print("time base", state["time"])
    print("--------------")
    print("time %.2f [minute]" % state["time"].minute)
    print("time %.2f [minute] (re-access)" % state["time"].minute)
    print("time %.2f [minute] (re-access)" % state["time"].minute)
    print("time %.2f [minute] (re-access)" % state["time"].minute)
    print("time %.2f [hour]" % state["time"].hour)
    print("time %.2f [hour] (re-access)" % state["time"].hour)
    print("time %.2f [hour] (re-access)" % state["time"].hour)
    print("time %.2f [second]" % state["time"].second)
    print("time %.2f [day]" % state["time"].day)
    print("time computation list %s" % ",".join(state["time"].computation_list))
    print("time data", state["time"])
    print()
    print("time2 base", state["time2"])
    print("--------------")
    print("time2 %.2f [mminute]" % state["time2"].minute)
    print("time2 %.2f [hour]" % state["time2"].hour)
    print("time2 %.2f [second]" % state["time2"].second)
    print("time2 %.2f [day]" % state["time2"].day)
    print("time2 computation list %s" % ",".join(state["time2"].computation_list))
    print("time2 data", state["time2"])


def register(mf):
    mf.register_event("main", main)
    mf.register_event("add50minutes", add50minutes)
