
def register(mf):
    file = __file__
    mf.load("..")
    mf.register_event("main", lambda: print(file))
