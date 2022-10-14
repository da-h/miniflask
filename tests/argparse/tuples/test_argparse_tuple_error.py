from pathlib import Path
import pytest

import miniflask  # noqa: [E402]


def test_tuple_len_error(capsys):
    mf = miniflask.init(
        ".modules",
        debug=True
    )

    mf.load("module1")
    with pytest.raises(SystemExit):
        mf.parse_args([
            "--float4", "0.0"
        ])
    captured = capsys.readouterr()
    with open("/tmp/test", "w") as f:
        f.write(captured.err)
    assert captured.err.split("\n", 1)[1] == """
pytest: error: argument --modules.module1.float4: expected 4 arguments
""".lstrip()
