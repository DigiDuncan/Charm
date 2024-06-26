"""
This type stub file was generated by pyright.
"""

import sys
from typing import Literal

"""Holds type aliases used throughout the codebase."""
if sys.version_info >= (3, 12):
    ...
else:
    ...
HorizontalAlign = Literal["left", "center", "right"]
AnchorX = Literal["left", "center", "right"]
AnchorY = Literal["top", "bottom", "center", "baseline"]
ContentVAlign = Literal["left", "center", "top"]
__all__ = ["Buffer", "HorizontalAlign", "AnchorX", "AnchorY", "ContentVAlign"]
