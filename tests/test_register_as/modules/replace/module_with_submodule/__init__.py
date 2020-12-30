
def register(mf):
    file = __file__
    mf.register_as("main.module_with_submodule")
    mf.load("submodule")
    mf.register_event("main", lambda: print(file))
