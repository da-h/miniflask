import miniflask  # noqa: E402


def test_none(capsys):
    mf = miniflask.init(
        ".modules",
        debug=True
    )

    mf.load("module1")
    mf.parse_args()
    captured = capsys.readouterr()

    mf.event.print_all()
    captured = capsys.readouterr()
    assert captured.out == """
modules.module1.int1: None
modules.module1.int2: []
modules.module1.float1: None
modules.module1.float2: None
modules.module1.float3: None
modules.module1.float4: None
modules.module1.float5: None
modules.module1.float6: []
modules.module1.bool1: None
modules.module1.bool2: []
modules.module1.enum1: None
modules.module1.enum2: []
modules.module1.str1: None
modules.module1.str2: []
modules.module1.str3: None\n""".lstrip()


def test_space(capsys):
    mf = miniflask.init(
        ".modules",
        debug=True
    )

    mf.load("module1")
    mf.parse_args([
        "--int1", "1337",
        "--int2", "-1337",
        "--float1", "1.234",
        "--float2", "-1.234",
        "--float3", "-0.0",
        "--float4", "0.0",
        "--float5", "3e5",
        "--float6", "-3e5",
        "--bool1", "False",
        "--bool2", "True",
        "--enum1", "small",
        "--enum2", "medium",
        "--str1", "abcd1234",
        "--str2", "αβγδ∀⇐Γ∂",
        "--str3", ""
    ])
    captured = capsys.readouterr()

    mf.event.print_all()
    captured = capsys.readouterr()
    assert captured.out == """
modules.module1.int1: 1337
modules.module1.int2: [-1337]
modules.module1.float1: 1.234
modules.module1.float2: -1.234
modules.module1.float3: -0.0
modules.module1.float4: 0.0
modules.module1.float5: 300000.0
modules.module1.float6: [-300000.0]
modules.module1.bool1: False
modules.module1.bool2: [True]
modules.module1.enum1: SIZE.SMALL
modules.module1.enum2: [<SIZE.MEDIUM: 1>]
modules.module1.str1: abcd1234
modules.module1.str2: ['αβγδ∀⇐Γ∂']
modules.module1.str3: \n""".lstrip()


def test_equal(capsys):
    mf = miniflask.init(
        ".modules",
        debug=True
    )

    mf.load("module1")
    mf.parse_args([
        "--int1=1337",
        "--int2=-1337",
        "--float1=1.234",
        "--float2=-1.234",
        "--float3=-0.0",
        "--float4=0.0",
        "--float5=3e5",
        "--float6=-3e5",
        "--bool1=False",
        "--bool2=True",
        "--enum1=small",
        "--enum2=medium",
        "--str1=abcd1234",
        "--str2=αβγδ∀⇐Γ∂",
        "--str3="
    ])
    captured = capsys.readouterr()

    mf.event.print_all()
    captured = capsys.readouterr()
    assert captured.out == """
modules.module1.int1: 1337
modules.module1.int2: [-1337]
modules.module1.float1: 1.234
modules.module1.float2: -1.234
modules.module1.float3: -0.0
modules.module1.float4: 0.0
modules.module1.float5: 300000.0
modules.module1.float6: [-300000.0]
modules.module1.bool1: False
modules.module1.bool2: [True]
modules.module1.enum1: SIZE.SMALL
modules.module1.enum2: [<SIZE.MEDIUM: 1>]
modules.module1.str1: abcd1234
modules.module1.str2: ['αβγδ∀⇐Γ∂']
modules.module1.str3: \n""".lstrip()
