from pathlib import Path
import miniflask  # noqa: E402


def init_mf():
    return miniflask.init(".modules", debug=True)


def test_register_event_during_event(capsys):
    mf = init_mf()
    mf.run(argv=[], modules=["register_event_during_event"])
    captured = capsys.readouterr()
    out = """
test 0
test 1
added to test 1
"""
    assert out in captured.out
