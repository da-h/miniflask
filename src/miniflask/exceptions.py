import traceback as tb
from colored import fg, bg, attr

def save_traceback():
    try:
        raise TracebackException("Could not register Variable.")
    except TracebackException as e:
        full_tb = tb.extract_stack()

        # ignore all miniflask internals
        # note for the -2: last tb-summary is from this function itself and can be ignored as well
        for i in range(len(full_tb)-2,0,-1):
            if full_tb[i].name != "register_defaults":
                break
        return full_tb[:i]

class RegisteringException(Exception):
    # def __init__(self, msg, traceback):
    #     self.with_traceback(traceback)
    def __str__(self):
        base_exc = super().__str__()
        for t in self.traceback:
            t.filename = fg('green')+t.filename+attr('reset')
            t.lineno = fg('yellow')+str(t.lineno)+attr('reset')
            t.name = fg('blue')+attr("bold")+t.name+attr('reset')
        traceback = "".join(tb.format_list(self.traceback))
        return base_exc + "\n\nThe variable definition occured in:\n"""+traceback

    def __init__(self, msg='', traceback=tb.extract_stack(), *args, **kwargs):

        # storing the traceback which provides useful information about where the exception occurred
        self.traceback = traceback

        super().__init__(msg)

class TracebackException(Exception):
    pass
