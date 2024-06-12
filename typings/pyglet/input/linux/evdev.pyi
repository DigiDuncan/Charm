"""
This type stub file was generated by pyright.
"""

import ctypes
from typing import List
from .evdev_constants import *
from pyglet.app.xlib import XlibSelectDevice
from pyglet.input.base import Controller, ControllerManager, Device

_IOC_NRBITS = ...
_IOC_TYPEBITS = ...
_IOC_SIZEBITS = ...
_IOC_DIRBITS = ...
_IOC_NRSHIFT = ...
_IOC_TYPESHIFT = ...
_IOC_SIZESHIFT = ...
_IOC_DIRSHIFT = ...
_IOC_NONE = ...
_IOC_WRITE = ...
_IOC_READ = ...
class Timeval(ctypes.Structure):
    _fields_ = ...


class InputEvent(ctypes.Structure):
    _fields_ = ...


class InputID(ctypes.Structure):
    _fields_ = ...


class InputABSInfo(ctypes.Structure):
    _fields_ = ...


class FFReplay(ctypes.Structure):
    _fields_ = ...


class FFTrigger(ctypes.Structure):
    _fields_ = ...


class FFEnvelope(ctypes.Structure):
    _fields_ = ...


class FFConstantEffect(ctypes.Structure):
    _fields_ = ...


class FFRampEffect(ctypes.Structure):
    _fields_ = ...


class FFConditionEffect(ctypes.Structure):
    _fields_ = ...


class FFPeriodicEffect(ctypes.Structure):
    _fields_ = ...


class FFRumbleEffect(ctypes.Structure):
    _fields_ = ...


class FFEffectType(ctypes.Union):
    _fields_ = ...


class FFEvent(ctypes.Structure):
    _fields_ = ...


EVIOCGVERSION = ...
EVIOCGID = ...
EVIOCGNAME = ...
EVIOCGPHYS = ...
EVIOCGUNIQ = ...
EVIOCSFF = ...
def EVIOCGBIT(fileno, ev, buffer):
    ...

def EVIOCGABS(fileno, abs): # -> InputABSInfo:
    ...

def get_set_bits(bytestring): # -> set[Any]:
    ...

_abs_names = ...
_rel_names = ...
event_types = ...
class EvdevDevice(XlibSelectDevice, Device):
    _fileno = ...
    def __init__(self, display, filename) -> None:
        ...
    
    def get_guid(self): # -> str:
        """Get the device's SDL2 style GUID string"""
        ...
    
    def open(self, window=..., exclusive=...): # -> None:
        ...
    
    def close(self): # -> None:
        ...
    
    def get_controls(self): # -> list[Any]:
        ...
    
    def ff_upload_effect(self, structure): # -> None:
        ...
    
    def fileno(self): # -> int | None:
        ...
    
    def poll(self): # -> Literal[False]:
        ...
    
    def select(self): # -> None:
        ...
    


class FFController(Controller):
    """Controller that supports force-feedback"""
    _fileno = ...
    _weak_effect = ...
    _play_weak_event = ...
    _stop_weak_event = ...
    _strong_effect = ...
    _play_strong_event = ...
    _stop_strong_event = ...
    def open(self, window=..., exclusive=...): # -> None:
        ...
    
    def rumble_play_weak(self, strength=..., duration=...): # -> None:
        ...
    
    def rumble_play_strong(self, strength=..., duration=...): # -> None:
        ...
    
    def rumble_stop_weak(self): # -> None:
        ...
    
    def rumble_stop_strong(self): # -> None:
        ...
    


class EvdevControllerManager(ControllerManager, XlibSelectDevice):
    def __init__(self, display=...) -> None:
        ...
    
    def __del__(self): # -> None:
        ...
    
    def fileno(self): # -> int:
        """Allow this class to be Selectable"""
        ...
    
    def select(self): # -> None:
        """Triggered whenever the devices_file changes."""
        ...
    
    def get_controllers(self) -> List[Controller]:
        ...
    


def get_devices(display=...): # -> list[Any]:
    ...

def get_joysticks(display=...): # -> list[Joystick]:
    ...

def get_controllers(display=...): # -> list[FFController | Controller]:
    ...
