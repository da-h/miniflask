from pathlib import Path

import miniflask  # noqa: E402

mf = miniflask.init(
    "modules",
    debug=True
)


def test_temporary():
    mf.run(modules=["dosomething"], argv=[])
