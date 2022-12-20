import pytest

import miniflask  # noqa: E402

mf = miniflask.init(
    ".modules",
    debug=True
)


def test_module_a():
    mf.run(modules=["a"], argv=[])


def test_module_b():
    with pytest.raises(miniflask.exceptions.RegisterError):
        mf.run(modules=["b"], argv=[])
