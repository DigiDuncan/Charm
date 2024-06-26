"""
This type stub file was generated by pyright.
"""

from ctypes import *
from pyglet.gl import *
from pyglet.image import *
from pyglet.image.codecs import *

gdk = ...
gdkpixbuf = ...
GdkPixbufLoader = c_void_p
GdkPixbuf = c_void_p
guchar = c_char
class GTimeVal(Structure):
    _fields_ = ...


GQuark = c_uint32
gint = c_int
gchar = c_char
class GError(Structure):
    _fields_ = ...


gerror_ptr = ...
class GdkPixBufLoader:
    """
    Wrapper around GdkPixBufLoader object.
    """
    def __init__(self, filename, file) -> None:
        ...
    
    def __del__(self): # -> None:
        ...
    
    def write(self, data): # -> None:
        ...
    
    def get_pixbuf(self): # -> GdkPixBuf:
        ...
    
    def get_animation(self): # -> GdkPixBufAnimation:
        ...
    


class GdkPixBuf:
    """
    Wrapper around GdkPixBuf object.
    """
    def __init__(self, loader, pixbuf) -> None:
        ...
    
    def __del__(self): # -> None:
        ...
    
    def load_next(self): # -> bool:
        ...
    
    @property
    def width(self):
        ...
    
    @property
    def height(self):
        ...
    
    @property
    def channels(self):
        ...
    
    @property
    def rowstride(self):
        ...
    
    @property
    def has_alpha(self):
        ...
    
    def get_pixels(self):
        ...
    
    def to_image(self): # -> ImageData | None:
        ...
    


class GdkPixBufAnimation:
    """
    Wrapper for a GdkPixBufIter for an animation.
    """
    def __init__(self, loader, anim, gif_delays) -> None:
        ...
    
    def __del__(self): # -> None:
        ...
    
    def __iter__(self): # -> GdkPixBufAnimationIterator:
        ...
    
    def to_animation(self): # -> Animation:
        ...
    


class GdkPixBufAnimationIterator:
    def __init__(self, loader, anim_iter, start_time, gif_delays) -> None:
        ...
    
    def __del__(self): # -> None:
        ...
    
    def __iter__(self): # -> Self:
        ...
    
    def __next__(self): # -> AnimationFrame:
        ...
    
    def get_frame(self): # -> AnimationFrame | None:
        ...
    
    @property
    def gdk_delay_time(self):
        ...
    


class GdkPixbuf2ImageDecoder(ImageDecoder):
    def get_file_extensions(self): # -> list[str]:
        ...
    
    def get_animation_file_extensions(self): # -> list[str]:
        ...
    
    def decode(self, filename, file): # -> ImageData | None:
        ...
    
    def decode_animation(self, filename, file): # -> Animation:
        ...
    


def get_decoders(): # -> list[GdkPixbuf2ImageDecoder]:
    ...

def get_encoders(): # -> list[Any]:
    ...

def init(): # -> None:
    ...

