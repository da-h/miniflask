from pathlib import Path
import miniflask  # noqa: E402
import pytest


def test_helper_setup(capsys):
    mf = miniflask.init(
        ".modules",
        debug=True
    )

    mf.load("helpervar")
    mf.parse_args([])
    captured = capsys.readouterr()
    mf.event.print_all()
    captured = capsys.readouterr()
    assert captured.out == """
modules.helpervar.helpervar: 1
""".lstrip()


def test_helper_overwrite(capsys):
    mf = miniflask.init(
        ".modules",
        debug=True
    )

    mf.load(["helpervar", "helpervar_override"])
    mf.parse_args([])
    captured = capsys.readouterr()
    mf.event.print_all()
    captured = capsys.readouterr()
    assert captured.out == """
modules.helpervar.helpervar: 2
""".lstrip()


def test_helper_cli(capsys):
    mf = miniflask.init(
        ".modules",
        debug=True
    )

    mf.load("helpervar")
    with pytest.raises(ValueError):
        mf.parse_args([
            "--helpervar", "11"
        ])
        mf.event.print_all()


def test_helper_cli_after_overwrite(capsys):
    mf = miniflask.init(
        ".modules",
        debug=True
    )

    mf.load(["helpervar", "helpervar_override"])
    with pytest.raises(ValueError):
        mf.parse_args([
            "--helpervar", "11"
        ])
        mf.event.print_all()
