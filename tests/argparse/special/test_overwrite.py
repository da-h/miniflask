from pathlib import Path
import pytest
import miniflask  # noqa: E402


def test_setup(capsys):
    mf = miniflask.init(
        module_dirs=str(Path(__file__).parent / "modules"),
        debug=True
    )

    mf.load(["defaults"])
    mf.parse_args([
        "--var_default_override_twice_and_cli", "1114"
    ])
    captured = capsys.readouterr()
    mf.event.print_all()
    captured = capsys.readouterr()
    assert captured.out == """
modules.defaults.var_default: 1
modules.defaults.var_default_override: 2
modules.defaults.var_default_override_twice: 3
modules.defaults.var_default_override_twice_and_cli: 1114
""".lstrip()


def test_override(capsys):
    mf = miniflask.init(
        module_dirs=str(Path(__file__).parent / "modules"),
        debug=True
    )

    mf.load(["defaults", "defaults_override"])
    mf.parse_args([
        "--var_default_override_twice_and_cli", "1114"
    ])
    captured = capsys.readouterr()
    mf.event.print_all()
    captured = capsys.readouterr()
    assert captured.out == """
modules.defaults.var_default: 1
modules.defaults.var_default_override: 12
modules.defaults.var_default_override_twice: 13
modules.defaults.var_default_override_twice_and_cli: 1114
""".lstrip()


def test_override_twice(capsys):
    mf = miniflask.init(
        module_dirs=str(Path(__file__).parent / "modules"),
        debug=True
    )

    mf.load(["defaults", "defaults_override", "defaults_override_twice"])
    mf.parse_args([
        "--var_default_override_twice_and_cli", "1114"
    ])
    captured = capsys.readouterr()
    mf.event.print_all()
    captured = capsys.readouterr()
    assert captured.out == """
modules.defaults.var_default: 1
modules.defaults.var_default_override: 12
modules.defaults.var_default_override_twice: 113
modules.defaults.var_default_override_twice_and_cli: 1114
""".lstrip()


def test_override_conflict():
    mf = miniflask.init(
        module_dirs=str(Path(__file__).parent / "modules"),
        debug=True
    )

    mf.load(["defaults", "defaults2", "defaults_override"])
    with pytest.raises(miniflask.exceptions.RegisterError):
        mf.parse_args([])
    mf.event.print_all()


def test_override_scoped_absolute():
    mf = miniflask.init(
        module_dirs=str(Path(__file__).parent / "modules"),
        debug=True
    )

    mf.load(["defaults", "defaults2", "defaults_override_scoped_absolute"])
    mf.parse_args([])
    mf.event.print_all()


def test_override_scoped_relative():
    mf = miniflask.init(
        module_dirs=str(Path(__file__).parent / "modules"),
        debug=True
    )

    mf.load(["defaults", "defaults2", "defaults_override_scoped_relative"])
    mf.parse_args([])
    mf.event.print_all()
