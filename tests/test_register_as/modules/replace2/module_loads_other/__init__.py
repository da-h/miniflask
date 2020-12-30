
def register(mf):
    file = __file__
    mf.load(["submodule", "module_with_submodule"])
    mf.register_event("main", lambda: print(file))
