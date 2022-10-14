from pathlib import Path
import pytest
import miniflask  # noqa: E402


mf = miniflask.init(
    "modules",
    debug=True
)


def test_directcall_beforeafter():
    mf.load("circularlike")
    with pytest.raises(RecursionError):
        mf.parse_args([])
