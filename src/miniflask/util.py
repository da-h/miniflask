from os import walk, path
from colored import attr, fg
from argparse import Action
import argparse
import re


# get modules in a directory
def getModulesAvail(module_dirs, f={}):
    for base_module_name, dir in module_dirs.items():
        basename_dir = path.basename(dir)
        for (dirpath, dirnames, filenames) in walk(dir):
            module_name_id = base_module_name + "." + dirpath[len(dir) + 1:].replace(path.sep, ".")
            import_path = ((basename_dir + ".") if not basename_dir.endswith('.') else "") + dirpath[len(dir) + 1:].replace(path.sep, ".")

            # empty module id is not allowed
            if len(module_name_id) == 0:
                continue

            # ignore sub directories
            if path.exists(path.join(dirpath, ".ignoredir")) or (path.basename(dirpath).startswith(".") and not dirpath.endswith('.')):
                dirnames[:] = []
                continue

            # ignore no real moules
            if ".module" not in filenames:
                continue

            # module found
            f[module_name_id] = {
                'id': module_name_id,
                'lowpriority': path.exists(path.join(dirpath, ".lowpriority")),
                'importpath': import_path
            }
    return f


# coloring
def highlight_loading_module(x):
    x = x.split(".")
    return fg('light_gray') + ".".join(x[:-1]) + ("" if len(x) == 1 else ".") + attr('reset') + fg('green') + attr('bold') + x[-1] + attr('reset')


highlight_error = lambda: fg('red') + attr('bold') + "Error:" + attr('reset') + " "
highlight_name = lambda x: fg('blue') + attr('bold') + x + attr('reset')
highlight_module = lambda x: fg('green') + attr('bold') + x + attr('reset')
highlight_loading = lambda x: highlight_loading_module(x)
highlight_loading_default = lambda y, x: attr('dim') + y + attr('reset') + " ⟶  " + highlight_loading_module(x)
highlight_loaded_default = lambda y, x: attr('dim') + x + " found modules: " + ", ".join(highlight_loading_module(m) for m in y) + attr('reset')
highlight_loaded_none = lambda x: fg('red') + x + attr('reset')
highlight_loaded = lambda x, y: attr('underlined') + x + attr('reset') + " " + fg('green') + attr('bold') + ", ".join(y) + attr('reset')
highlight_event = lambda x: fg('light_yellow') + x + attr('reset')
highlight_type = lambda x: fg('cyan') + x + attr('reset')
highlight_val = lambda x: x
highlight_val_overwrite = lambda x: fg('red') + attr('bold') + x + attr('reset')


def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')


def get_varid_from_fuzzy(varid, varid_list):
    # check for direct match first
    r = re.compile(r"^(.*\.)?%s$" % varid)
    found_varids = list(filter(r.match, varid_list))

    # if no matching varid found, check for fuzzy identifier
    if len(found_varids) == 0:
        r = re.compile(r"^(.*\.)?%s$" % varid.replace(".", r"\.(.*\.)*"))
        found_varids = list(filter(r.match, varid_list))

    # if more than one module found, use default module-variables
    if len(found_varids) > 1:
        found_varids = list(filter(lambda x: "default." in x, found_varids))

    return found_varids


# Argparse action for handling Enums
class EnumAction(Action):
    def __init__(self, **kwargs):
        enum = kwargs.pop("type", None)
        self._enum = enum

        # enum defines argparse choices elready
        choices = set([*(e.name for e in enum), *(e.name.lower() for e in enum)])
        kwargs.setdefault("choices", choices)

        # actually register argparse action
        super(EnumAction, self).__init__(**kwargs)

    def __call__(self, parser, namespace, values, option_string=None, return_enum=False):
        if isinstance(values, list):
            enum = [self(parser, namespace, v, option_string=option_string, return_enum=True) for v in values]
        else:
            try:
                enum = self._enum[values.upper()]
            except:  # noqa: E722
                enum = self._enum(values)
            if return_enum:
                return enum
        setattr(namespace, self.dest, enum)
