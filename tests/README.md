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

### More information

- [Full pytest documentation](https://docs.pytest.org/)
