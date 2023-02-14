import pytest
import miniflask  # noqa: E402


def init_mf():
    return miniflask.init(".modules", debug=True)


def test_shortid():
    mf = init_mf()
    mf.run(argv=[], modules=["module1"])
    assert "modules.parentdir.module1" in mf.modules_loaded
    assert len(mf.modules_loaded) == 1


def test_partial_id():
    mf = init_mf()
    mf.run(argv=[], modules=["modules.module1"])
    assert "modules.parentdir.module1" in mf.modules_loaded
    assert len(mf.modules_loaded) == 1


def test_partial_id_2():
    mf = init_mf()
    mf.run(argv=[], modules=["parentdir.module1"])
    assert "modules.parentdir.module1" in mf.modules_loaded
    assert len(mf.modules_loaded) == 1


def test_full_id():
    mf = init_mf()
    mf.run(argv=[], modules=["modules.parentdir.module1"])
    assert "modules.parentdir.module1" in mf.modules_loaded
    assert len(mf.modules_loaded) == 1


def test_shortid_error():
    mf = init_mf()
    with pytest.raises(ValueError) as excinfo:
        mf.run(argv=[], modules=["module2"])
        assert "is not unique" in str(excinfo.value)
    assert len(mf.modules_loaded) == 0


def test_partial_id_error():
    mf = init_mf()
    with pytest.raises(ValueError) as excinfo:
        mf.run(argv=[], modules=["modules.module2"])
        assert "is not unique" in str(excinfo.value)
    assert len(mf.modules_loaded) == 0


def test_partial_id_3():
    mf = init_mf()
    mf.run(argv=[], modules=["modules.otherdir.module2"])
    assert "modules.otherdir.module2" in mf.modules_loaded
    assert len(mf.modules_loaded) == 1


def test_partial_id_4():
    mf = init_mf()
    mf.run(argv=[], modules=["modules.otherdir.module2"])
    assert "modules.otherdir.module2" in mf.modules_loaded
    assert len(mf.modules_loaded) == 1


def test_partial_id_5():
    mf = init_mf()
    mf.run(argv=[], modules=["parentdir.module2"])
    assert "modules.parentdir.module2" in mf.modules_loaded
    assert len(mf.modules_loaded) == 1


def test_partial_id_6():
    mf = init_mf()
    mf.run(argv=[], modules=["parentdir.module2"])
    assert "modules.parentdir.module2" in mf.modules_loaded
    assert len(mf.modules_loaded) == 1
