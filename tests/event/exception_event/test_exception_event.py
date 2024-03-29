import pytest
import miniflask  # noqa: E402


def test_exception_event():
    mf = miniflask.init(
        ".modules",
        debug=False
    )

    mf.load("module1")
    mf.parse_args([])
    with pytest.raises(ValueError):
        mf.event.main()


def test_exception_event_debugmode():
    mf = miniflask.init(
        ".modules",
        debug=True
    )

    mf.load("module1")
    mf.parse_args([])
    with pytest.raises(ValueError):
        mf.event.main()


def test_exception_event_unique_register():
    mf = miniflask.init(
        ".modules",
        debug=False
    )

    with pytest.raises(miniflask.exceptions.RegisterError):
        mf.load(["module1", "module2"])


def test_exception_event_unique_register_debugmode():
    mf = miniflask.init(
        ".modules",
        debug=True
    )

    with pytest.raises(miniflask.exceptions.RegisterError):
        mf.load(["module1", "module2"])
