from pathlib import Path
import miniflask  # noqa: E402


mf = miniflask.init(
    module_dirs=str(Path(__file__).parent / "modules"),
    debug=True
)


def test_dataclass():
    mf.run(
        modules=["module1"],
        argv=[]
    )
