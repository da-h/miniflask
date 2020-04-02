MiniFlask
=========
[![python-3 badge](https://img.shields.io/pypi/v/miniflask?style=flat-square)](https://pypi.org/project/miniflask/)
[![python-3 badge](https://img.shields.io/pypi/pyversions/miniflask?style=flat-square)](https://pypi.org/project/miniflask/)
[![CI build status](https://github.com/da-h/miniflask/workflows/Deploy/badge.svg)](https://github.com/da-h/miniflask/actions?query=workflow%3ADeploy)

Miniflask is a **small** research-oriented **plugin**-engine for **python**.
> A long time ago in a galaxy full of plugin-engines ...


Quick Start
-----------

For a quick look into miniflask, just install it using
```bash
# until we deploy to pip:
cd [your project dir]
git clone https://github.com/da-h/miniflask miniflask_git
ln -s miniflask_git/src/miniflask .

# in a future release of course:
pip install miniflask
```

[Read the Documentation](https://da-h.github.io/miniflask)
----------------------

Short Example
-------------


**Module Definition**  
Let's start a new project first by creating a new directory:
```bash
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

License
-------
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](https://opensource.org/licenses/MIT) - See [LICENSE](LICENSE) for details.  
