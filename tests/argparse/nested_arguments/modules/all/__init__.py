

def main(state):
    for key, val in state.all.items():
        print(key, val)


def register(mf):
    all_modules = sorted([module for module in mf.modules_avail.keys() if module.startswith("modules")])
    mf.register_globals({"number": 0})
    mf.load(all_modules)
    mf.register_event("main", main)
