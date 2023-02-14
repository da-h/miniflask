import miniflask  # noqa: E402


def init_mf():
    return miniflask.init(".modules", debug=True)


def test_parent_autoload_level1():
    mf = init_mf()
    mf.run(modules=["submodule"])
    assert "modules.parentdir.module3.submodule" in mf.modules_loaded
    assert "modules.parentdir.module3" in mf.modules_loaded
    assert len(mf.modules_loaded) == 2


def test_parent_autoload_level1_two_children():
    mf = init_mf()
    mf.load("submodule2")
    mf.run(modules=["submodule"])
    assert "modules.parentdir.module3.submodule2" in mf.modules_loaded
    assert "modules.parentdir.module3.submodule" in mf.modules_loaded
    assert "modules.parentdir.module3" in mf.modules_loaded
    assert len(mf.modules_loaded) == 3


def test_parent_autoload_skip():
    mf = init_mf()
    mf.run(modules=["submodule_without_autoload"])
    assert "modules.parentdir.module3.submodule_without_autoload" in mf.modules_loaded
    assert len(mf.modules_loaded) == 1


def test_parent_autoload_level2():
    mf = init_mf()
    mf.run(modules=["subsubmodule"])
    assert "modules.parentdir.module3.submodule.subsubmodule" in mf.modules_loaded
    assert "modules.parentdir.module3.submodule" in mf.modules_loaded
    assert "modules.parentdir.module3" in mf.modules_loaded
    assert len(mf.modules_loaded) == 3


def test_parent_autoload_level2_with_folder_in_between():
    mf = init_mf()
    mf.run(modules=["submodule_with_folder_in_between"])
    assert "modules.parentdir.module3.submodule_dir.submodule_with_folder_in_between" in mf.modules_loaded
    assert "modules.parentdir.module3" in mf.modules_loaded
    assert len(mf.modules_loaded) == 3
