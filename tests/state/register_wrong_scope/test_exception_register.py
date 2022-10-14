from pathlib import Path
import pytest

import miniflask  # noqa: E402

mf = miniflask.init(
    ".modules",
    debug=True
)


def test_exception_register():
    with pytest.raises(miniflask.exceptions.RegisterError):
        mf.load("module1")
        mf.register_event("main", lambda: print("Main."), unique=False)
        mf.run(argv=[])
