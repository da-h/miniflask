#!/bin/python
import sys
import os
sys.path.insert(0, os.path.join("..", "..", "src"))

import miniflask  # noqa: E402
mf = miniflask.init(
    module_dirs="./modules",
)
event = mf.event
mf.load("modulenomfargs")

a = 0
for i in range(10000000):
    a += event.func(42)
