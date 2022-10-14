from pathlib import Path

import miniflask  # noqa: [E402]

mf = miniflask.init(
    ".modules",
    debug=True
)


def test_types(capsys):
    with capsys.disabled():
        mf.load("module1")
    mf.event.print_all()
    captured = capsys.readouterr()
    assert captured.out == """
modules.module1.int1: (42,)
modules.module1.int2: (-42, 0)
modules.module1.float1: (2.345,)
modules.module1.float2: (-2.345, 2.345)
modules.module1.float3: (-2.345, 0, 2.345)
modules.module1.float4: (-2.345, 0, 1, 2.345)
modules.module1.float5: (-2.345, -1, 0, 1, 2.345)
modules.module1.float6: (1000000.0,)
modules.module1.bool1: (True,)
modules.module1.bool2: (False, True)
modules.module1.enum1: (<SIZE.MEDIUM: 1>, <SIZE.SMALL: 0>, <SIZE.MEDIUM: 1>)
modules.module1.str1: ('',)
modules.module1.str2: ('abcd1234', '')
modules.module1.str3: ('αβγδ∀⇐Γ∂', '', '')
""".lstrip()
