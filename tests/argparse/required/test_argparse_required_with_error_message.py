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
    mf.load("module1_with_error_message")
    error_message = """
    Missing CLI-arguments or unspecified variables during miniflask call.
        --modules.module1_with_error_message.int1
        Defined in line 38 in file 'modules/module1_with_error_message/__init__.py'.
        --modules.module1_with_error_message.int2
        Defined in line 38 in file 'modules/module1_with_error_message/__init__.py'.
        --modules.module1_with_error_message.float1
        Defined in line 38 in file 'modules/module1_with_error_message/__init__.py'.
        --modules.module1_with_error_message.float2
        Defined in line 38 in file 'modules/module1_with_error_message/__init__.py'.
        --modules.module1_with_error_message.float3
        Defined in line 38 in file 'modules/module1_with_error_message/__init__.py'.
        --modules.module1_with_error_message.float4
        Defined in line 38 in file 'modules/module1_with_error_message/__init__.py'.
        --modules.module1_with_error_message.float5
        Defined in line 38 in file 'modules/module1_with_error_message/__init__.py'.
        --modules.module1_with_error_message.float6
        Defined in line 38 in file 'modules/module1_with_error_message/__init__.py'.
        --modules.module1_with_error_message.bool1
        Defined in line 38 in file 'modules/module1_with_error_message/__init__.py'.
        --modules.module1_with_error_message.bool2
        Defined in line 38 in file 'modules/module1_with_error_message/__init__.py'.
        --modules.module1_with_error_message.enum1
        Defined in line 38 in file 'modules/module1_with_error_message/__init__.py'.
        --modules.module1_with_error_message.str1
        Defined in line 38 in file 'modules/module1_with_error_message/__init__.py'.
        --modules.module1_with_error_message.str2
        Defined in line 38 in file 'modules/module1_with_error_message/__init__.py'.
        --modules.module1_with_error_message.str3
        Defined in line 38 in file 'modules/module1_with_error_message/__init__.py'.

Did you forget something?
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
            assert error.strip() == expected.strip(), (error, expected)
