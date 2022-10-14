from pathlib import Path
import miniflask  # noqa: E402


mf = miniflask.init(
    ".modules",
    debug=True
)


def test_dataclass():
    mf.run(
        modules=["module1"],
        argv=[]
    )
