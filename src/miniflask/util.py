import re
import argparse
import inspect
from argparse import Action
from os import walk, path
from pathlib import Path
from pkgutil import resolve_name
from colored import attr, fg


# get the absolute package name of the current file to cwd()
# - i.e. $result can be loaded using `import $result`
def get_full_base_module_name(directory):
    directory = Path(directory).absolute()
    base_import = directory.name

    while (directory.parent / "__init__.py").exists():
        directory = directory.parent
        base_import = directory.name + "." + base_import

    return base_import


# get modules in a directory
def getModulesAvail(python_import_paths, f=None):
    if f is None:
        f = {}
    for base_module_id, base_module_path in python_import_paths.items():
        if base_module_path.startswith("."):
            stack_frame = inspect.stack()[2]  # the frame in which miniflask.init has been called
            callee_module_path = Path(stack_frame.filename).parent
            base_module_path = get_full_base_module_name(callee_module_path) + base_module_path
        module = resolve_name(base_module_path)
        directory = module.__path__[0]

        for (dirpath, dirnames, filenames) in walk(directory):
            local_import_name = dirpath[len(directory) + 1:].replace(path.sep, ".")
            if local_import_name:
                module_id = base_module_id + "." + local_import_name
                module_path = base_module_path + "." + local_import_name
            else:
                module_id = base_module_id
                module_path = base_module_path

            # empty module id is not allowed
            if len(module_id) == 0:
                continue

            # ignore sub directories
            if path.exists(path.join(dirpath, ".ignoredir")) or (path.basename(dirpath).startswith(".") and not dirpath.endswith('.')):
                dirnames[:] = []
                continue

            # ignore no real moules
            if ".module" not in filenames:
                continue

            # module found
            f[module_id] = {
                'id': module_id,
                'lowpriority': path.exists(path.join(dirpath, ".lowpriority")),
                'importname': module_path
            }

    return f


# coloring
def highlight_loading_module(x):
    x = x.split(".")
    return fg('light_gray') + ".".join(x[:-1]) + ("" if len(x) == 1 else ".") + attr('reset') + fg('green') + attr('bold') + x[-1] + attr('reset')


highlight_error = lambda x="Error:": fg('red') + attr('bold') + x + attr('reset') + " "
highlight_name = lambda x: fg('blue') + attr('bold') + x + attr('reset')
highlight_module = lambda x: fg('green') + attr('bold') + str(x) + attr('reset')
highlight_loading = highlight_loading_module
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
    if v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    raise argparse.ArgumentTypeError('Boolean value expected.')


def get_varid_from_fuzzy(varid, varid_list, fuzzy_fill=True):

    # check for fuzzy identifier first (maybe user did not give all information)
    if fuzzy_fill:
        r = re.compile(r"^(.*\.)?%s$" % varid.replace(".", r"\.(.*\.)*"))
        found_varids = list(filter(r.match, varid_list))

        if len(found_varids) == 1:
            return found_varids
    else:
        found_varids = []

    # first check for direct match of a possibly scoped variable
    varid_scopes = varid.split(".")
    varid_scopes, varname = varid_scopes[:-1], varid_scopes[-1]
    for i in range(len(varid_scopes), -1, -1):
        varid_test = ".".join(varid_scopes[:i] + [varname])

        # check for direct match first
        r = re.compile(r"^(.*\.)?%s$" % varid_test)
        found_varids = list(filter(r.match, varid_list))

        if len(found_varids) == 1:
            return found_varids

    return found_varids


relative_import_re = re.compile(r"(\.+)(.*)")


def get_relative_id(possibly_relative_path, base_id, offset=1, ensure_local=False):
    if not base_id:
        return possibly_relative_path, False
    if ensure_local and not possibly_relative_path.startswith("."):
        possibly_relative_path = "." + possibly_relative_path
    was_relative = False
    m = relative_import_re.match(possibly_relative_path)
    if m is not None:
        upmodule = len(m[1])
        relative_module = m[2]
        if upmodule == offset:
            possibly_relative_path = base_id + ("." + relative_module if relative_module else "")
        else:
            possibly_relative_path = ".".join(base_id.split(".")[:-upmodule + offset]) + ("." + relative_module if relative_module else "")
        was_relative = True
    return possibly_relative_path, was_relative


# Argparse action for handling Enums
class EnumAction(Action):  # pylint: disable=too-few-public-methods
    def __init__(self, **kwargs):
        enum = kwargs.pop("type", None)
        self._enum = enum

        # enum defines argparse choices elready
        choices = set([*(e.name for e in enum), *(e.name.lower() for e in enum)])
        kwargs.setdefault("choices", choices)

        # actually register argparse action
        super().__init__(**kwargs)

    def __call__(self, parser, namespace, values, option_string=None, return_enum=False):  # pylint: disable=inconsistent-return-statements
        if isinstance(values, list):
            enum = [self(parser, namespace, v, option_string=option_string, return_enum=True) for v in values]
        else:
            try:
                enum = self._enum[values.upper()]
            except:  # noqa: E722 pylint: disable=bare-except
                enum = self._enum(values)
            if return_enum:
                return enum
        setattr(namespace, self.dest, enum)
