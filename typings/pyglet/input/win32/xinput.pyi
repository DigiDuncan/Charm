"""
This type stub file was generated by pyright.
"""

from pyglet.libs.win32 import com
from pyglet.event import EventDispatcher
from pyglet.libs.win32.types import *
from pyglet.input.base import Controller, ControllerManager, Device

XINPUT_GAMEPAD_LEFT_THUMB_DEADZONE = ...
XINPUT_GAMEPAD_RIGHT_THUMB_DEADZONE = ...
XINPUT_GAMEPAD_TRIGGER_THRESHOLD = ...
BATTERY_DEVTYPE_GAMEPAD = ...
BATTERY_DEVTYPE_HEADSET = ...
BATTERY_TYPE_DISCONNECTED = ...
BATTERY_TYPE_WIRED = ...
BATTERY_TYPE_ALKALINE = ...
BATTERY_TYPE_NIMH = ...
BATTERY_TYPE_UNKNOWN = ...
BATTERY_LEVEL_EMPTY = ...
BATTERY_LEVEL_LOW = ...
BATTERY_LEVEL_MEDIUM = ...
BATTERY_LEVEL_FULL = ...
XINPUT_GAMEPAD_DPAD_UP = ...
XINPUT_GAMEPAD_DPAD_DOWN = ...
XINPUT_GAMEPAD_DPAD_LEFT = ...
XINPUT_GAMEPAD_DPAD_RIGHT = ...
XINPUT_GAMEPAD_START = ...
XINPUT_GAMEPAD_BACK = ...
XINPUT_GAMEPAD_LEFT_THUMB = ...
XINPUT_GAMEPAD_RIGHT_THUMB = ...
XINPUT_GAMEPAD_LEFT_SHOULDER = ...
XINPUT_GAMEPAD_RIGHT_SHOULDER = ...
XINPUT_GAMEPAD_GUIDE = ...
XINPUT_GAMEPAD_A = ...
XINPUT_GAMEPAD_B = ...
XINPUT_GAMEPAD_X = ...
XINPUT_GAMEPAD_Y = ...
XINPUT_KEYSTROKE_KEYDOWN = ...
XINPUT_KEYSTROKE_KEYUP = ...
XINPUT_KEYSTROKE_REPEAT = ...
XINPUT_DEVTYPE_GAMEPAD = ...
XINPUT_DEVSUBTYPE_GAMEPAD = ...
XINPUT_DEVSUBTYPE_WHEEL = ...
XINPUT_DEVSUBTYPE_ARCADE_STICK = ...
XINPUT_DEVSUBTYPE_FLIGHT_SICK = ...
XINPUT_DEVSUBTYPE_DANCE_PAD = ...
XINPUT_DEVSUBTYPE_GUITAR = ...
XINPUT_DEVSUBTYPE_DRUM_KIT = ...
VK_PAD_A = ...
VK_PAD_B = ...
VK_PAD_X = ...
VK_PAD_Y = ...
VK_PAD_RSHOULDER = ...
VK_PAD_LSHOULDER = ...
VK_PAD_LTRIGGER = ...
VK_PAD_RTRIGGER = ...
VK_PAD_DPAD_UP = ...
VK_PAD_DPAD_DOWN = ...
VK_PAD_DPAD_LEFT = ...
VK_PAD_DPAD_RIGHT = ...
VK_PAD_START = ...
VK_PAD_BACK = ...
VK_PAD_LTHUMB_PRESS = ...
VK_PAD_RTHUMB_PRESS = ...
VK_PAD_LTHUMB_UP = ...
VK_PAD_LTHUMB_DOWN = ...
VK_PAD_LTHUMB_RIGHT = ...
VK_PAD_LTHUMB_LEFT = ...
VK_PAD_LTHUMB_UPLEFT = ...
VK_PAD_LTHUMB_UPRIGHT = ...
VK_PAD_LTHUMB_DOWNRIGHT = ...
VK_PAD_LTHUMB_DOWNLEFT = ...
VK_PAD_RTHUMB_UP = ...
VK_PAD_RTHUMB_DOWN = ...
VK_PAD_RTHUMB_RIGHT = ...
VK_PAD_RTHUMB_LEFT = ...
VK_PAD_RTHUMB_UPLEFT = ...
VK_PAD_RTHUMB_UPRIGHT = ...
VK_PAD_RTHUMB_DOWNRIGHT = ...
VK_PAD_RTHUMB_DOWNLEFT = ...
XUSER_MAX_COUNT = ...
XUSER_INDEX_ANY = ...
ERROR_DEVICE_NOT_CONNECTED = ...
ERROR_EMPTY = ...
ERROR_SUCCESS = ...
class XINPUT_GAMEPAD(Structure):
    _fields_ = ...


