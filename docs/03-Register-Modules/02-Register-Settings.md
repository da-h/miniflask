{theme=documentation}

\include{"../include.md"}

# Register Module Settings:
Register Variables For the Module

**Example File:** `modules/module1/__init__.py`
```python
def register(mf):
    mf.register_defaults({
        "variableA": 42,
        "variableB": "Hello",
        "variableC": True
        "variableD": [1,2,3,5,8,13] # only lists of same type are supported
    })
```

---

### Argument Parser
Whenever we load `module1`, e.g. by using 
```shell
python main.py module1
```
we also load these variables into the argument parser of miniflask.  
For the example above, we list all arguments that can be used for `module1`:
```shell
> python main.py module1 -h
usage: main.py modulelist [optional arguments]

optional arguments:
  -h, --help            show this help message and exit
  --module1.variableA 	int
  --module1.variableB 	string
  --module1.variableC
  --no-module1.variableC
  --module1.variableD	[int]
```

Thus, to turn `variableC` off, we can just add `--no-module1.variableC` to the above command.

### Global Settings / Overwrite Settings of other Modules
In some cases global dependencies are needed. For instance, a module can be used as a preset of modules with predefined settings (see below).  
In this case, we can call `register_defaults` using the argument `all`.
**Note:** Multiple calls to `register_defaults` are allowed.

**Example File:** `modules/module2/__init__.py`
```python
def register(mf):
    mf.register_defaults({
        "module1.variableB": "overwrites variable of module1",
        "global_var": "this variable is global",
    }, all=True)
```
\n

## Note {.alert}
For the call
```shell
python main.py module1,module2
```
the variable `module1.variableB` is **overwritten**.

For the call
```shell
python main.py module2,module1
```
the variable `module1.variableB` is **not overwritten**.
