from pathlib import Path

import miniflask  # noqa: E402

mf = miniflask.init(
    module_dirs=str(Path(__file__).parent / "modules"),
    debug=True
)


class event():

    @classmethod
    def func(cls, x):
        return x


def test_mf_class():

    mf.load("moduleunique")

    a = 0
    for i in range(10000000):
        a += event.func(42)
