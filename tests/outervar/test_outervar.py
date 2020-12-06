from pathlib import Path

import miniflask  # noqa: E402

mf = miniflask.init(
    module_dirs=str(Path(__file__).parent / "modules"),
    debug=True
)


def test_outervar():
    event = mf.event
    mf.load("module1")
    var_a = 42
    mf.event.main()
    del event, var_a  # now unused
