{theme=documentation}

\include{"../include.md"}

\include{"../08-API/02-miniflask-Instance/08-register_defaults.md"}

# Register Module Settings:
 \shortdescr

\main


## Example
A typical used case are variables that can be overridden freely using CLI.  
Example file: `modules/module1/__init__.py`
\examples

## Overriding these using the CLI
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

## Overriding Booleans
For a boolean typed variable, the following arguments are possible:

| **Set to True**  | **Set to False** |
| ---------------- | ---------------- |
| \block[
```
--module.var
--module.var true
--module.var TrUe (well, boolean values are case insensitive)
--module.var yes
--module.var y
--module.var t
--module.var 1
```
] | \block[
```
--no-module.var
--module.var false
--module.var FalSE (well, boolean values are case-insensitive)
--module.var no
--module.var n
--module.var f
--module.var 0
```
] |

**Overriding Lists of basic types**:  
List arguments are just as easy as
```
--module.var 1 2 3 4 5
```



## Required Arguments
Set any basic data type (`str`, `bool`, `int`, `float`) or list of any basic data type as default value to register an argument that has to be specified by the CLI.
```python
def register(mf):
    mf.register_defaults({
        "variableA": int,
        "variableB": str,
        "variableC": bool,
        "variableD": [float] # only lists of same type are supported
    })
```




## Nested Arguments
Given nested modules, it is possible to group variables in the CLI using the folllowing syntax:
```python
--module1.submodule [ --var1 42 --var2 43 ]
```
or
```python
--module1 [ --submodule [ --var1 42 --var2 43 ] ]
```

These calls would translate to the following:
```
--module1.submodule.var1 42
--module1.submodule.var2 43
```




