{theme=documentation}

\include{"../include.md"}

# Register Modules {section-contentlist=False}
Telling MiniFlask what exists.

### Initialize Miniflask
\include{"../08-API/02-miniflask-Instance/01-miniflask.init.md"}

\main


**Example Launch File**  
```python
import miniflask

# tell miniflask where to look for modules
mf = miniflask.init(module_dirs="./modules")

# parse CLI-args & run the main event
mf.run()
```

Project structure may be very project specific. Miniflask allows various way to organize your projects.
Other possibilities are to define modules directly or to specify multiple distinct folders that contain miniflask modules.

\examples

### What is a Module?
> A miniflask module is a self-contained functional unit with a persistent variable store. In principle, it's a singleton class.

**Module Declaration**
- **A MiniFlask module is a folder that contains at least these two files**: 
    - `__init__.py` containing a method called `register(mf)`.  
        The method `register(mf)` is called whenever a module is loaded.
        It's purpose is to tell miniflask in which way the module is to be used.
    - `.module` *(empty file)*


### Unique & Short Module Identifiers
When working with miniflask modules we will want to reference modules uniquely.
The unique module identifier is just the path to the folder (starting with the base directory defined during initialization), where the module seperator is a dot (`.`).


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

Further, we initialized miniflask using the line
```py
mf = miniflask.init({
    "mods": "./modules",
})
```
by specifying the name `mods` for our main repository contained in the folder `./modules/`.


Every module in this repository can now be referenced in two ways: \block[
    | **Type**       | unique module identifier | (short) module identifier | 
    | ---------- | -------------------- | --------------------- |
    | **Description**           | unique identification by specifying the whole module path | any subset of the unique identifier if only one module matches that description | 
    | **Availability**          | Always  | Not available if \block[
- two modules would share the same short identifier
- module-folder contains the file `.noshortid`
    ] |
    | **Example**               | `module1`,\n (has no shorter id)\n `subfolder1.module3` or also `mods.module3`,\n `subfolder1.module4` or also `mods.module4`| `mods.module1`\n`mods.module2`\n`mods.subfolder1.module3`\n`mods.subfolder1.module4` |
    ]
