from pathlib import Path

import miniflask  # noqa: E402

mf = miniflask.init(
    module_dirs=str(Path(__file__).parent / "modules"),
    debug=True
)


def test_mf_event_nonunique():
    event = mf.event
    mf.load("modulenonunique")

    a = 0
    for i in range(10000000):
        a += event.func(42)[0]
