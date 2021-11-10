
def main():
    print("overwritten main event and removed attached as well")


def register(mf):
    mf.overwrite_event('main', main, keep_attached_events=False)
