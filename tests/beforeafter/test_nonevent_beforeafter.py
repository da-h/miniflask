from pathlib import Path
import miniflask  # noqa: E402


mf = miniflask.init(
    module_dirs=str(Path(__file__).parent / "modules"),
    debug=True
)


def test_directcall_beforeafter(capsys):
    mf.load("directcalls")
    # mf.run(modules=["directcalls"], argv=[], call="")
    mf.parse_args([])
    captured = capsys.readouterr()
    mf.event.main()
    captured = capsys.readouterr()
    assert captured.out == """
before_-event called
event called
after_-event called
""".lstrip()
