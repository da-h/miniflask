from miniflask import outervar


def main(state, event, varA=outervar):
    del state, event  # unused
    print("outervar:", varA)


def register(mf):
    mf.register_event('main', main, unique=True)
