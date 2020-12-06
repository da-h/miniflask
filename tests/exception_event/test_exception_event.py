from pathlib import Path

import miniflask  # noqa: E402

mf = miniflask.init(
    module_dirs=str(Path(__file__).parent / "modules"),
    debug=True
)


def test_exception_event():
    mf.load("module1")
    mf.register_event("main", lambda: print("Main."))
    mf.run(argv=[])
