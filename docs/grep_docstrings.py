import pathlib
from textwrap import dedent
from inspect import getmembers, isfunction

from miniflask.miniflask import miniflask, miniflask_wrapper  # noqa: F401
from miniflask.event import event  # noqa: F401
from miniflask.state import state  # noqa: F401

classes = ["miniflask", "miniflask_wrapper", "event", "state"]

for cls in classes:
    for name, fn in getmembers(locals()[cls], isfunction):

        # skip private api
        # if name.startswith("_"):
        #     continue

        if not fn.__doc__:
            continue

        print(dedent(fn.__doc__))

        # create file for that function
        cls_dir = pathlib.Path("08-Reference/%s" % cls)
        cls_dir.mkdir(parents=True, exist_ok=True)
        with open(cls_dir / ("%s.md" % name), "w") as f:
            f.write("\n".join(f.strip() for f in fn.__doc__.split("\n")))
