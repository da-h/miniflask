from miniflask import like


def main():
    print("main event")


def register(mf):
    mf.register_defaults({
        "foobar": like("foobar", 0)
    })
    mf.register_event('main', main, unique=False)
