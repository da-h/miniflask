{theme=documentation}

\include{"../include.md"}

# Register Modules {section-contentlist=False}
Telling MiniFlask what exists.

### Initialize Miniflask
We initialize MiniFlask using the argument `module_dirs`. This tells MiniFlask where all modules are defined. Besides that, the module directory can be organized as you wish.


**Example** `main.py`
```python
import miniflask

# initialize miniflask
mf = miniflask.init(module_dirs="./modules")
mf.parse_args()
```

**Note**: `parse_args` requires some modules to be loaded from cli. However, using `optional=True` miniflask does not require the user to load any modules anymore. (This makes sense, if your script that loads miniflask itself loads some modules per defaulft.)

**Example**  
For instance, we could organize the folder `./modules` like this:
```shell
> ls
main.py
modules/
    module1/__init__.py
      ...  /.module
    module2/__init__.py
      ...  /.module
      ...  /.noshortid
    subfolder1/module3/__init__.py
        ...   /  ...  /.module
    subfolder1/module4/__init__.py
        ...   /  ...  /.module
    ... and so on ...
```



### Module Declaration
- A MiniFlask module needs to serve two files: 
    - `__init__.py` containing a method called `register(mf)`.  
        The method `register(mf)` is called whenever a module is loaded.
        It's purpose is to tell miniflask in which way the module is to be used.
    - `.module` *(empty file)*
- every such module can be referenced in two ways:
    |            | short identifier | unique identifier |
    | ---------- | -------------------- | --------------------- |
    | description           | directory name | directory identifier |
    | example               | `module1`,\n `module3`,\n `module4` | `module1`,\n `module2`,\n `subfolder1.module3`,\n `subfolder1.module4` |
    | call                  | `python main.py module3` | `python main.py subfolder1.module3` |
    | availability             | **not available if** \block[
- two modules share the same short identifiers
- module-folder contains the file `.noshortid`
    ] | always |
    
