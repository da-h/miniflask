from pathlib import Path

import miniflask  # noqa: E402

mf = miniflask.init(
    module_dirs=str(Path(__file__).parent / "modules"),
)


def test_outervar():
    event = mf.event
    mf.load("module1")
    varA = 42
    mf.event.main()
    del event, varA  # now unused
