import traceback as tb

from colored import fg, attr


def save_traceback():
    try:
        raise TracebackException("Could not register Variable.")
    except TracebackException:
        full_tb = tb.extract_stack()

        # ignore this very function in the traceback
        return full_tb[:-1]


class RegisterError(Exception):

    def __str__(self):
        base_exc = super().__str__().replace("\\x1b", "\x1b")
        return base_exc + ("\n\n" + fg('red') + "The variable definition occured in" + attr('reset') + ":\n""" + format_traceback_list(self.traceback) if self.traceback is not None else "")

    def __init__(self, *args, msg='', traceback=None, **kwargs):
        # del args, kwargs  # unused
        # storing the traceback which provides useful information about where the exception occurred
        self.traceback = traceback

        super().__init__(" ".join(args) + " " + msg, **kwargs)


class StateKeyError(Exception):

    def __str__(self):
        base_exc = super().__str__().replace("\\x1b", "\x1b")
        return base_exc + ("\n\n" + fg('red') + "The Key Error occured in" + attr('reset') + ":\n""" + format_traceback_list(self.traceback) if self.traceback is not None else "")

    def __init__(self, *args, msg='', traceback=None, **kwargs):
        # storing the traceback which provides useful information about where the exception occurred
        self.traceback = traceback

        super().__init__(" ".join(args) + " " + msg, **kwargs)


class TracebackException(Exception):
    pass


def format_traceback_list(traceback_list, ignore_miniflask=True, exc=None):
    if ignore_miniflask:
        traceback_list = [t for t in traceback_list if not t.filename.endswith("src/miniflask/event.py") and (not t.filename.endswith("src/miniflask/miniflask.py") or t.name in ["load", "run"])]

    # ignore "raise" lines
    if exc is not None and "raise" in traceback_list[-1].line:
        t = traceback_list[-1]
        t.filename = fg('green') + t.filename + attr('reset')
        t.lineno = fg('yellow') + str(t.lineno) + attr('reset')
        t.name = fg('blue') + attr("bold") + t.name + attr('reset')
        exception_type = fg('red') + attr('bold') + type(exc).__name__ + attr('reset')
        last_msg = "  File %s, line %s, in %s\n    %s: %s" % (t.filename, t.lineno, t.name, exception_type, str(exc))
        traceback_list = traceback_list[:-1]

    # format the raise line differently
    if exc is not None and "raise" not in traceback_list[-1].line:
        exception_type = fg('red') + attr('bold') + type(exc).__name__ + attr('reset')
        last_msg = "    %s: %s" % (exception_type, str(exc))
    else:
        last_msg = str(exc)
    for t in traceback_list:
        t.filename = fg('green') + t.filename + attr('reset')
        t.lineno = fg('yellow') + str(t.lineno) + attr('reset')
        t.name = fg('blue') + attr("bold") + t.name + attr('reset')
    return "".join(tb.format_list(traceback_list)) + last_msg
