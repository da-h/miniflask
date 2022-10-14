from pathlib import Path
from os.path import dirname
import pytest
import miniflask  # noqa: E402


def init_mf():
    return miniflask.init("modules", debug=True)


all_modules = ["otherdir", "otherdir.module2", "parentdir", "parentdir.module1", "parentdir.module2", "parentdir.module3", "parentdir.module3.submodule", "parentdir.module3.submodule.subsubmodule"]


# check if state fetches the right local variable
def test_state_implicit_local(explicit=False):
    modules = all_modules
    mf = init_mf()
    mf.run(argv=[], modules=["all"])

    results = mf.event.get_local_var(explicit=explicit)
    assert len(results) == len(modules)
    for m, filename in zip(modules, results):
        m = m.replace(".", "/")
        dir = dirname(filename)
        assert dir.endswith(m), "'%s' should end with '%s'" % (dir, m)


# check if state fetches the right local variable
def test_state_implicit_global(explicit=False):
    modules = all_modules
    mf = init_mf()
    mf.run(argv=[], modules=["all"])

    results = mf.event.get_global_var(explicit=explicit)
    assert len(results) == len(modules)
    global_m = "all"
    for _, filename in zip(modules, results):
        dir = dirname(filename)
        assert dir.endswith(global_m), "'%s' should end with '%s'" % (dir, global_m)


# check if state fetches the right child variable
def test_state_implicit_fuzzychild(explicit=False):
    modules = all_modules
    mf = init_mf()
    mf.run(argv=[], modules=["all"])

    results = mf.event.get_fuzzy_child_var(explicit=explicit)
    assert len(results) == len(modules)
    global_m = "module3/submodule/subsubmodule/fuzzychild"
    for filename in results:
        dir = dirname(filename)
        assert dir.endswith(global_m), "'%s' should end with '%s'" % (dir, global_m)


# check if state fetches the local variable of the parent
def test_state_implicit_parent(explicit=False):
    modules = [m for m in all_modules if "." in m]

    mf = init_mf()
    mf.run(argv=[], modules=["all"])

    # check wether state fetches the right local variable
    results = mf.event.get_parent_var(explicit=explicit)
    assert len(results) == len(modules)
    for m, filename in zip(modules, results):
        m = m.replace(".", "/")
        dir = dirname(filename)
        # assert not dir.endswith(m), "%s shouldn't end with %s" % (dir, m)
        m = "/".join(m.split("/")[:-1])
        assert dir.endswith(m), "'%s' should end with '%s'" % (dir, m)


# check if state fetches the local variable of the parents parent
def test_state_implicit_parent_parent(explicit=False):
    modules = ["parentdir.module3.submodule", "parentdir.module3.submodule.subsubmodule"]

    mf = init_mf()
    mf.run(argv=[], modules=["all"])

    # check wether state fetches the right local variable
    results = mf.event.get_parent_parent_var(explicit=explicit)
    assert len(results) == len(modules)
    for m, filename in zip(modules, results):
        m = m.replace(".", "/")
        dir = dirname(filename)
        # assert not dir.endswith(m), "%s shouldn't end with %s" % (dir, m)
        m = "/".join(m.split("/")[:-2])
        assert dir.endswith(m), "'%s' should end with '%s'" % (dir, m)


# check also explicit version ( .var )
def test_state_explicit_local():
    test_state_implicit_local(explicit=True)


# check also explicit version ( ..var )
def test_state_explicit_parent():
    test_state_implicit_parent(explicit=True)


# check also explicit version ( ...var )
def test_state_explicit_parent_parent():
    test_state_implicit_parent_parent(explicit=True)


# check also explicit version ( var, for global variable var )
def test_state_explicit_global():
    test_state_implicit_global(explicit=True)


# check also explicit version for fuzzy child variable
def test_state_explicit_fuzzychild():
    test_state_implicit_fuzzychild(explicit=True)


# check if state raises error for nonunique fuzzy variables
def test_state_error_multiple_fuzzy_vars():
    modules = all_modules

    for module in modules:
        mf = init_mf()
        mf.run(argv=[], modules=[module, "fuzzychild", "varisnonunique"])

        with pytest.raises(miniflask.exceptions.StateKeyError) as excinfo:
            mf.event.get_fuzzy_child_nonunique_var()
        assert "is not unique" in str(excinfo.value)
        assert "Found 2 variables" in str(excinfo.value)


# check if state raises error if variable not found
def test_state_error_var_not_found():
    modules = all_modules

    for module in modules:
        mf = init_mf()
        mf.run(argv=[], modules=[module])

        with pytest.raises(miniflask.exceptions.StateKeyError) as excinfo:
            mf.event.get_nonexistent_var()
        assert "not known" in str(excinfo.value)


if __name__ == "__main__":
    test_state_implicit_local()
    test_state_implicit_parent()
    test_state_implicit_parent_parent()
    test_state_implicit_global()
    test_state_implicit_fuzzychild()
    test_state_explicit_local()
    test_state_explicit_parent()
    test_state_explicit_parent_parent()
    test_state_explicit_global()
    test_state_explicit_fuzzychild()
    test_state_error_multiple_fuzzy_vars()
    test_state_error_var_not_found()
