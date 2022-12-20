import miniflask  # noqa: E402


def test_enum():
    mf = miniflask.init(
        ".modules",
        debug=True
    )
    mf.run(
        modules=["module1"],
        argv=["--module1.sizerequired", "SMALL",
              "--module1.sizelist", "MEDIUM", "SMALL"]
    )


def test_enum_relative_import():
    mf = miniflask.init(
        ".modules",
        debug=True
    )
    mf.run(
        modules=["module2"],
        argv=["--module1.sizerequired", "SMALL",
              "--module1.sizelist", "MEDIUM", "SMALL"]
    )
