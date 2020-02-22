#!/bin/python
import sys
import os
sys.path.insert(0, os.path.join("..","..","src"))

import miniflask
mf = miniflask.init(
    modules_dir="./modules",
)
mf.load("module1")
from modules.module1 import func as func2

class event():

    @classmethod
    def func(cls, x):
        return x

a = 0
for i in range(10000000):
    a += event.func(42)
