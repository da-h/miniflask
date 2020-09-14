{theme=documentation}

\include{"../include.md"}

# State
Global Variables, but Fancy. ;)

Every event gets called with a state-Object as its first argument.
This is the modules **local** and **persistent** variable scope.

**Example file**: `./modules/module1/__init__.py`
```python
def dosomething(state, event):
    print(state["var"])
    print()
    state["var"] *= 500
    print(state["var"])

def register(mf):
    mf.register_defaults({
        "var": 42
    })
    mf.register_event('dosomething',dosomething)
```

## Use/change the global variable scope
Every variable defined by plain `register_defaults` gets prepended by the modules *unique id*.
The global scope of the programs state can also be used explicitly.

{.alert}
This, however should of course be used with caution, as it breaks the modularity of the code.

**Example file**: `./modules/module2/__init__.py`
```python
def dosomethingelse(state, event):

    # this uses the variables of any global
    print(state.all["modules1.var"])
    print()
    state.all["modules1.var"] *= 500
    print(state.all["modules1.var"])

def register(mf):
    mf.register_event('dosomethingelse',dosomethingelse)
```


## Use/change other modules' variable scope
Instead to the above solution using `state.all` you can also get a version of state with another scope.

{.alert}
This makes sense for inheritance like module dependencies.

**Example file**: `./modules/module2/__init__.py`
```python
def dosomethingelse(state, event):
    state = state.scope("module1")

    # this uses the variables of module1, even though used in module2
    print(state["var"])
    print()
    state["var"] *= 500
    print(state["var"])

def register(mf):
    mf.register_event('dosomethingelse',dosomethingelse)
```


## Temporary Changes
Instead to change the state before/after an event, you can use the following construction using `state.temporary`:

```python
def dosomething(state, event):
    print("in event", state["variable"])

def main(state, event):

    print("before event", state["variable"])
    with state.temporary({
        "variable": 42:
    }):
        event.dosomething()
    print("after event", state["variable"])

def register(mf):
    mf.register_defaults({
        "variable": 0
    })
    mf.register_event('dosomething',dosomething)
    mf.register_event('main',main)
```


