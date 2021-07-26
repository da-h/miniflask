
def main():
    print("overwritten main event")


def register(mf):
    mf.overwrite_event('main', main)
