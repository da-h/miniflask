from .miniflask import miniflask
from .event import outervar
from .modules import *

# meta
__version__ = "1.1"

def init(**kwargs):
    return miniflask(**kwargs)
