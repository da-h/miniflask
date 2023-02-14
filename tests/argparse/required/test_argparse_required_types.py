import re
import miniflask  # noqa: E402

mf = miniflask.init(
    ".modules",
    debug=True
)


def escape_ansi(line):
    ansi_escape = re.compile(r'(?:\x1B[@-_]|[\x80-\x9F])[0-?]*[ -/]*[@-~]')
    return ansi_escape.sub('', line)


def test_types():
    mf.load("module1")
    error_message = """
    Missing CLI-arguments or unspecified variables during miniflask call.
        --modules.module1.int1
        Defined in line 38 in file 'modules/module1/__init__.py'.
        --modules.module1.int2
        Defined in line 38 in file 'modules/module1/__init__.py'.
        --modules.module1.float1
        Defined in line 38 in file 'modules/module1/__init__.py'.
        --modules.module1.float2
        Defined in line 38 in file 'modules/module1/__init__.py'.
        --modules.module1.float3
        Defined in line 38 in file 'modules/module1/__init__.py'.
        --modules.module1.float4
        Defined in line 38 in file 'modules/module1/__init__.py'.
        --modules.module1.float5
        Defined in line 38 in file 'modules/module1/__init__.py'.
        --modules.module1.float6
        Defined in line 38 in file 'modules/module1/__init__.py'.
        --modules.module1.bool1
        Defined in line 38 in file 'modules/module1/__init__.py'.
        --modules.module1.bool2
        Defined in line 38 in file 'modules/module1/__init__.py'.
        --modules.module1.enum1
        Defined in line 38 in file 'modules/module1/__init__.py'.
        --modules.module1.str1
        Defined in line 38 in file 'modules/module1/__init__.py'.
        --modules.module1.str2
        Defined in line 38 in file 'modules/module1/__init__.py'.
        --modules.module1.str3
        Defined in line 38 in file 'modules/module1/__init__.py'.
""".strip().split("\n")
    try:
        mf.parse_args(argv=[])
    except ValueError as excinfo:
        errtext = escape_ansi(str(excinfo)).split("\n")

    assert len(error_message) == len(errtext)
    for expected, error in zip(error_message, errtext):

        # we ignore the folder from which pytest is run
        # (this would change the relative file path of the error message)
        if "'" in expected:
            start, end = expected.strip().split("'", 1)
            assert error.strip().startswith(start)
            assert error.strip().endswith(end)
        else:
            assert error.strip() == expected.strip()
