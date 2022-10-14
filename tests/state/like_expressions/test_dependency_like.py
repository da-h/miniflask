from pathlib import Path
import miniflask  # noqa: E402


mf = miniflask.init(
    "modules",
    debug=True
)


def test_like_depedencies(capsys):
    mf.load(["actual_data", "dependency_one", "dependency_two"])
    mf.parse_args([])
    captured = capsys.readouterr()
    mf.event.main()
    captured = capsys.readouterr()
    assert captured.out == """
foo: 11
foo2: 112
foo3: 13
foo4: 4
""".lstrip()
