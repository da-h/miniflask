{theme=documentation}

\include{"../include.md"}

# Module Dependencies {section-contentlist=False}
Presets, but fancy

## Default Modules
With `register_default_module` you can register a module to be loaded automatically, if a regular expression is not matched in the list of loaded moduls.

Typically, modules will be ordered in folderes based on distinct functionality.
In the following example, `module2` requires at least one module in the folder `some/folder/` to be loaded. If none such module was found by the end of the module loading-phase the default module will be loaded.

**Example File:** `modules/module2/__init__.py`
```python
def register(mf):
    mf.register_default_module("some\.folder\..*", "some.folder.defaultmodule")
```


## Plain Dependencies
With `load` you can load any other module if the current module was loaded.

**Example File:** `modules/module2/__init__.py`
```python
def register(mf):
    mf.load('some.othermodule')
    mf.load(['list.of.modules1', 'list.of.modules2'])
```

