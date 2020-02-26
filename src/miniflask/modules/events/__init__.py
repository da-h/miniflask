from miniflask.dummy import miniflask_dummy
from colored import fg, bg, attr
from miniflask.miniflask import highlight_module

def color_module(moduleid):
    moduleid = moduleid.split(".")
    moduleid[0] = attr('dim')+moduleid[0]
    moduleid[-1] = attr('reset')+highlight_module(moduleid[-1])
    return ".".join(moduleid)

def register(mf):
    events = {}
    for module in mf.modules_avail.keys():

        # ignore self
        if __name__ == mf.getModuleId(module):
            continue

        # ignore short ids
        if module != mf.getModuleId(module):
            continue

        # note all events
        module_events = mf.getModuleEvents(module)
        for e in module_events:
            if e in events:
                events[e].append(module)
            else:
                events[e] = [module]

    # print it
    print()
    print(fg('yellow')+attr('underlined')+"Available events"+attr('reset'))
    for e in sorted(events.keys()):
        unique_flag = "!" if e[1] else ">"
        print(fg('yellow')+unique_flag+' '+e[0]+attr('reset')+" used in "+", ".join([color_module(ev) for ev in events[e]])+attr('reset'))
    print()
