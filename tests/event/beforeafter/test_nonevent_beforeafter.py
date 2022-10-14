from pathlib import Path
import miniflask  # noqa: E402


mf = miniflask.init(
    ".modules",
    debug=True
)


def test_directcall_beforeafter(capsys):
    mf.load("directcalls")
    mf.parse_args([])
    captured = capsys.readouterr()
    mf.event.main()
    captured = capsys.readouterr()
    assert captured.out == """
before_-event called
event called
after_-event called
""".lstrip()