class XINPUT_STATE(Structure):
    _fields_ = ...


class XINPUT_VIBRATION(Structure):
    _fields_ = ...


class XINPUT_CAPABILITIES(Structure):
    _fields_ = ...


class XINPUT_BATTERY_INFORMATION(Structure):
    _fields_ = ...


class XINPUT_CAPABILITIES_EX(Structure):
    _fields_ = ...


if library_name == "xinput1_4":
    XInputGetBatteryInformation = ...
    XInputGetState = ...
    XInputGetCapabilities = ...
else:
    XInputGetBatteryInformation = ...
    XInputGetState = ...
    XInputGetCapabilities = ...
XInputSetState = ...
BSTR = LPCWSTR
IWbemContext = c_void_p
RPC_C_AUTHN_WINNT = ...
RPC_C_AUTHZ_NONE = ...
RPC_C_AUTHN_LEVEL_CALL = ...
RPC_C_IMP_LEVEL_IMPERSONATE = ...
EOAC_NONE = ...
VT_BSTR = ...
CLSID_WbemLocator = ...
IID_IWbemLocator = ...
class IWbemClassObject(com.pIUnknown):
    _methods_ = ...


class IEnumWbemClassObject(com.pIUnknown):
    _methods_ = ...


class IWbemServices(com.pIUnknown):
    _methods_ = ...


class IWbemLocator(com.pIUnknown):
    _methods_ = ...


def get_xinput_guids(): # -> list[Any]:
    """We iterate over all devices in the system looking for IG_ in the device ID, which indicates it's an
    XInput device. Returns a list of strings containing pid/vid.
    Monstrosity found at: https://docs.microsoft.com/en-us/windows/win32/xinput/xinput-and-directinput
    """
    ...

controller_api_to_pyglet = ...
class XInputDevice(Device):
    def __init__(self, index, manager) -> None:
        ...
    
    def set_rumble_state(self): # -> None:
        ...
    
    def get_controls(self): # -> list[Button | AbsoluteAxis]:
        ...
    
    def get_guid(self): # -> Literal['XINPUTCONTROLLER']:
        ...
    


class XInputDeviceManager(EventDispatcher):
    def __init__(self) -> None:
        ...
    
    def get_devices(self): # -> list[XInputDevice]:
        ...
    
    def on_connect(self, device): # -> None:
        """A device was connected."""
        ...
    
    def on_disconnect(self, device): # -> None:
        """A device was disconnected"""
        ...
    


_device_manager = ...
class XInputController(Controller):
    def rumble_play_weak(self, strength=..., duration=...): # -> None:
        ...
    
    def rumble_play_strong(self, strength=..., duration=...): # -> None:
        ...
    
    def rumble_stop_weak(self): # -> None:
        ...
    
    def rumble_stop_strong(self): # -> None:
        ...
    


class XInputControllerManager(ControllerManager):
    def __init__(self) -> None:
        ...
    
    def get_controllers(self): # -> list[Any]:
        ...
    


def get_devices(): # -> list[XInputDevice]:
    ...

def get_controllers(): # -> list[XInputController]:
    ...
