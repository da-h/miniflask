
def main(state, event):
    raise ValueError("Throwing an Exception.")


def register(mf):
    mf.register_event('main', main)
