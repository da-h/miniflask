from pathlib import Path
import miniflask  # noqa: E402


def test_overwrite_setup(capsys):
    mf = miniflask.init(
        module_dirs=str(Path(__file__).parent / "modules"),
        debug=False
    )

    mf.load(["module1"])
    mf.parse_args([])
    captured = capsys.readouterr()
    mf.event.main()
    captured = capsys.readouterr()
    assert captured.out == """
main event
""".lstrip()


def test_overwrite(capsys):
    mf = miniflask.init(
        module_dirs=str(Path(__file__).parent / "modules"),
        debug=False
    )

    mf.load(["module1", "main_overwrite"])
    mf.parse_args([])
    captured = capsys.readouterr()
    mf.event.main()
    captured = capsys.readouterr()
    assert captured.out == """
overwritten main event
""".lstrip()


def test_overwrite_during_event(capsys):
    mf = miniflask.init(
        module_dirs=str(Path(__file__).parent / "modules"),
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
main event
overwrites event during init-event
overwritten main event during event
""".lstrip()
