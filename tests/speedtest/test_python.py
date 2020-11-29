#!/bin/python

def func():
    return 42


a = 0
for i in range(10000000):
    a += func()
