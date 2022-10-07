
def register(mf):
    mf.register_default_module("..module3", required_id="modules.otherdir")
    mf.register_event("main", lambda: print("tests"), unique=False)
