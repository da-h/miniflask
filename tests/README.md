## Tests via pytest

### Requirements

Make sure the current development version of miniflask is installed:
```
pip install -e ../
```

pytest and all needed requirements must be installed as well:
```
pip install pytest
pip install -r ../requirements.txt
```

### Quick Start Guide

- Files must start with `test_` or end with `_test`.
- Methods to be tested need to be prefixed with `test_`. 

You can see a list of all "registered" tests with
```
pytest --collect-only
``` 

or simply run all tests
```
pytest
```

#### Some notes

- pytest executes all tests with the initial working directory (e.g. `tests`).
    Therefore, relative module imports in miniflask down work and the absolute path is used (e.g. `str(Path(__file__).parent / "modules")` to add the `modules` directory as module).
- pytest adds additional arguments to the execution call.
    Therefore, pass the `argv` to miniflask manually (e.g. `mf.run(argv=[])`). 


### More information

- [Full pytest documentation](https://docs.pytest.org/)
