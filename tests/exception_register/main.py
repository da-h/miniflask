import sys
import os
sys.path.insert(0, os.path.join("..","..","src"))

import miniflask
mf = miniflask.init(
    module_dirs="./modules",
)

mf.load("module1")

mf.register_event("main", lambda: print("Main."))

mf.run()
