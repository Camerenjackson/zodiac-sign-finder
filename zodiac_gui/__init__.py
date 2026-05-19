"""Zodiac Sign Finder — desktop Western zodiac lookup."""

from zodiac_gui.theme import APP_NAME, APP_VERSION
from zodiac_gui.zodiac_logic import ZodiacError, ZodiacResult, lookup

__version__ = APP_VERSION
__app_name__ = APP_NAME

__all__ = ["ZodiacError", "ZodiacResult", "lookup", "__version__", "__app_name__"]
