import sys
from itertools import zip_longest
from miniflask.miniflask import highlight_module, highlight_val, highlight_name, highlight_val_overwrite

def insert_key(S,k,val):

    # create dict if not existent
    if k[0] not in S:
        S_new = {}
        S[k[0]] = S_new

    # insert keys recursively
    if len(k) > 1:
        insert_key(S[k[0]], k[1:], val)
    else:
        S[k[0]] = val

def listsettings(state, event):
    S = {}
    last_k = []
    if len(state.all) == 0:
        print("No Settings available.")
        return
    maxklen = max(len(k) for k in state.all.keys())
    print("Folder│"+highlight_name("module")+"│"+highlight_module("variable")+(" "*(maxklen-22))+" = "+highlight_val("value"))
    print("—"*(maxklen+8))
    for k, v in state.all.items():
        klen = len(k)
        korig = k
        overwritten = v != state.default[k]
        k = k.split(".")
        insert_key(S,k,v)
        if len(k) > 1:
            k_hidden = [" "*len(ki) if ki==ki2 else ki for ki,ki2 in zip_longest(k,last_k) if ki is not None]
            last_k = k
            k_hidden[-2] = highlight_name(k_hidden[-2])
            k_hidden[-1] = highlight_module(k_hidden[-1])
        else:
            k_hidden = k

        append = "" if not overwritten else " -> "+highlight_val_overwrite(str(v))
        print("│".join(k_hidden)+(" "*(maxklen-klen))+" = "+highlight_val(str(state.default[korig]))+append)

def register(mf):
    mf.register_event("init", listsettings)
