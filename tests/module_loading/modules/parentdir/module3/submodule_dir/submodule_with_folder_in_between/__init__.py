

def register(mf):
    mf.register_event("main", lambda: print("tests"), unique=False)
