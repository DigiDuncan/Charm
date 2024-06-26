"""
This type stub file was generated by pyright.
"""

from ctypes import *
from pyglet.gl.gl import *
from pyglet.gl.wgl import *
from pyglet.gl.wglext_arb import *

"""Cached information about version and extensions of current WGL
implementation.
"""
class WGLInfoException(Exception):
    ...


class WGLInfo:
    def get_extensions(self): # -> list[Any] | list[str]:
        ...
    
    def have_extension(self, extension): # -> bool:
        ...
    


_wgl_info = ...
get_extensions = ...
have_extension = ...
