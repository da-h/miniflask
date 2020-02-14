from os import walk, path

# get modules in a directory
def getModulesAvail(modules_dir):
    f = {}
    for (dirpath, dirnames, filenames) in walk(modules_dir):
        module_name_id = dirpath[len(modules_dir)+1:].replace(path.sep,".")
        module_name_short = module_name_id.split(".")[-1]
        if len(module_name_id) == 0:
            continue
        if ".module" not in filenames:
            continue
        f[module_name_id] = module_name_id
        if module_name_short in f and module_name_short != module_name_id:
            del f[module_name_short]
        else:
            f[module_name_short] = module_name_id
    return f
