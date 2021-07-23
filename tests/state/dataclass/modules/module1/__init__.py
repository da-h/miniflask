from dataclasses import dataclass
import miniflask


@dataclass
class TestdataclassAll:
    state: miniflask.state
    event: miniflask.event
    somevar: int


@dataclass
class TestdataclassStateOnly:
    state: miniflask.state
    somevar: int


@dataclass
class TestdataclassEventOnly:
    event: miniflask.event
    somevar: int


def main(event):
    print(event.dataclassAll(42))
    print(event.dataclassStateOnly(42))
    print(event.dataclassEventOnly(42))


def register(mf):
    mf.register_event('main', main, unique=False)
    mf.register_event('dataclassAll', TestdataclassAll)
    mf.register_event('dataclassStateOnly', TestdataclassStateOnly)
    mf.register_event('dataclassEventOnly', TestdataclassEventOnly)
