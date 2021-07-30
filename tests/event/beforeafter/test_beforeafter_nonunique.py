from pathlib import Path
import miniflask  # noqa: E402


def test_beforeafter_setup(capsys):
    mf = miniflask.init(
        module_dirs=str(Path(__file__).parent / "modules"),
        debug=True
    )
    mf.load("setup_multiple")
    mf.parse_args([])
    captured = capsys.readouterr()
    mf.event.main()
    captured = capsys.readouterr()
    assert captured.out == """
event called with value: 42
event called with value: 42
event called with value: 42
event called with value: 42
event returned value: [42, 42, 42, 42]
""".lstrip()


def test_beforeafter_before(capsys):
    mf = miniflask.init(
        module_dirs=str(Path(__file__).parent / "modules"),
        debug=True
    )
    mf.load(["setup_multiple", "beforeevent", "beforeevent2"])
    mf.parse_args([])
    captured = capsys.readouterr()
    mf.event.main()
    captured = capsys.readouterr()
    assert captured.out == """
before_-event called
before_-event (2) called
event called with value: 85
event called with value: 85
event called with value: 85
event called with value: 85
event returned value: [85, 85, 85, 85]
""".lstrip()


def test_beforeafter_after(capsys):
    mf = miniflask.init(
        module_dirs=str(Path(__file__).parent / "modules"),
        debug=True
    )
    mf.load(["setup_multiple", "afterevent_multiple", "afterevent2_multiple"])
    mf.parse_args([])
    captured = capsys.readouterr()
    mf.event.main()
    captured = capsys.readouterr()
    assert captured.out == """
event called with value: 42
event called with value: 42
event called with value: 42
event called with value: 42
after_-event called
after_-event (2) called
event returned value: [1, 44, 87, 130]
""".lstrip()


def test_beforeafter_before_and_after(capsys):
    mf = miniflask.init(
        module_dirs=str(Path(__file__).parent / "modules"),
        debug=True
    )
    mf.load(["setup_multiple", "beforeevent", "beforeevent2", "afterevent_multiple", "afterevent2_multiple"])
    mf.parse_args([])
    captured = capsys.readouterr()
    mf.event.main()
    captured = capsys.readouterr()
    assert captured.out == """
before_-event called
before_-event (2) called
event called with value: 85
event called with value: 85
event called with value: 85
event called with value: 85
after_-event called
after_-event (2) called
event returned value: [1, 87, 173, 259]
""".lstrip()
