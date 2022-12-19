def register(mf):
    mf.register_defaults({
        "test_multiple_inline_I": lambda: 1 * 42, "test_multiple_inline_II": lambda: 2 * 42,
    })
