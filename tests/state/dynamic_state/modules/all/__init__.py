

def register(mf):
    all_modules = sorted([module for module in mf.modules_avail.keys() if module.startswith("modules")])
    mf.load(all_modules)
    mf.register_globals({"filename_level0": __file__})
