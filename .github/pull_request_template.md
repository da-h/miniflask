# FEATURENAME
**Attention**: This is a breaking change.

This MR changes ...

## Description

**Setup**:
...

**Problem**:
...

**Previously**:
...

**New Behavior**:
...


## Things done in this MR
- ...
- ...
- ...

**Check all before creating this PR**:
- [ ] Documentation adapted
- [ ] unit tests adapted / created


## Example Usage

```python
def dosomething(val):
    print("event called with value: %i" % val)
    return val

def main(event):
    print("event returned value: %i" % event.dosomething(42))

def before_dosomething(event):
    print("before_-event called")
    event.hook["args"][0] *= 2

def after_dosomethingl(event):
    print("after_-event called")
    event.hook["result"] += 1

def register(mf):
    mf.register_event('dosomething', dosomething)
    mf.register_event('main', main)
    mf.register_event('before_dosomething', before_dosomething, unique=False)
    mf.register_event('after_dosomething', after_dosomething, unique=False)
```
