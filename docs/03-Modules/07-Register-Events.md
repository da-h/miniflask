{theme=documentation}



# Register Events


\include{"../include.md"}

Module function can be attached to hooks so that they are called automatically upon reaching the specified hook. Events can be attached to a hook when registering an event.

### Minimal Example
**Example File:** `modules/module1/__init__.py`
```python
def main(state, event):
    print("This is the main-event of module1")

def register(mf):
    mf.register_event('main', main)
```

**Example File:** `modules/module2/__init__.py`
```python
def main(state, event):
    print("This is the main-event of module2")

def notneeded(state, event, someargument):
    print("Event was called. Argument:" + someargument)
    return "notneeded() result"

def register(mf):
    mf.register_event('main', main, unique=False)
    mf.register_event('notneeded', notneeded, unique=False)
```

**Example File:** `main.py`
```python
import miniflask

# initialize miniflask
mf = miniflask.init(module_dirs="./modules")
state, event = mf.state, mf.event
mf.parse_args()
mf.event.main()
```

---

### Register Events
Every Event-Method can be called with two arguments `state` and `event` (**only as first two arguments**), **plus** the arguments that are passed when the event is called.

There are two type of events:

**Unique**:  
Can be defined by exactly one module.\n Typically unique events are called and are expected to return exactly one result.  
`mf.register_event('eventname', fn, unique=True)`

**Nonunique**  
Can be defined by arbitrary many module. The results of all such events of loaded modules are collected and returned in a list.  
`mf.register_event('eventname', fn, unique=False)`

### Transform events (before/after event call)

Sometimes, it is useful to call an event just before or after a given event *event0*. This is useful when observing what the effects of *event0* are or when applying a modifyier before *event0*. This can be done without defining a new event by simply registering the event in the following way:

` mf.register_event('before_event0', fn)` or `mf.register_event('after_event0',fn)`.

In its definition, the transform function takes all arguments of the original function followed by any supplementary arguments for the transformation call. The transform function returns the arguments of the original function.

```python
def before_blub(state, event, *args, **kwargs):
	#*args are the original arguments of blub
	#**kwargs are supplementary arguments of the transform function
	...
	return args
```

### Outervar
In some scenarios it may be useful to define a module to depend completely on another module.
In this case we can inherit the scope of some variables from the callee, by setting their default to `miniflask.event.outervar`.
**Note:** This is miniflasks version of friend-classes known from OOP, as such it should also be used with caution and only for strong dependencies between modules that also are too loose for a well-defined interfaces.

**Example File:** `modules/module2/__init__.py`
```python
from miniflask.event import outervar

def main(state, event, varA=outervar):
    print("This variable is queried from the callee scope:", varA)

def register(mf):
    mf.register_event('main', main, unique=False)
```

**Example File:** `main.py`
```python
import miniflask

# initialize miniflask
mf = miniflask.init(module_dirs="./modules")
state, event = mf.state, mf.event
mf.parse_args()
varA=42
mf.event.main()
```



### Call Events
Events can be called using the `event` object, i.e. in another event or after initialization of miniflask using the global `mf.event` object (see above).

There are two types of calls:

**Mandatory Calls**  
You expect this event to exist and to be called using a self-specified interface.
E.g.:

```python
event.main()
result = event.notneeded("some argument")
```

*Note*: This code will raise an Exception, if one of the two events `main` or `notneeded` are not defined (or differ in their interface to the expectation of the call).

**Optional Calls**  
You want this event to be called if it is defined, but if it isn't you don't mind.
E.g.:

```python
event.optional.main()
result = event.optional.notneeded("some argument")
result = event.optional.notneeded("some argument", altfn=lambda s: s+" (no optional event used)")
```
\n

# Note {.alert}
- `event.optional.eventname()` treats the event like a `nonunique` event, thus it returns an list of results.
- `event.optional.eventname(..., altfn=...)` treats the event like a `unique` event, but in case no event was defined, it uses altfn to parse the arguments.
# .{.end}


### Performance Note
Leaving the `event` and `state` argument out from an event function definition removes an extra function wrapper around every function. Thus, without them the time consumption should not differ at all from a normal function call.
