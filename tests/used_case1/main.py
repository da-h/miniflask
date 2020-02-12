import sys
import os
sys.path.insert(0, os.path.join("..","..","src"))

import miniflask
mf = miniflask.init(
    modules_dir="./modules",
)
mf.parse_args()
if not mf.halt_parse:
    if hasattr(mf.event, 'main'):
        mf.event.main()
    else:
        print("There is nothing to do.")


# calling events
# event.main_loop()

# getting/setting variables
# state["model.resnet.num_filters"]

# event
# -> calling events / event groups

# miniflask object
# -> parse args
# -> load modules
# -> register new events
