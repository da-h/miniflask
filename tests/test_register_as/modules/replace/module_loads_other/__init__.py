
def register(mf):
    file = __file__
    mf.register_as("main.module_loads_other")
    mf.load(["submodule", "module_with_submodule"])
    mf.register_event("main", lambda: print(file))
