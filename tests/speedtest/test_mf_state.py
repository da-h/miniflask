from pathlib import Path

import miniflask  # noqa: E402

mf = miniflask.init(
    module_dirs=str(Path(__file__).parent / "modules"),
    debug=True
)


def test_mf_state():
    mf.load("moduleunique")
    event = mf.event

    a = 0
    for i in range(10000000):
        a += event.get_state_var("a")
