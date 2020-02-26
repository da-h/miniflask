from miniflask import outervar

def main(state, event, varA=outervar):
    print("outervar:",varA)

def register(mf):
    mf.register_event('main', main, unique=True)
