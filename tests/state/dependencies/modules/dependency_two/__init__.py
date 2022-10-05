from miniflask import like


def register(mf):
    mf.register_defaults({
        "bar": 11,
        "bar2": like("foobar2", 12),
        "bar3": like("foobar3", 13)
    })
