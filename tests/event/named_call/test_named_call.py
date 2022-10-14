from pathlib import Path
import miniflask  # noqa: E402


def test_named_call(capsys):
    mf = miniflask.init(
        ".modules",
        debug=False
    )

    mf.load(["module1", "module2"])
    mf.parse_args([])
    for module, result in mf.event.named_call("main").items():
        print(module, result)
    captured = capsys.readouterr()
    assert "\n".join(captured.out.split("\n")[2:]) == """
modules.module1 1337
modules.module2 2345
""".lstrip()
