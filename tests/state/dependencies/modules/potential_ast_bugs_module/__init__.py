
def register(mf):
    mf.register_defaults({
        "annotation": lambda: 10,
        "annotation.bug": lambda: 10,
        "lambda_with_comment": lambda: 10,  # just some comment
        "var_with_comment": 10,  # just some comment
    })
