
def register(mf):
    mf.load(".submodule")
    mf.register_event("main", lambda: print("tests"), unique=False)
