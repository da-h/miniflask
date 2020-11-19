import sys
import os
sys.path.insert(0, os.path.join("..", "..", "src"))

import miniflask  # noqa: E402
mf = miniflask.init(
    module_dirs="./modules",
)

mf.run()
