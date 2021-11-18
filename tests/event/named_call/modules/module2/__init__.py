
def main(state):
    del state
    return 2345


def register(mf):
    mf.register_event('main', main, unique=False)
