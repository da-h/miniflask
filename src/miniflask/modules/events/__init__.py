from miniflask.dummy import miniflask_dummy
from colored import fg, bg, attr
from miniflask.miniflask import highlight_module
import re
import typing

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
            event_key = (e[0],e[1][0])
            if event_key in events:
                events[event_key][0].append(module_id)
                events[event_key][1].append(e[1][1])
            else:
                events[event_key] = ([module_id],[e[1][1]])

    # register actual module
    mf.register_defaults({
        "event": "",
        "module": "",
        "long": False,
        "list": False,
        "only_loaded": True,
    })
    mf.register_helpers({
        "events": events
    })
    mf.register_event('init', init)
    mf.register_event('get_event_tree', get_event_tree, unique=True)


# adapted from https://stackoverflow.com/a/51904019
from dis import Bytecode
def list_func_calls(fn):
    funcs = []
    bytecode = Bytecode(fn)
    instrs = list(reversed([instr for instr in bytecode]))
    for (ix, instr) in enumerate(instrs):
        if instr.argval == "event" and ix-2 > 0 and instrs[ix-1].opname == "LOAD_METHOD":
            funcs.append(instrs[ix-1].argval)
        elif instr.argval == "event" and ix-1 > 0 and instrs[ix-1].opname == "LOAD_ATTR" and instrs[ix-1].argval == "optional" and instrs[ix-2].opname == "LOAD_METHOD":
            funcs.append(instrs[ix-2].argval)
        elif instr.argval == "event" and ix-1 > 0 and instrs[ix-1].opname == "LOAD_ATTR" and instrs[ix-1].argval not in ["_mf"]:
            if instrs[ix-1].argval == "optional":
                if ix - 2 > 0:
                    funcs.append(instrs[ix-2].argval)
            else:
                funcs.append(instrs[ix-1].argval)
    return ["%s" % funcname for funcname in reversed(funcs)]


def get_event_tree(state, event, eventname, event_tree={}, only_loaded=True):
    _fns = []
    if only_loaded:
        modules = []
        if (eventname,False) in state["events"]:
            modules += state["events"][(eventname,False)][0]
        if (eventname,True) in state["events"]:
            modules += state["events"][(eventname,True)][0]
        for m in modules:
            if not m in event._mf.modules_loaded:
                continue
            _fns.append(event[m][eventname])
    else:
        if (eventname,False) in state["events"]:
            _fns += state["events"][(eventname,False)][1]
        if (eventname,True) in state["events"]:
            _fns += state["events"][(eventname,True)][1]

    fns = []
    for fn in _fns:
        if isinstance(fn,type):
            for fname in dir(fn):
                f = getattr(fn,fname)
                if fname.startswith("__") and fname.endswith("__") and fname != "__init__":
                    continue
                if not callable(f) or type(f) == type:
                    continue
                if type(f) == typing.TypeVar:
                    continue
                fns.append(f)
        else:
            fns += [fn]

    subevents, subevents_tree = [], []
    for fn in fns:
        fn_calls = list_func_calls(fn)
        # used = set()
        # fn_calls = [x for x in fn_calls if x not in used and (used.add(x) or True)]
        for s in fn_calls:
            subevents.append(s)
            if s in event_tree:
                subevents_tree.append(True)
            else:
                # breakpoint()
                # event_tree[s] = (subevents, subevents_tree)
                (s1,s2,_) = event.get_event_tree(s, event_tree, only_loaded=only_loaded)
                event_tree[s] = (s1, s2)
                subevents_tree.append((s1,s2))
    return subevents, subevents_tree, event_tree

def print_event_tree(state,event,tree,full_tree,depth=0):
    if depth == 0:
        print()
        print(fg('yellow')+attr('underlined')+"Event-Calltree"+attr('reset'))
    for name,subtree in zip(*tree):
        unique_flag = ">"
        print("   "*depth+fg('yellow')+unique_flag+' '+attr('reset')+name+attr('reset'))
        if subtree != True:
            if len(subtree) > 0:
                print_event_tree(state,event,subtree,full_tree,depth+1)
        else:
            if len(full_tree[name][1]) > 0:
                print("   "*(depth+2)+attr('dim')+"as above"+attr('reset'))
    if depth == 0:
        print() 

def print_event_list(state,event):
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
        print(fg('yellow')+unique_flag+' '+e[0]+attr('reset')+" used in "+", ".join([color_module(ev, short=not state["long"]) for ev in state["events"][e][0]])+attr('reset'))
    print()

def init(state, event):

    # print it
    if state["list"]:
        print_event_list(state,event)
    else:
        event_names, event_subtrees, full_tree = event.get_event_tree('main',only_loaded=state["only_loaded"])
        print_event_tree(state,event,[['main'],[(event_names,event_subtrees)]],full_tree)

