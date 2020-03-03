import sys
import os
from itertools import zip_longest
from miniflask.miniflask import highlight_module, highlight_val, highlight_name, highlight_val_overwrite

def listsettings(state, event):
    last_k = []
    if len(state.all) == 0:
        print("No Settings available.")
        return
    maxklen = max(len(k) for k in state.all.keys())
    text = "Folder│"+highlight_name("module")+"│"+highlight_module("variable")+(" "*(maxklen-22))+" = "+highlight_val("value")+os.linesep
    text += "—"*(maxklen+8)+os.linesep
    for k, v in sorted(state.all.items()):

        # ignore state variables that are not registered for argument parsing
        if k not in state.default:
            continue

        klen = len(k)
        korig = k
        overwritten = v != state.default[k]
        k = k.split(".")
        if len(k) > 1:
            k_hidden = [" "*len(ki) if ki==ki2 else ki for ki,ki2 in zip_longest(k,last_k) if ki is not None]
            last_k = k
            k_hidden[-2] = highlight_name(k_hidden[-2])
            k_hidden[-1] = highlight_module(k_hidden[-1])
        else:
            k_hidden = k
            k_hidden[-1] = highlight_module(k_hidden[-1])

        append = "" if not overwritten else " ⟶   "+highlight_val_overwrite(str(v))
        text += "│".join(k_hidden)+(" "*(maxklen-klen))+" = "+highlight_val(str(state.default[korig]))+append+os.linesep

    return text


def init(state,event):
    print(listsettings(state,event))

def settings_html(state,event):
    html = "<code>"+listsettings(state,event)+"</code>"
    return html


def register(mf):
    mf.register_event("init", init)
    mf.register_event("settings_html", settings_html)
