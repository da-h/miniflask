from pathlib import Path
import miniflask  # noqa: E402


def init_mf():
    return miniflask.init(".modules", debug=True)


def test_default_module_byid_noload():
    mf = init_mf()
    mf.run(argv=[], modules=["otherdir.module2", "module6"])
    assert "modules.otherdir.module2" in mf.modules_loaded
    assert "modules.parentdir.module6" in mf.modules_loaded
    assert len(mf.modules_loaded) == 2


def test_default_module_byid_load():
    mf = init_mf()
    mf.run(argv=[], modules=["module6"])
    assert "modules.parentdir.module6" in mf.modules_loaded
    assert "modules.parentdir.module3" in mf.modules_loaded
    assert "modules.parentdir.module3.submodule" in mf.modules_loaded
    assert len(mf.modules_loaded) == 3


def test_default_module_byevent_noload():
    mf = init_mf()
    mf.run(argv=[], modules=["module1", "module7"])
    assert "modules.parentdir.module1" in mf.modules_loaded
    assert "modules.parentdir.module7" in mf.modules_loaded
    assert len(mf.modules_loaded) == 2


def test_default_module_byevent_load():
    mf = init_mf()
    mf.run(argv=[], modules=["module7"])
    assert "modules.parentdir.module7" in mf.modules_loaded
    assert "modules.parentdir.module3" in mf.modules_loaded
    assert "modules.parentdir.module3.submodule" in mf.modules_loaded
    assert len(mf.modules_loaded) == 3
