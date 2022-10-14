import re
from pathlib import Path
import miniflask  # noqa: E402


ansi_code_re = re.compile(r'(?:\x1B[@-_]|[\x80-\x9F])[0-?]*[ -/]*[@-~]')


def ansi_escape(s):
    return ansi_code_re.sub("", s)


def init_mf():
    mf = miniflask.init(
        ".modules",
        debug=True
    )
    mf.load("all")
    return mf


def test_nested_arguments_init(capsys):
    mf = init_mf()
    mf.parse_args([])

    mf.event.main()
    captured = capsys.readouterr()
    assert ansi_escape(captured.out) == """
modules.all
    ├── modules.otherdir.module2.submodule
    ├── modules.parentdir.module1
    ├── modules.parentdir.module2
    ╰── modules.parentdir.module3.submodule.subsubmodule
number 0
modules.otherdir.otherdir_var 0
modules.otherdir.module2.module2_var 1
modules.otherdir.module2.submodule.submodule_var 2
modules.parentdir.parentdir_var 3
modules.parentdir.module1.module1_var 4
modules.parentdir.module2.module2_var 5
modules.parentdir.module3.module3_var 6
modules.parentdir.module3.submodule.submodule_var 7
modules.parentdir.module3.submodule.subsubmodule.subsubmodule_var 8
""".lstrip()


def test_nested_arguments_level1_nesting(capsys):
    mf = init_mf()
    mf.parse_args([
        "--modules", "[",
            "--otherdir_var", "42", "--otherdir.module2_var", "43",  # noqa: E131
        "]",
        "--otherdir.module2", "[",
            "--submodule_var", "44",
        "]",
        "--modules.parentdir.", "[",
            "--parentdir_var", "45",
        "]",
    ])

    mf.event.main()
    captured = capsys.readouterr()
    assert ansi_escape(captured.out) == """
modules.all
    ├── modules.otherdir.module2.submodule
    ├── modules.parentdir.module1
    ├── modules.parentdir.module2
    ╰── modules.parentdir.module3.submodule.subsubmodule
number 0
modules.otherdir.otherdir_var 42
modules.otherdir.module2.module2_var 43
modules.otherdir.module2.submodule.submodule_var 44
modules.parentdir.parentdir_var 45
modules.parentdir.module1.module1_var 4
modules.parentdir.module2.module2_var 5
modules.parentdir.module3.module3_var 6
modules.parentdir.module3.submodule.submodule_var 7
modules.parentdir.module3.submodule.subsubmodule.subsubmodule_var 8
""".lstrip()


def test_nested_arguments_level2_nesting(capsys):
    mf = init_mf()
    mf.parse_args([
        "--modules", "[",
            "--otherdir", "[",  # noqa: E131
                "--otherdir_var", "42", "--module2_var", "43",  # noqa: E131
            "]",
            "--parentdir", "[",  # noqa: E131
                "--parentdir_var", "44",
            "]",
        "]",
    ])

    mf.event.main()
    captured = capsys.readouterr()
    assert ansi_escape(captured.out) == """
modules.all
    ├── modules.otherdir.module2.submodule
    ├── modules.parentdir.module1
    ├── modules.parentdir.module2
    ╰── modules.parentdir.module3.submodule.subsubmodule
number 0
modules.otherdir.otherdir_var 42
modules.otherdir.module2.module2_var 43
modules.otherdir.module2.submodule.submodule_var 2
modules.parentdir.parentdir_var 44
modules.parentdir.module1.module1_var 4
modules.parentdir.module2.module2_var 5
modules.parentdir.module3.module3_var 6
modules.parentdir.module3.submodule.submodule_var 7
modules.parentdir.module3.submodule.subsubmodule.subsubmodule_var 8
""".lstrip()


def test_nested_arguments_level3_nesting(capsys):
    mf = init_mf()
    mf.parse_args([
        "--modules", "[",
            "--otherdir", "[",  # noqa: E131
                "--otherdir_var", "42", "--module2_var", "43",  # noqa: E131
            "]",
            "--parentdir", "[",  # noqa: E131
                "--parentdir_var", "44",
                "--module1", "[",  # noqa: E131
                    "--module1_var", "45",  # noqa: E131
                "]",
                "--module2", "[",  # noqa: E131
                    "--module2_var", "46",  # noqa: E131
                "]",
                "--module3", "[",  # noqa: E131
                    "--module3_var", "47",
                    "--submodule.submodule_var", "48",
                    "--subsubmodule.subsubmodule_var", "49",  # noqa: E131
                "]",
            "]",
        "]",
    ])

    mf.event.main()
    captured = capsys.readouterr()
    assert ansi_escape(captured.out) == """
modules.all
    ├── modules.otherdir.module2.submodule
    ├── modules.parentdir.module1
    ├── modules.parentdir.module2
    ╰── modules.parentdir.module3.submodule.subsubmodule
number 0
modules.otherdir.otherdir_var 42
modules.otherdir.module2.module2_var 43
modules.otherdir.module2.submodule.submodule_var 2
modules.parentdir.parentdir_var 44
modules.parentdir.module1.module1_var 45
modules.parentdir.module2.module2_var 46
modules.parentdir.module3.module3_var 47
modules.parentdir.module3.submodule.submodule_var 48
modules.parentdir.module3.submodule.subsubmodule.subsubmodule_var 49
""".lstrip()


def test_nested_arguments_level5_nesting(capsys):
    mf = init_mf()
    mf.parse_args([
        "--modules", "[",
            "--otherdir", "[",  # noqa: E131
                "--otherdir_var", "42", "--module2_var", "43",  # noqa: E131
            "]",
            "--parentdir", "[",  # noqa: E131
                "--parentdir_var", "44",
                "--module1", "[",  # noqa: E131
                    "--module1_var", "45",  # noqa: E131
                "]",
                "--module2", "[",  # noqa: E131
                    "--module2_var", "46",  # noqa: E131
                "]",
                "--module3", "[",  # noqa: E131
                    "--module3_var", "47",
                    "--submodule", "[",  # noqa: E131
                        "--submodule_var", "48",  # noqa: E131
                        "--subsubmodule", "[",  # noqa: E131
                            "--subsubmodule_var", "49",  # noqa: E131
                        "]",  # noqa: E131
                    "]",  # noqa: E131
                "]",  # noqa: E131
            "]",  # noqa: E131
        "]",
    ])

    mf.event.main()
    captured = capsys.readouterr()
    assert ansi_escape(captured.out) == """
modules.all
    ├── modules.otherdir.module2.submodule
    ├── modules.parentdir.module1
    ├── modules.parentdir.module2
    ╰── modules.parentdir.module3.submodule.subsubmodule
number 0
modules.otherdir.otherdir_var 42
modules.otherdir.module2.module2_var 43
modules.otherdir.module2.submodule.submodule_var 2
modules.parentdir.parentdir_var 44
modules.parentdir.module1.module1_var 45
modules.parentdir.module2.module2_var 46
modules.parentdir.module3.module3_var 47
modules.parentdir.module3.submodule.submodule_var 48
modules.parentdir.module3.submodule.subsubmodule.subsubmodule_var 49
""".lstrip()
