
def register(mf):
    mf.load("...otherdir.module2")
    mf.register_event("main", lambda: print("tests"))
