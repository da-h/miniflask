from pathlib import Path

import miniflask  # noqa: E402

mf = miniflask.init(
    module_dirs=str(Path(__file__).parent / "modules"),
    debug=True
)


def test_mf_python():

    mf.load("module1")
    from modules.module1 import func as func2  # noqa: F401,E402

    def func(x):
        return x

    a = 0
    for i in range(10000000):
        a += func(42)
