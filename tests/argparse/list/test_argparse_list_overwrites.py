from pathlib import Path

import miniflask  # noqa: [E402]


def test_space(capsys):
    mf = miniflask.init(
        module_dirs=str(Path(__file__).parent / "modules"),
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
        "--str1", "abcd1234",
        "--str2", "αβγδ∀⇐Γ∂",
        "--str3", ""
    ])
    captured = capsys.readouterr()

    mf.event.print_all()
    captured = capsys.readouterr()
    assert captured.out == """
modules.module1.int1: [1337]
modules.module1.int2: [-1337]
modules.module1.float1: [1.234]
modules.module1.float2: [-1.234]
modules.module1.float3: [-0.0]
modules.module1.float4: [0.0]
modules.module1.float5: [300000.0]
modules.module1.float6: [-300000.0]
modules.module1.bool1: [False]
modules.module1.bool2: [True]
modules.module1.enum1: [<SIZE.SMALL: 0>]
modules.module1.str1: ['abcd1234']
modules.module1.str2: ['αβγδ∀⇐Γ∂']
modules.module1.str3: ['']
""".lstrip()


def test_equal(capsys):
    mf = miniflask.init(
        module_dirs=str(Path(__file__).parent / "modules"),
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
        "--str1=abcd1234",
        "--str2=αβγδ∀⇐Γ∂",
        "--str3="
    ])
    captured = capsys.readouterr()

    mf.event.print_all()
    captured = capsys.readouterr()
    assert captured.out == """
modules.module1.int1: [1337]
modules.module1.int2: [-1337]
modules.module1.float1: [1.234]
modules.module1.float2: [-1.234]
modules.module1.float3: [-0.0]
modules.module1.float4: [0.0]
modules.module1.float5: [300000.0]
modules.module1.float6: [-300000.0]
modules.module1.bool1: [False]
modules.module1.bool2: [True]
modules.module1.enum1: [<SIZE.SMALL: 0>]
modules.module1.str1: ['abcd1234']
modules.module1.str2: ['αβγδ∀⇐Γ∂']
modules.module1.str3: ['']
""".lstrip()


def test_bool_int(capsys):
    mf = miniflask.init(
        module_dirs=str(Path(__file__).parent / "modules"),
        debug=True
    )

    mf.load("module1")
    mf.parse_args([
        "--bool1=0",
        "--bool2=1",
    ])
    captured = capsys.readouterr()

    mf.event.print_bool()
    captured = capsys.readouterr()
    assert captured.out == """
modules.module1.bool1: [False]
modules.module1.bool2: [True]
""".lstrip()


def test_bool_yesno(capsys):
    mf = miniflask.init(
        module_dirs=str(Path(__file__).parent / "modules"),
        debug=True
    )

    mf.load("module1")
    mf.parse_args([
        "--bool1=no",
        "--bool2=yes",
    ])
    captured = capsys.readouterr()

    mf.event.print_bool()
    captured = capsys.readouterr()
    assert captured.out == """
modules.module1.bool1: [False]
modules.module1.bool2: [True]
""".lstrip()


def test_bool_tf(capsys):
    mf = miniflask.init(
        module_dirs=str(Path(__file__).parent / "modules"),
        debug=True
    )

    mf.load("module1")
    mf.parse_args([
        "--bool1=f",
        "--bool2=t",
    ])
    captured = capsys.readouterr()

    mf.event.print_bool()
    captured = capsys.readouterr()
    assert captured.out == """
modules.module1.bool1: [False]
modules.module1.bool2: [True]
""".lstrip()


def test_bool_truefalse(capsys):
    mf = miniflask.init(
        module_dirs=str(Path(__file__).parent / "modules"),
        debug=True
    )

    mf.load("module1")
    mf.parse_args([
        "--bool1=false",
        "--bool2=true",
    ])
    captured = capsys.readouterr()

    mf.event.print_bool()
    captured = capsys.readouterr()
    assert captured.out == """
modules.module1.bool1: [False]
modules.module1.bool2: [True]
""".lstrip()
