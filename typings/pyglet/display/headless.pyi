"""
This type stub file was generated by pyright.
"""

from .base import Canvas, Display, Screen
from ctypes import *

class HeadlessDisplay(Display):
    def __init__(self) -> None:
        ...
    
    def get_screens(self): # -> list[HeadlessScreen]:
        ...
    
    def __del__(self): # -> None:
        ...
    


class HeadlessCanvas(Canvas):
    def __init__(self, display, egl_surface) -> None:
        ...
    


class HeadlessScreen(Screen):
    def __init__(self, display, x, y, width, height) -> None:
        ...
    
    def get_matching_configs(self, template):
        ...
    
    def get_modes(self): # -> None:
        ...
    
    def get_mode(self): # -> None:
        ...
    
    def set_mode(self, mode): # -> None:
        ...
    
    def restore_mode(self): # -> None:
        ...
    

