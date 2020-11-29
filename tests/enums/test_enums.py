from pathlib import Path

import miniflask  # noqa: E402

mf = miniflask.init(
    module_dirs=str(Path(__file__).parent / "modules"),
)


def test_enum_argument():
    mf.run(
        modules=["module1"],
        argv=["--module1.sizerequired", "SMALL"]
    )


def test_enum_list():
    mf.run(
        modules=["module1"],
        argv=["--module1.sizelist", "SMALL", "MEDIUM", "LARGE"]
    )
