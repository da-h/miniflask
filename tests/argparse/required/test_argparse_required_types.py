from pathlib import Path
import pytest

import miniflask  # noqa: E402

mf = miniflask.init(
    module_dirs=str(Path(__file__).parent / "modules"),
    debug=True
)


def test_types(capsys):
    mf.load("module1")
    error_message = """
The following argument is required: --modules.module1.int1
The following argument is required: --modules.module1.int2
The following argument is required: --modules.module1.float1
The following argument is required: --modules.module1.float2
The following argument is required: --modules.module1.float3
The following argument is required: --modules.module1.float4
The following argument is required: --modules.module1.float5
The following argument is required: --modules.module1.float6
The following argument is required: --modules.module1.enum1
The following argument is required: --modules.module1.str1
The following argument is required: --modules.module1.str2
The following argument is required: --modules.module1.str3
""".strip()
    with pytest.raises(SystemExit) as excinfo:
        mf.parse_args(argv=[])
    captured = capsys.readouterr()
    assert excinfo.value.args[0] == 2

    # we allow any order of the messages "The following argument is required ..."
    assert all(message in captured.err for message in error_message.split("\n"))
