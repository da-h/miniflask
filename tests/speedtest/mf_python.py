#!/bin/python
import sys
import os
sys.path.insert(0, os.path.join("..", "..", "src"))

import miniflask  # noqa: E402
mf = miniflask.init(
    module_dirs="./modules",
)
mf.load("module1")
from modules.module1 import func as func2  # noqa: F401,E402


def func(x):
    return x


a = 0
for i in range(10000000):
    a += func(42)
