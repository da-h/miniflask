from pathlib import Path
import miniflask  # noqa: E402


def init_mf():
    base_path = Path(__file__).parent / "modules"
    return miniflask.init(module_dirs=[base_path / "main", base_path / "replace", base_path / "replace2"], debug=True)


def check(check, out, mf):
    assert check in out, "Checking for string '%s' in output: '%s'" % (check, out)


def test_register_as_setup(capsys):
    mf = init_mf()
    mf.run(argv=[], modules=["main.module_loads_other"], call="off")
    capsys.readouterr()
    mf.event.main()
    assert len(mf.modules_loaded) == 3
    captured = capsys.readouterr()
    out = captured.out
    check("main/module_loads_other", out, mf)
    check("main/module_with_submodule", out, mf)
    check("main/module_with_submodule/submodule", out, mf)


def test_register_as_replace_module_loader_module(capsys):
    mf = init_mf()
    mf.run(argv=[], modules=["replace.module_loads_other", "main.module_loads_other"], call="off")
    capsys.readouterr()
    mf.event.main()
    assert len(mf.modules_loaded) == 3
    captured = capsys.readouterr()
    out = captured.out
    check("replace/module_loads_other", out, mf)
    check("main/module_with_submodule", out, mf)
    check("main/module_with_submodule/submodule", out, mf)


def test_register_as_replace_module_loader_module_test_reload(capsys):
    mf = init_mf()
    mf.run(argv=[], modules=["replace.module_loads_other", "main.module_loads_other"], call="off")
    capsys.readouterr()
    mf.event.main()
    assert len(mf.modules_loaded) == 3
    captured = capsys.readouterr()
    out = captured.out
    check("replace/module_loads_other", out, mf)
    check("main/module_with_submodule", out, mf)
    check("main/module_with_submodule/submodule", out, mf)


def test_register_as_replace_submodule(capsys):
    mf = init_mf()
    mf.run(argv=[], modules=["replace.submodule", "main.module_loads_other"], call="off")
    capsys.readouterr()
    mf.event.main()
    assert len(mf.modules_loaded) == 3
    captured = capsys.readouterr()
    out = captured.out
    check("main/module_loads_other", out, mf)
    check("main/module_with_submodule", out, mf)
    check("replace/module_with_submodule/submodule", out, mf)


def test_register_as_replace_module(capsys):
    mf = init_mf()
    mf.run(argv=[], modules=["replace.module_with_submodule", "main.module_loads_other"], call="off")
    capsys.readouterr()
    mf.event.main()
    assert len(mf.modules_loaded) == 3
    captured = capsys.readouterr()
    out = captured.out
    check("main/module_loads_other", out, mf)
    check("replace/module_with_submodule", out, mf)
    check("main/module_with_submodule/submodule", out, mf)


def test_register_as_replace_module_and_submodule(capsys):
    mf = init_mf()
    mf.run(argv=[], modules=["replace2.module_with_submodule", "main.module_loads_other"], call="off")
    capsys.readouterr()
    mf.event.main()
    assert len(mf.modules_loaded) == 3
    captured = capsys.readouterr()
    out = captured.out
    check("main/module_loads_other", out, mf)
    check("replace2/module_with_submodule", out, mf)
    check("replace2/module_with_submodule/submodule", out, mf)
