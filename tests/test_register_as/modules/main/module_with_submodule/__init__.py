
def register(mf):
    file = __file__
    mf.load("submodule")
    mf.register_event("main", lambda: print(file))
