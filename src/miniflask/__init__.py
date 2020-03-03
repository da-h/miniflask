from .miniflask import miniflask, print_info
from .event import outervar
from .modules import *

# meta
__version__ = "1.4"

def init(**kwargs):
    return miniflask(**kwargs)
