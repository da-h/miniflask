from miniflask import outervar


def main(var_a=outervar):
    print("outervar:", var_a)


def register(mf):
    mf.register_event('main', main)
