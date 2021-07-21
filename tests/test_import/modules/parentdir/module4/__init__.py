
def register(mf):
    mf.load("..module3")
    mf.register_event("main", lambda: print("tests"), unique=False)
