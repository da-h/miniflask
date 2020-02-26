from os import walk, path
from colored import attr, fg

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

        # add reference to shortid
        is_module_with_shortid = not path.exists(path.join(dirpath,".noshortid"))
        if is_module_with_shortid:
            if module_name_short in f and module_name_short != module_name_id:
                del f[module_name_short]
            else:
                f[module_name_short] = module_name_id
    return f

# coloring
highlight_error = lambda: fg('red')+attr('bold')+"Error:"+attr('reset')+" "
highlight_name = lambda x: fg('blue')+attr('bold')+x+attr('reset')
highlight_module = lambda x: fg('green')+attr('bold')+x+attr('reset')
highlight_loading = lambda x: "Load Module ... "+highlight_module(x)
highlight_loaded_none = lambda x: fg('red')+x+attr('reset')
highlight_loaded = lambda x, y: attr('underlined')+x+attr('reset')+" "+fg('green')+attr('bold')+", ".join(y)+attr('reset')
highlight_event = lambda x: fg('light_yellow')+x+attr('reset')
highlight_blue_line = lambda x: fg('blue')+attr('bold')+x+attr('reset')
highlight_type = lambda x: fg('cyan')+x+attr('reset')
highlight_val = lambda x: fg('white')+x+attr('reset')
highlight_val_overwrite = lambda x: fg('red')+attr('bold')+x+attr('reset')


