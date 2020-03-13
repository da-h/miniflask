from .miniflask import miniflask, print_info
from .event import outervar
from .modules import *
from .state import like

# meta
__version__ = "1.5.1"

def init(**kwargs):
    return miniflask(**kwargs)
