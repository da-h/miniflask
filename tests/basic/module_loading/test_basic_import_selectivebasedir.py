import os
import miniflask  # noqa: E402

# to test relative imports, we have to assume that the base-directory can be anywhere, for pytests sake
relpath = os.path.relpath(os.path.dirname(__file__), os.getcwd())


def init_mf():
    return miniflask.init(".modules.parentdir.module3", ".modules.otherdir.module2", debug=True)


def test_setup():
    mf = init_mf()
    mf.run(argv=[], modules=["miniflask.modules"])
    assert sorted([m for m in mf.modules_avail.keys() if not m.startswith("miniflask")]) == [
        'module2',
        'module3',
        'module3.submodule',
        'module3.submodule.subsubmodule',
        'module3.submodule2',
        'module3.submodule_dir.submodule_with_folder_in_between',
        'module3.submodule_without_autoload'
    ]
