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
modules.module1.int1: [42]
modules.module1.int2: [-42]
modules.module1.float1: [2.345]
modules.module1.float2: [-2.345]
modules.module1.float3: [0.0]
modules.module1.float4: [-0.0]
modules.module1.float5: [10000000.0]
modules.module1.float6: [-10000000.0]
modules.module1.bool1: [True]
modules.module1.bool2: [False]
modules.module1.enum1: [<SIZE.MEDIUM: 1>]
modules.module1.str1: ['']
modules.module1.str2: ['abcd1234']
modules.module1.str3: ['αβγδ∀⇐Γ∂']
""".lstrip()
