from pathlib import Path
import pytest
import miniflask  # noqa: E402


mf = miniflask.init(
    module_dirs=str(Path(__file__).parent / "modules"),
    debug=True
)


def test_directcall_beforeafter():
    mf.load("circularlike")
    with pytest.raises(RecursionError):
        mf.parse_args([])
