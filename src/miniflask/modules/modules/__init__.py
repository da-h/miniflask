def showModules(state, event):
    event._mf.showModules(with_event=state.all["events"])
    print()

def register(mf):
    mf.register_globals({
        "events": False
    })
    mf.register_event('init', showModules)
