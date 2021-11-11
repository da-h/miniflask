import os
from enum import EnumMeta
from itertools import zip_longest

from colored import attr, fg

from ...util import highlight_module, highlight_val, highlight_name, highlight_val_overwrite, highlight_event
from ...state import like


html_module = lambda x: x  # noqa: E731 no-lambda
html_name = lambda x: x  # noqa: E731 no-lambda
html_val = lambda x: x  # noqa: E731 no-lambda
html_val_overwrite = lambda x: x  # noqa: E731 no-lambda


def listsettings(mf, state, asciicodes=True):

    # colors
    color_module = highlight_module if asciicodes else html_module
    color_name = highlight_name if asciicodes else html_name
    color_val = highlight_val if asciicodes else html_val
    color_val_overwrite = highlight_val_overwrite if asciicodes else html_val_overwrite
    linesep = os.linesep if asciicodes else "\n"
    attr_fn = (lambda x: '') if not asciicodes else attr

    last_k = []
    if len(state.all) == 0:
        return "No Settings available."
    maxklen = max(len(k) for k in state.all.keys())
    text = "Folder│" + color_name("module") + "│" + color_module("variable") + (" " * (maxklen - 22)) + " = " + color_val("value") + linesep
    text += "—" * (maxklen + 8) + linesep if asciicodes else ''
    for k, v in sorted(state.all.items()):

        # ignore state variables that are not registered for argument parsing
        if k not in state.default:
            continue

        klen = len(k)
        korig = k
        overwritten = v != (state.default[k].default if hasattr(state.default[k], 'default') else state.default[k])
        k = k.split(".")
        if len(k) > 1:
            k_hidden = [" " * len(ki) if ki == ki2 and asciicodes else ki for ki, ki2 in zip_longest(k, last_k) if ki is not None]
            last_k = k
            k_hidden[-2] = color_name(k_hidden[-2])
            k_hidden[-1] = color_module(k_hidden[-1])
        else:
            k_hidden = k
            k_hidden[-1] = color_module(k_hidden[-1])

        is_lambda = callable(state.default[korig]) and not isinstance(state.default[korig], type) and not isinstance(state.default[korig], EnumMeta) and not isinstance(state.default[korig], like)
        value_str = attr_fn('dim') + "λ ⟶   " + attr_fn('reset') + str(state.default[korig].default) if is_lambda else state.default[korig].str(asciicodes=False) if hasattr(state.default[korig], 'str') else str(state.default[korig])
        append = "" if not overwritten else " ⟶   " + color_val_overwrite(str(v))
        text += "│".join(k_hidden) + (" " * (maxklen - klen)) + " = " + color_val(value_str) + append + linesep

        # add definition paths
        if state["show_registration_definitions"]:
            prefix = "│".join([" " * len(k) for k in korig.split(".")]) + (" " * (maxklen - klen)) + "   "
            for definition_type, caller_traceback in mf._settings_parser_tracebacks[korig]:
                summary = next(filter(lambda t: not t.filename.endswith("miniflask/miniflask.py"), reversed(caller_traceback)))
                arg_err_str = (fg('blue') + "definition" if definition_type == "definition" else fg('yellow') + "overwritten") + attr('reset') + " in line %s in file '%s'." % (highlight_event(str(summary.lineno)), attr('dim') + os.path.relpath(summary.filename) + attr('reset'))
                text += prefix + arg_err_str + linesep

    return text


def init(mf, state):
    print(listsettings(mf, state))


def settings_html(mf, state):
    html = listsettings(mf, state, asciicodes=False)
    html = html.split("\n")
    html = "\n".join([h.replace('=', '</td><td style="padding: 0 0.5em;">=</td><td><code>', 1) for h in html])
    html = html.replace('\n', '</code></td></tr>\n<tr><td style="text-align:left;">')
    html = html[:-8]
    html = "<table><tr><td style='padding: 0 0.5em; font-weight: bold; text-align: left;'>" + html + "</table>"
    return html


def register(mf):
    mf.register_helpers({
        "show_registration_definitions": False
    })
    mf.register_event("init", init, unique=False)
    mf.register_event("settings_html", settings_html, unique=False)
