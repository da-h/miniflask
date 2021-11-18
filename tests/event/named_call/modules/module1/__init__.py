
def main():
    return 1337


def register(mf):
    mf.register_event('main', main, unique=False)
