
def register(mf):
    file = __file__
    mf.register_as("main.module_with_submodule.submodule")
    mf.load("..")
    mf.register_event("main", lambda: print(file))


register_parents = False
