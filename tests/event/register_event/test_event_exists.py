from pathlib import Path
import miniflask  # noqa: E402


def init_mf():
    return miniflask.init("modules", debug=True)


def test_event_exists_false():
    mf = init_mf()
    mf.run(argv=[], modules=[])
    assert not mf.event.exists("main")
    assert not mf.event.exists("add_test")
    assert not mf.event.exists("sub_test")


def test_event_exists_true():
    mf = init_mf()
    mf.run(argv=[], modules=["register_event_during_event"])
    assert mf.event.exists("main")
    assert mf.event.exists("add_test")
    assert not mf.event.exists("sub_test")
