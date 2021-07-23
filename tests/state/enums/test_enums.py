from pathlib import Path

import miniflask  # noqa: E402

mf = miniflask.init(
    module_dirs=str(Path(__file__).parent / "modules"),
    debug=True
)


def test_enum():
    mf.run(
        modules=["module1"],
        argv=["--module1.sizerequired", "SMALL",
              "--module1.sizelist", "MEDIUM", "SMALL"]
    )
