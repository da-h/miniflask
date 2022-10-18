import pytest
from setup import setup
from miniflask.exceptions import RegisterError


def test_lambda_arguments():
    mf = setup()
    mf.load("lambdaarguments_module1")
    assert mf.state_registrations["modules.lambdaarguments_module1.var1"][-1].depends_on == []
    assert mf.state_registrations["modules.lambdaarguments_module1.var1"][-1].depends_alternatives == {}
    assert mf.state_registrations["modules.lambdaarguments_module1.var2"][-1].depends_on == ["var1"]
    assert mf.state_registrations["modules.lambdaarguments_module1.var2"][-1].depends_alternatives == {}
    assert mf.state_registrations["modules.lambdaarguments_module1.var3"][-1].depends_on == ["var2", "var1"]
    assert mf.state_registrations["modules.lambdaarguments_module1.var3"][-1].depends_alternatives == {}
    assert mf.state_registrations["modules.lambdaarguments_module1.var4"][-1].depends_on == ["var1"]
    assert mf.state_registrations["modules.lambdaarguments_module1.var4"][-1].depends_alternatives == {}
    assert mf.state_registrations["modules.lambdaarguments_module1.var5"][-1].depends_on == ["var1", "var3"]
    assert mf.state_registrations["modules.lambdaarguments_module1.var5"][-1].depends_alternatives == {"var1": ["var3"]}
    assert mf.state_registrations["modules.lambdaarguments_module1.var6"][-1].depends_on == ["var1", "var2", "var3", "var4"]
    assert mf.state_registrations["modules.lambdaarguments_module1.var6"][-1].depends_alternatives == {"var1": ["var3", "var4"], "var2": ["var3", "var4"]}


def test_circular_dependency_errors():
    mf = setup()
    mf.load("circulardep_error_selfdependency")
    mf.load("circulardep_error_module1")
    mf.load("circulardep_error_module2")
    mf.load("circulardep_error_module3")
    with pytest.raises(RegisterError) as excinfo:
        mf.parse_args([])
    assert """
The registration of state variables has led to the following errors:

Error: Circular dependencies found! (A → B means "A depends on B")

modules.circulardep_error_selfdependency.foo
    → modules.circulardep_error_selfdependency.foo
modules.circulardep_error_selfdependency.foo2
    → modules.circulardep_error_selfdependency.foo2bar
    → modules.circulardep_error_selfdependency.foo2
modules.circulardep_error_selfdependency.foo3
    → modules.circulardep_error_selfdependency.foo3barbar
    → modules.circulardep_error_selfdependency.foo3bar
    → modules.circulardep_error_selfdependency.foo3
modules.circulardep_error_module1.foo
    → modules.circulardep_error_module2.foo
    → modules.circulardep_error_module3.foo
    → modules.circulardep_error_module1.foo
modules.circulardep_error_module1.bar
    → modules.circulardep_error_module2.bar
    → modules.circulardep_error_module3.bar
    → modules.circulardep_error_module3.bar2
    → modules.circulardep_error_module2.bar2
    → modules.circulardep_error_module1.bar2
    → modules.circulardep_error_module3.bar2
""".strip() == str(excinfo.value).strip()


def test_dependency_unresolved():
    mf = setup()
    mf.load("unresolveddep_error_dependencynotfound")
    with pytest.raises(RegisterError) as excinfo:
        mf.parse_args([])
    assert """
The registration of state variables has led to the following errors:

Error: Dependency not found! (A → B means "A depends on B")

modules.unresolveddep_error_dependencynotfound.foo
    → varnotfound ← not found
""".strip() == str(excinfo.value).strip()


def test_working_dependencies(capsys):
    mf = setup()
    mf.load("settings")
    mf.load("dependencychain_module1")
    mf.load("dependencychain_module2")
    mf.load("dependencychain_module3")
    mf.load("dependencychain_module4")
    mf.parse_args([])
    captured = capsys.readouterr()
    mf.event.print_all()
    captured = capsys.readouterr()
    assert captured.out == """
modules.dependencychain_module1.foo1: 100
modules.dependencychain_module1.foo2: 200
modules.dependencychain_module1.foo3: 600
modules.dependencychain_module1.foo4: 31105924806303
modules.dependencychain_module1.foo5: 24000
modules.dependencychain_module2.foo1: 100
modules.dependencychain_module2.foo2: 200
modules.dependencychain_module2.foo3: 300
modules.dependencychain_module2.foo4: 10368641602101
modules.dependencychain_module2.foo5: 6000
modules.dependencychain_module3.foo1: 101
modules.dependencychain_module3.foo2: 200
modules.dependencychain_module3.foo3: 300
modules.dependencychain_module3.foo4: 400
modules.dependencychain_module3.foo5: 6000
modules.dependencychain_module4.foo5: 500
""".lstrip()


def test_alternative_dependencies(capsys):
    mf = setup()
    mf.load("settings")
    mf.load("dependencychain_module1")
    mf.load("dependencychain_module2")
    mf.load("dependencychain_module3")
    mf.parse_args([])
    captured = capsys.readouterr()
    mf.event.print_all()
    captured = capsys.readouterr()
    assert captured.out == """
modules.dependencychain_module1.foo1: 100
modules.dependencychain_module1.foo2: 200
modules.dependencychain_module1.foo3: 600
modules.dependencychain_module1.foo4: 31105924806303
modules.dependencychain_module1.foo5: 24
modules.dependencychain_module2.foo1: 100
modules.dependencychain_module2.foo2: 200
modules.dependencychain_module2.foo3: 300
modules.dependencychain_module2.foo4: 10368641602101
modules.dependencychain_module2.foo5: 6
modules.dependencychain_module3.foo1: 101
modules.dependencychain_module3.foo2: 200
modules.dependencychain_module3.foo3: 300
modules.dependencychain_module3.foo4: 400
modules.dependencychain_module3.foo5: 6
""".lstrip()


def test_overwritten_dependencies(capsys):
    mf = setup()
    mf.load("settings")
    mf.load("dependencychain_module1")
    mf.load("dependencychain_module2")
    mf.load("dependencychain_module3")
    mf.parse_args([
        "--dependencychain_module1.foo1", "101",
        "--dependencychain_module2.foo2", "201",
        "--dependencychain_module2.foo3", "301",
        "--dependencychain_module3.foo4", "401",
    ])
    captured = capsys.readouterr()
    mf.event.print_all()
    captured = capsys.readouterr()
    assert captured.out == """
modules.dependencychain_module1.foo1: 101
modules.dependencychain_module1.foo2: 201
modules.dependencychain_module1.foo3: 602
modules.dependencychain_module1.foo4: 31495718496396
modules.dependencychain_module1.foo5: 24
modules.dependencychain_module2.foo1: 100
modules.dependencychain_module2.foo2: 201
modules.dependencychain_module2.foo3: 301
modules.dependencychain_module2.foo4: 10498572832132
modules.dependencychain_module2.foo5: 6
modules.dependencychain_module3.foo1: 101
modules.dependencychain_module3.foo2: 200
modules.dependencychain_module3.foo3: 300
modules.dependencychain_module3.foo4: 401
modules.dependencychain_module3.foo5: 6
""".lstrip()
