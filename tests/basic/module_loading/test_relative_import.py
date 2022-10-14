from pathlib import Path
import miniflask  # noqa: E402


def init_mf():
    return miniflask.init(".modules", debug=True)


def test_passive_submodule_import():
    mf = init_mf()
    mf.run(argv=[], modules=["module3"])
    assert "modules.parentdir.module3" in mf.modules_loaded
    assert "modules.parentdir.module3.submodule" in mf.modules_loaded
    assert len(mf.modules_loaded) == 2


def test_active_submodule_import():
    mf = init_mf()
    mf.run(argv=[], modules=["submodule"])
    assert "modules.parentdir.module3" in mf.modules_loaded
    assert "modules.parentdir.module3.submodule" in mf.modules_loaded
    assert len(mf.modules_loaded) == 2


def test_relative_import():
    mf = init_mf()
    mf.run(argv=[], modules=["module4"])
    assert "modules.parentdir.module4" in mf.modules_loaded
    assert "modules.parentdir.module3" in mf.modules_loaded
    assert "modules.parentdir.module3.submodule" in mf.modules_loaded
    assert len(mf.modules_loaded) == 3


def test_relative_import_2():
    mf = init_mf()
    mf.run(argv=[], modules=["module5"])
    assert "modules.parentdir.module5" in mf.modules_loaded
    assert "modules.otherdir.module2" in mf.modules_loaded
    assert len(mf.modules_loaded) == 2
