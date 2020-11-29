from miniflask import outervar


def main(state, event, var_a=outervar):
    del state, event  # unused
    print("outervar:", var_a)


def register(mf):
    mf.register_event('main', main, unique=True)
