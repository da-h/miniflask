

def init(mf):
    print("overwrites event during init-event")
    mf.overwrite_event("main", main)


def main():
    print("overwritten main event during event")


def register(mf):
    mf.overwrite_event('init', init)
