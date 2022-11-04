lambda_tuple_definition = lambda: 42, lambda: 43  # noqa


def register(mf):
    mf.register_defaults({
        "test_lambda_tuple": lambda_tuple_definition[1],
    })
