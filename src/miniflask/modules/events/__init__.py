from miniflask.dummy import miniflask_dummy
from colored import fg, bg, attr
from miniflask.miniflask import highlight_module
import re

def color_module(moduleid, short=False):
    moduleid = moduleid.split(".")
    moduleid[0] = attr('dim')+moduleid[0]
    moduleid[-1] = attr('reset')+highlight_module(moduleid[-1])
    if short:
        return moduleid[-1]
    return ".".join(moduleid)

def register(mf):

    # precompute events
    events = {}
    for module_id in mf.modules_avail.keys():
        module_path = mf.modules_avail[module_id]["importpath"]

        # ignore self
        if __name__ == mf.getModuleId(module_id):
            continue

        # note all events
        module_events = mf.getModuleEvents(module_id)
        for e in module_events:
            if e in events:
                events[e].append(module_id)
            else:
                events[e] = [module_id]
                
    # register actual module
    mf.register_defaults({
        "event": "",
        "module": "",
        "long": False,
    })
    mf.register_helpers({
        "events": events
    })
    mf.register_event('init', init)


def init(state):

    # print it
    print()
    print(fg('yellow')+attr('underlined')+"Available events"+attr('reset'))
    event_list = state["events"].keys()
    if state["event"]:
        r = re.compile(".*"+state["event"]+".*")
        event_list = list(filter(lambda e: r.match(e[0]),event_list))
    if state["module"]:
        new_events = {}
        r = re.compile(".*"+state["module"]+".*")
        for e in state["events"].keys():
            modules = list(filter(r.match, state["events"][e]))
            if len(modules) > 0:
                new_events[e] = modules
        state["events"] = new_events
        event_list = list(filter(lambda e: e in state["events"],event_list))
    for e in sorted(event_list):
        unique_flag = "!" if e[1] else ">"
        print(fg('yellow')+unique_flag+' '+e[0]+attr('reset')+" used in "+", ".join([color_module(ev, short=not state["long"]) for ev in state["events"][e]])+attr('reset'))
    print()
