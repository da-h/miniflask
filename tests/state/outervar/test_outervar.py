import miniflask  # noqa: E402


def test_outervar():
    mf = miniflask.init(
        ".modules",
        debug=True
    )

    event = mf.event
    mf.load("module1")
    var_a = 42
    mf.event.main()
    del event, var_a  # now unused


def test_outervar_with_before_event(capsys):
    mf = miniflask.init(
        ".modules",
        debug=True
    )

    event = mf.event
    mf.load("module2")
    var_a = 42
    mf.event.main()
    del event, var_a  # now unused

    captured = capsys.readouterr()
    out = """
before_main
outervar: 42
main
"""
    assert out in captured.out
