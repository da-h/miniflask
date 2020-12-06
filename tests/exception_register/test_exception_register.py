from pathlib import Path
import pytest

import miniflask  # noqa: E402

mf = miniflask.init(
    module_dirs=str(Path(__file__).parent / "modules"),
    debug=True
)


def test_exception_register():
    with pytest.raises(miniflask.exceptions.RegisterError) as excinfo:
        mf.load("module1")
        mf.register_event("main", lambda: print("Main."))
        mf.run(argv=[])
