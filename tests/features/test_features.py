from pathlib import Path

import miniflask  # noqa: E402

mf = miniflask.init(
    module_dirs=str(Path(__file__).parent / "modules"),
    debug=True
)


def test_module_a():
    mf.run(modules=["a"], argv=[])


def test_module_b():
    mf.run(modules=["b"], argv=[])
