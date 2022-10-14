from pathlib import Path

import miniflask  # noqa: E402


def test_global_setup(capsys):
    mf = miniflask.init(
        "modules",
        debug=True
    )

    mf.load("globalvar")
    mf.parse_args([
    ])
    captured = capsys.readouterr()
    mf.event.print_all()
    captured = capsys.readouterr()
    assert captured.out == """
globalvar: 1
""".lstrip()


def test_global_cli_override(capsys):
    mf = miniflask.init(
        "modules",
        debug=True
    )

    mf.load("globalvar")
    mf.parse_args([
        "--globalvar", "42",
    ])
    captured = capsys.readouterr()
    mf.event.print_all()
    captured = capsys.readouterr()
    assert captured.out == """
globalvar: 42
""".lstrip()


def test_override(capsys):
    mf = miniflask.init(
        "modules",
        debug=True
    )

    mf.load(["globalvar", "globalvar_override"])
    mf.parse_args([])
    captured = capsys.readouterr()
    mf.event.print_all()
    captured = capsys.readouterr()
    assert captured.out == """
globalvar: 11
""".lstrip()


def test_override_cli(capsys):
    mf = miniflask.init(
        "modules",
        debug=True
    )

    mf.load(["globalvar", "globalvar_override"])
    mf.parse_args([
        "--globalvar", "111",
    ])
    captured = capsys.readouterr()
    mf.event.print_all()
    captured = capsys.readouterr()
    assert captured.out == """
globalvar: 111
""".lstrip()
