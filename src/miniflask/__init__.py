from .miniflask import miniflask, print_info
from .event import outervar
from .modules import *
from .state import like

# meta
__version__       = "1.9.2"
__title__         = "miniflask"
__description__   = "Small research-oriented hook-based plugin engine."
__url__           = "https://github.com/da-h/miniflask"
__uri__           = __url__
__doc__           = __description__ + " <" + __uri__ + ">"
__documentation__ = 'https://da-h.github.io/miniflask'
__source__        = __url__
__tracker__       = __url__ + '/issues'
__author__        = "David Hartmann"
__license__       = "MIT License"
__copyright__     = "Copyright (c) 2020 " + __author__


def init(**kwargs):
    return miniflask(**kwargs)
