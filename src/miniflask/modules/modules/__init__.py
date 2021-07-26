def showModules(state, event):
    print(event._mf.showModules(with_event=state.all["events"]))


def register(mf):
    mf.register_globals({
        "events": False
    })
    mf.register_event('init', showModules, unique=False)
