from pathlib import Path

import miniflask  # noqa: E402

mf = miniflask.init(
    module_dirs=str(Path(__file__).parent / "modules"),
    debug=True
)


def test_mf_python():

    mf.load("moduleunique")
    from modules.moduleunique import func  # noqa: F401,E402  # pylint: disable=import-outside-toplevel

    a = 0
    for _ in range(10000000):
        a += func(mf.event, mf.state, 42)
