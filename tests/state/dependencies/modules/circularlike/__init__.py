

def main():
    print("main event")


def register(mf):
    mf.register_defaults({
        "foobar": lambda state, event: state["foobar"]
    })
    mf.register_event('main', main, unique=False)
