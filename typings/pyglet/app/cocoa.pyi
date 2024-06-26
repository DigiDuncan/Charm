"""
This type stub file was generated by pyright.
"""

from pyglet.app.base import EventLoop, PlatformEventLoop
from pyglet.libs.darwin import PyObjectEncoding

NSApplication = ...
NSMenu = ...
NSMenuItem = ...
NSDate = ...
NSEvent = ...
NSUserDefaults = ...
NSTimer = ...
def add_menu_item(menu, title, action, key): # -> None:
    ...

def create_menu(): # -> None:
    ...

class _AppDelegate_Implementation:
    _AppDelegate = ...
    @_AppDelegate.method(b'@' + PyObjectEncoding)
    def init(self, pyglet_loop): # -> ObjCInstance | None:
        ...
    
    @_AppDelegate.method('v')
    def updatePyglet_(self): # -> None:
        ...
    
    @_AppDelegate.method('v@')
    def applicationWillTerminate_(self, notification): # -> None:
        ...
    
    @_AppDelegate.method('v@')
    def applicationDidFinishLaunching_(self, notification): # -> None:
        ...
    


_AppDelegate = ...
class CocoaAlternateEventLoop(EventLoop):
    """This is an alternate loop developed mainly for ARM64 variants of macOS.
    nextEventMatchingMask_untilDate_inMode_dequeue_ is very broken with ctypes calls. Events eventually stop
    working properly after X returns. This event loop differs in that it uses the built-in NSApplication event
    loop. We tie our schedule into it via timer.
    """
    def __init__(self) -> None:
        ...
    
    def run(self, interval=...): # -> None:
        ...
    
    def exit(self): # -> None:
        """Safely exit the event loop at the end of the current iteration.

        This method is a thread-safe equivalent for setting
        :py:attr:`has_exit` to ``True``.  All waiting threads will be
        interrupted (see :py:meth:`sleep`).
        """
        ...
    


class CocoaPlatformEventLoop(PlatformEventLoop):
    def __init__(self) -> None:
        ...
    
    def start(self): # -> None:
        ...
    
    def nsapp_start(self, interval): # -> None:
        """Used only for CocoaAlternateEventLoop"""
        ...
    
    def nsapp_step(self): # -> None:
        """Used only for CocoaAlternateEventLoop"""
        ...
    
    def nsapp_stop(self): # -> None:
        """Used only for CocoaAlternateEventLoop"""
        ...
    
    def step(self, timeout=...): # -> bool:
        ...
    
    def stop(self): # -> None:
        ...
    
    def notify(self): # -> None:
        ...
    


