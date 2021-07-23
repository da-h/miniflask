
def main():
    print("main event")


def register(mf):
    mf.register_event('main', main, unique=False)
