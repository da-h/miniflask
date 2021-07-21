import re
import pathlib
from textwrap import dedent
from inspect import getmembers, isfunction, signature

from miniflask import __version__
from miniflask.miniflask import miniflask, miniflask_wrapper  # noqa: F401
from miniflask.event import event  # noqa: F401
from miniflask.state import state  # noqa: F401

classes = [
    ("miniflask Instance", miniflask),
    ("register(mf) Object", miniflask_wrapper),
    ("event", event),
    ("state", state)
]

section_re = re.compile(r"\s*([a-zA-Z\-]+):")
fns_done = []

# update version.md
with open("version.md", "w") as f:
    f.write("{version=\"%s\"}" % __version__)

for i, (clsname, cls) in enumerate(classes):  # noqa: C901
    j = 0

    members = getmembers(cls, isfunction)

    # resort __init__ to front
    init_index = [n for n, m in members].index('__init__')
    if init_index >= 0:
        members = [members[init_index]] + members[:init_index] + members[init_index + 1:]

    for name, fn in members:
        if fn in fns_done:
            continue

        # skip private api
        # if name.startswith("_"):
        #     continue

        doc = fn.__doc__

        if not doc:
            continue
        fns_done.append(fn)
        j += 1

        first_line, doc = doc.split("\n", 1)
        first_line = first_line.strip()
        if first_line:
            name = first_line
        if name.startswith("!"):
            name = name[1:]
            skipsignature = True
        else:
            skipsignature = False
        doc = dedent(doc).split("\n")

        # convert doc-format to luke format
        # ---------------------------------
        luke_doc = ["{theme=documentation "]

        # name of first line is display name of function
        luke_doc.append("fname='%s'" % name)

        # get signature
        if not skipsignature:
            sig = signature(fn)
            sig_str = ", ".join(['%s="%s"' % (name, param.default) if isinstance(param.default, str) else str(param) for name, param in sig.parameters.items() if name != "self"])
            luke_doc.append("signature='%s'" % sig_str)
            luke_doc.append("fnamewithsig='%s(%s)'" % (name if not first_line else first_line, sig_str))

        # second line is description
        luke_doc.append("shortdescr='%s'" % doc[0])

        # collect topics (starting with word, ending with colon
        topics = {"main": []}
        current_topic = topics["main"]
        for line in doc[2:]:

            match = section_re.match(line)
            if match:
                # print("-> Topic="+match[1].lower())
                current_topic = topics[match[1].lower()] = []
                continue

            current_topic.append(line)

        # convert topics to luke variables
        for t, text in topics.items():
            luke_doc.append("%s=[\n%s\n]" % (t, "\n".join(text)))

        luke_doc.append("}")

        luke_doc.append("""
        \\ifexists{filename_current}[][\\include{"../include.md"}
# %{fname}%
## \\shortdescr

----

\\main

\\ifexists{note}[
### Note {.alert}
\\note
]

\\ifexists{fnamewithsig}[
### Method Signature
```python {verbatim=%{fnamewithsig}%}
```
]

\\ifexists{returns}[
## Returns
\\returns
]

\\ifexists{args}[
## Arguments
\\args
]

\\ifexists{examples}[
## Examples
\\examples
]

\\ifexists{appendix}[

---

\\appendix
]
]
        """)

        # create file for that function
        # -----------
        cls_dir = pathlib.Path("08-API/%02d-%s" % (i + 2, clsname.replace(" ", "-")))
        cls_dir.mkdir(parents=True, exist_ok=True)
        print(str(cls_dir / ("%02d-%s.md" % (j, name))))
        with open(cls_dir / ("%02d-%s.md" % (j, name)), "w") as f:
            f.write("\n".join(luke_doc))

        # create index (pointing to first function)
        # ------------
        if not (cls_dir / "index.md").exists():
            with open(cls_dir / "index.md", "w") as f:
                f.write("\\redirect{\"%02d-%s.md\"}" % (j, name))
