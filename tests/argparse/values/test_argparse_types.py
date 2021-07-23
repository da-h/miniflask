from pathlib import Path

import miniflask  # noqa: E402

mf = miniflask.init(
    module_dirs=str(Path(__file__).parent / "modules"),
    debug=True
)


def test_types(capsys):
    with capsys.disabled():
        mf.load("module1")
    mf.event.print_all()
    captured = capsys.readouterr()
    assert captured.out == """
int1: 42
int2: -42
float1: 2.345
float2: -2.345
float3: 0.0
float4: -0.0
float5: 10000000.0
float6: -10000000.0
bool1: True
bool2: False
enum1: SIZE.MEDIUM
str1: """.lstrip() + """
str2: abcd1234
str3: αβγδ∀⇐Γ∂
"""
