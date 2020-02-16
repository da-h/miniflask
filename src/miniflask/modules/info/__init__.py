import sys

def register(mf):
    mf.load(["modules","events"])
    mf.stop_parse()
    sys.exit(0)
