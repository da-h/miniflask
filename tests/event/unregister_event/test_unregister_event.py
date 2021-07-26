import pytest
from pathlib import Path
import miniflask  # noqa: E402


def test_unregister():
    mf = miniflask.init(
        module_dirs=str(Path(__file__).parent / "modules"),
        debug=False
    )

    mf.load(["module1", "main_unregister"])
    mf.parse_args([])
    with pytest.raises(AttributeError):
        mf.event.main()
