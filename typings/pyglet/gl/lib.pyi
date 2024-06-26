"""
This type stub file was generated by pyright.
"""

import ctypes
import pyglet
from pyglet.gl.lib_wgl import link_WGL
from pyglet.gl.lib_agl import link_AGL
from pyglet.gl.lib_glx import link_GLX

__all__ = ['link_GL', 'link_AGL', 'link_GLX', 'link_WGL', 'GLException', 'missing_function', 'decorate_function']
_debug_gl = pyglet.options['debug_gl']
_debug_gl_trace = pyglet.options['debug_gl_trace']
_debug_gl_trace_args = pyglet.options['debug_gl_trace_args']
class MissingFunctionException(Exception):
    def __init__(self, name, requires=..., suggestions=...) -> None:
        ...
    


def missing_function(name, requires=..., suggestions=...): # -> Callable[..., NoReturn]:
    ...

_int_types = ...
if hasattr(ctypes, 'c_int64'):
    ...
class c_void(ctypes.Structure):
    _fields_ = ...


class GLException(Exception):
    ...


def errcheck(result, func, arguments):
    ...

def decorate_function(func, name): # -> None:
    ...

link_AGL = ...
link_GLX = ...
link_WGL = ...
if pyglet.compat_platform in ('win32', 'cygwin'):
    ...
else:
    ...
