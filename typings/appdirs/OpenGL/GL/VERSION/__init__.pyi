"""
This type stub file was generated by pyright.
"""

import ctypes
from OpenGL import arrays, constants, wrapper
from OpenGL.raw.GL.ARB import imaging
from OpenGL.raw.GL.VERSION import GL_1_2 as _simple
from OpenGL.GL.ARB.imaging import *
from OpenGL.GL import images

"""Version 1.2 Image-handling functions

Almost all of the 1.2 enhancements are image-handling-related,
so this is, most of the 1.2 wrapper code...

Note that the functions that manually wrap certain operations are
guarded by if simple.functionName checks, so that you can use
if functionName to see if the function is available at run-time.
"""
glTexImage3D = ...
glTexSubImage3D = ...