import sys
import os
from itertools import zip_longest
from miniflask.miniflask import highlight_module, highlight_val, highlight_name, highlight_val_overwrite, like

html_module = lambda x: x
html_name= lambda x: x
html_val = lambda x: x
html_val_overwrite = lambda x: x

def listsettings(state, asciicodes=True):

    # colors
    color_module = highlight_module if asciicodes else html_module
    color_name = highlight_name if asciicodes else html_name
    color_val = highlight_val if asciicodes else html_val
    color_val_overwrite = highlight_val_overwrite if asciicodes else html_val_overwrite
    linesep = os.linesep if asciicodes else "<br>"

    last_k = []
    if len(state.all) == 0:
        return "No Settings available."
    maxklen = max(len(k) for k in state.all.keys())
    text = "Folder│"+color_name("module")+"│"+color_module("variable")+(" "*(maxklen-22))+" = "+color_val("value")+linesep
    text += "—"*(maxklen+8)+linesep
    for k, v in sorted(state.all.items()):

        # ignore state variables that are not registered for argument parsing
        if k not in state.default:
            continue

        klen = len(k)
        korig = k
        overwritten = v != (state.default[k].default if isinstance(state.default[k],like) else state.default[k])
        k = k.split(".")
        if len(k) > 1:
            k_hidden = [" "*len(ki) if ki==ki2 and asciicodes else ki for ki,ki2 in zip_longest(k,last_k) if ki is not None]
            last_k = k
            if k_hidden[-2] == "default":
                k_hidden[-3] = color_name(k_hidden[-3])
            else:
                k_hidden[-2] = color_name(k_hidden[-2])
            k_hidden[-1] = color_module(k_hidden[-1])
        else:
            k_hidden = k
            k_hidden[-1] = color_module(k_hidden[-1])

        append = "" if not overwritten else " ⟶   "+color_val_overwrite(str(v))
        text += "│".join(k_hidden)+(" "*(maxklen-klen))+" = "+color_val(str(state.default[korig]))+append+linesep

    return text


def init(state):
    print(listsettings(state))

def settings_html(state):
    html = "<code>"+listsettings(state, asciicodes=False)+"</code>"
    return html


def register(mf):
    mf.register_event("init", init)
    mf.register_event("settings_html", settings_html)
