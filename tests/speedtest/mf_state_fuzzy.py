#!/bin/python
import sys
import os
sys.path.insert(0, os.path.join("..","..","src"))

import miniflask
mf = miniflask.init(
    module_dirs="./modules",
)
mf.load("moduleunique")
event = mf.event

a = 0
for i in range(10000000):
    a += event.get_state_var(".moduleunique.a")
