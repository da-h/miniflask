from pathlib import Path

import miniflask  # noqa: E402

mf = miniflask.init(
    module_dirs=str(Path(__file__).parent / "modules"),
)


def test_exception_register():
    mf.load("module1")
    mf.register_event("main", lambda: print("Main."))
    mf.run(argv=[])
