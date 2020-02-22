#!/bin/python
import sys
import os
sys.path.insert(0, os.path.join("..","..","src"))

import miniflask
mf = miniflask.init(
    modules_dir="./modules",
)
event = mf.event
mf.load("modulenonunique")

a = 0
for i in range(10000000):
    a += event.func(42)[0]
