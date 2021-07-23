
def register(mf):
    mf.overwrite_defaults({
        "var_default_override": 12,
        "var_default_override_twice": 13,
        "var_default_override_twice_and_cli": 14
    }, scope="..defaults")
