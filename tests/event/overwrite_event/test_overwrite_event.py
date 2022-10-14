from pathlib import Path
import miniflask  # noqa: E402


def test_overwrite_setup(capsys):
    mf = miniflask.init(
        ".modules",
        debug=False
    )

    mf.load(["module1"])
    mf.parse_args([])
    captured = capsys.readouterr()
    mf.event.main()
    captured = capsys.readouterr()
    assert captured.out == """
before main event
main event
after main event
""".lstrip()


def test_overwrite(capsys):
    mf = miniflask.init(
        ".modules",
        debug=False
    )

    mf.load(["module1", "main_overwrite"])
    mf.parse_args([])
    captured = capsys.readouterr()
    mf.event.main()
    captured = capsys.readouterr()
    assert captured.out == """
before main event
overwritten main event
after main event
""".lstrip()


def test_overwrite_during_event(capsys):
    mf = miniflask.init(
        ".modules",
        debug=False
    )

    mf.load(["module1", "main_overwrite_during_event"])
    mf.parse_args([])
    captured = capsys.readouterr()
    mf.event.main()
    mf.event.init()
    mf.event.main()
    captured = capsys.readouterr()
    assert captured.out == """
before main event
main event
after main event
overwrites event during init-event
before main event
overwritten main event during event
after main event
""".lstrip()


def test_overwrite_with_attached(capsys):
    mf = miniflask.init(
        ".modules",
        debug=False
    )

    mf.load(["module1", "main_overwrite_with_attached"])
    mf.parse_args([])
    captured = capsys.readouterr()
    mf.event.main()
    captured = capsys.readouterr()
    assert captured.out == """
overwritten main event and removed attached as well
""".lstrip()
