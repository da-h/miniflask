def showModules(state, event):
    event._mf.showModules(with_event=state.all["events"])

def register(mf):
    mf.register_globals({
        "events": True
    })
    mf.register_event('init', showModules)
