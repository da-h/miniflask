{theme=documentation}

\include{"../include.md"}

# Module Dependencies {section-contentlist=False}
Presets for modules

## Default Modules
With `register_default_module` you can register a module to be loaded automatically, if a regular expression is not matched in the list of loaded moduls.

Typically, modules will be ordered in folderes based on distinct functionality.
In the following example, `module2` requires at least one module in the folder `some/folder/` to be loaded. If none such module was found by the end of the module loading-phase the default module will be loaded.

**Example File:** `modules/module2/__init__.py`
```python
def register(mf):
    mf.register_default_module("some.folder.defaultmodule", required_id="some\folder\.*")
```
It is also possible to load a module only if a required event does not exist.

```python
def register(mf):
    mf.register_default_module("some.folder.defaultmodule", required_event="this_event_is_required")
```

## Plain Dependencies
With `load` you can load any other module if the current module was loaded.

**Example File:** `modules/module2/__init__.py`
```python
def register(mf):
    mf.load('some.othermodule')
    mf.load(['list.of.modules1', 'list.of.modules2'])
```
## Child modules

It is possible to load a module as a child of another module.

```python
mf.load_as_child(module1,module2)
```

..loads module2 as a child of module1. module2 then uses the identifier `module1.module2`. The variables of the second module then have to be accessed through the new global identifier. 

{.alert}
Note: Main methods of child modules will not be called automatically.

