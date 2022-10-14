import miniflask  # noqa: E402


def test_beforeafter_setup_none_return(capsys):
    mf = miniflask.init(
        ".modules",
        debug=True
    )
    mf.load("setup_none_return")
    mf.parse_args([])
    captured = capsys.readouterr()
    mf.event.main()
    captured = capsys.readouterr()
    assert captured.out == """
event called with value: 42
event returned value: None
""".lstrip()


def test_beforeafter_before(capsys):
    mf = miniflask.init(
        ".modules",
        debug=True
    )
    mf.load(["setup_none_return", "beforeevent", "beforeevent2"])
    mf.parse_args([])
    captured = capsys.readouterr()
    mf.event.main()
    captured = capsys.readouterr()
    assert captured.out == """
before_-event called
before_-event (2) called
event called with value: 85
event returned value: None
""".lstrip()


def test_beforeafter_before_otherorder(capsys):
    mf = miniflask.init(
        ".modules",
        debug=True
    )
    mf.load(["setup_none_return", "beforeevent2", "beforeevent"])
    mf.parse_args([])
    captured = capsys.readouterr()
    mf.event.main()
    captured = capsys.readouterr()
    assert captured.out == """
before_-event (2) called
before_-event called
event called with value: 86
event returned value: None
""".lstrip()


def test_beforeafter_after(capsys):
    mf = miniflask.init(
        ".modules",
        debug=True
    )
    mf.load(["setup_none_return", "afterevent", "afterevent2"])
    mf.parse_args([])
    captured = capsys.readouterr()
    mf.event.main()
    captured = capsys.readouterr()
    assert captured.out == """
event called with value: 42
after_-event called
after_-event (2) called
event returned value: None
""".lstrip()


def test_beforeafter_after_otherorder(capsys):
    mf = miniflask.init(
        ".modules",
        debug=True
    )
    mf.load(["setup_none_return", "afterevent2", "afterevent"])
    mf.parse_args([])
    captured = capsys.readouterr()
    mf.event.main()
    captured = capsys.readouterr()
    assert captured.out == """
event called with value: 42
after_-event (2) called
after_-event called
event returned value: None
""".lstrip()


def test_beforeafter_all(capsys):
    mf = miniflask.init(
        ".modules",
        debug=True
    )
    mf.load(["setup_none_return", "beforeevent", "beforeevent2", "afterevent", "afterevent2"])
    mf.parse_args([])
    captured = capsys.readouterr()
    mf.event.main()
    captured = capsys.readouterr()
    assert captured.out == """
before_-event called
before_-event (2) called
event called with value: 85
after_-event called
after_-event (2) called
event returned value: None
""".lstrip()
