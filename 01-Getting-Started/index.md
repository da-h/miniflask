{theme=documentation}

\include{"../include.md"}
MiniFlask {section-contentlist=False}
=========

# Geting Started {section-contentlist=False}
# Miniflask is a **small** research-oriented **plugin**-engine for **python**.

> A long time ago in a galaxy full of plugin-engines ...


Quick Start
===========

For a quick look into miniflask, just install it using
```shell
pip install miniflask
```


Short Example
=============


**Module Definition**  
Let's start a new project first by creating a new directory:
```shell
> ls
main.py
modules/
    module1/__init__.py
    module2/__init__.py
    module1/__init__.py
```

Let's define a simple module, `modules/module1/__init__.py`:
```python
def main(state, event):
    print("main event called by module1")

def register(mf):
    mf.register_event('main', main)
```

Let's define another module, `modules/module2/__init__.py`:
```python
def main(state, event):
    print("main event called by module2")
    print("it uses a variable var:", state["var"])

def register(mf):
    mf.register_defaults({
        "var": 42
    })
    mf.register_event('main', main)
```



Our main.py looks like this:
```python
import miniflask

# initialize miniflask
mf = miniflask.init(module_dirs="./modules")
mf.parse_args()

# check if all requested modules are loaded
if not mf.halt_parse:

    # call event "main" if exists
    if hasattr(mf.event, 'main'):
        mf.event.main()
    else:
        print("There is nothing to do.")
```


**Usage**:  
Now, we can use our program in the following ways:
```sh
> python main.py
There is nothing to do.
```

```sh
> python main.py module1
main event called by module1
```

```sh
> python main.py module2,module1
main event called by module2
it uses a variable var: 42
main event called by module1
```

```sh
> python main.py module2,module1 --module2.var 9001
main event called by module2
it uses a variable var: 9001
main event called by module1
```
