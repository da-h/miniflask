
def register(mf):
    mf.overwrite_defaults({
        "testvar": 42
    }, scope="..notexistentmodule")
