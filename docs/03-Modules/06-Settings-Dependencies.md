{theme=documentation}

\include{"../include.md"}



## Dependencies
In some cases global dependencies are needed.  


### Common Scopes
Groups of Modules often share variables. (Either by functionality, or, by conceptional classification).  
The method `register_defaults` has the optional argument `scope`. This variable defaults to the unique module id of the current module.
Overwriting the variable allows for shared or global settings.

**Example File:** `modules/module2/__init__.py`
```python
def register(mf):
    mf.set_sccope("common")
    mf.register_defaults({
        "varA": 42,
    })
```
This variable is identified in the global scope by `common.varA` instead of `module2.varA`.
**Note**: `mf.set_scope()` sets the scope globally (also in the event states).

**Alternative**:
```python
    mf.register_defaults({
        "varA": 42,
    }, scope="common")
```
This variable is identified in the global scope by `common.varA` instead of `module2.varA`.

\n



#### Global Settings
Global variables are just a special case of common scopes.

**Example File:** `modules/module2/__init__.py`
```python
def register(mf):
    mf.register_globals({
        "global_var": "this variable is global",
    })
```

**Note**: `mf.register_globals(...)` is equivalent to a call of `mf.register_defaults(...,scope="")`.  
\n



### Overwrite Settings of other Modules
A module can be used as a preset of other modules with predefined settings.  

**Example File:** `modules/module2/__init__.py`
```python
def register(mf):
    mf.load("module1") # module dependency
    mf.overwrite_defaults({
        "module1.variableB": "overwrites variable of module1",
    })
```

**Note**: `mf.overwrite_defaults(...)` is equivalent to a call of `mf.register_defaults(...,overwrite=True)`.  
In case any variable to overwrite is not known, the method will throw an Exception (`ValueError`).
**Note**: `mf.register_defaults` would also overwrite variables, however, it would not raise an Exception if the variable is not known.
\n


### Module Helpers
Each registered variable can be changed using cli arguments (see above). This behaviour can be suppressed as follows.

**Example File:** `modules/module2/__init__.py`
```python
def register(mf):

    class A():
        pass
    mf.register_helpers({
        "variable": A(), # cannot be changed using argument parsers
    })
```

**Note**: `mf.register_helpers(...)` is equivalent to a call of `mf.register_defaults(...,cliargs=False)`.  
\n


### Settings-Dependent Settings
On variable definition, all variables can be initialized using a lambda. This lambda retrieves the global `state`- and `event`-Objects to allow for settings dependdent settings

**Example File:** `modules/module2/__init__.py`
```python
def register(mf):
    mf.register_defaults({
        # unless anything is overwritten in the cli, this variable would be 420
        "variable": lambda state,event: state["module1.variableA"] * 10
    })
```
