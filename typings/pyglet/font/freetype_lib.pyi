"""
This type stub file was generated by pyright.
"""

from ctypes import *
from .base import FontException

_libfreetype = ...
_font_data = ...
FT_Byte = c_char
FT_Bytes = ...
FT_Char = c_byte
FT_Int = c_int
FT_UInt = c_uint
FT_Int16 = c_int16
FT_UInt16 = c_uint16
FT_Int32 = c_int32
FT_UInt32 = c_uint32
FT_Int64 = c_int64
FT_UInt64 = c_uint64
FT_Short = c_short
FT_UShort = c_ushort
FT_Long = c_long
FT_ULong = c_ulong
FT_Bool = c_char
FT_Offset = c_size_t
FT_String = c_char
FT_String_Ptr = c_char_p
FT_Tag = FT_UInt32
FT_Error = c_int
FT_Fixed = c_long
FT_Pointer = c_void_p
FT_Pos = c_long
class FT_Vector(Structure):
    _fields_ = ...


class FT_BBox(Structure):
    _fields_ = ...


class FT_Matrix(Structure):
    _fields_ = ...


FT_FWord = c_short
FT_UFWord = c_ushort
FT_F2Dot14 = c_short
class FT_UnitVector(Structure):
    _fields_ = ...


FT_F26Dot6 = c_long
class FT_Data(Structure):
    _fields_ = ...


FT_Generic_Finalizer = ...
class FT_Generic(Structure):
    _fields_ = ...


class FT_Bitmap(Structure):
    _fields_ = ...


FT_PIXEL_MODE_NONE = ...
FT_PIXEL_MODE_MONO = ...
FT_PIXEL_MODE_GRAY = ...
FT_PIXEL_MODE_GRAY2 = ...
FT_PIXEL_MODE_GRAY4 = ...
FT_PIXEL_MODE_LCD = ...
FT_PIXEL_MODE_LCD_V = ...
FT_PIXEL_MODE_BGRA = ...
class FT_LibraryRec(Structure):
    _fields_ = ...
    def __del__(self): # -> None:
        ...
    


FT_Library = ...
class FT_Bitmap_Size(Structure):
    _fields_ = ...


class FT_Glyph_Metrics(Structure):
    _fields_ = ...
    def dump(self): # -> None:
        ...
    


FT_Glyph_Format = c_ulong
def FT_IMAGE_TAG(tag): # -> int:
    ...

FT_GLYPH_FORMAT_NONE = ...
FT_GLYPH_FORMAT_COMPOSITE = ...
FT_GLYPH_FORMAT_BITMAP = ...
FT_GLYPH_FORMAT_OUTLINE = ...
FT_GLYPH_FORMAT_PLOTTER = ...
class FT_Outline(Structure):
    _fields_ = ...


FT_SubGlyph = c_void_p
class FT_GlyphSlotRec(Structure):
    _fields_ = ...


FT_GlyphSlot = ...
class FT_Size_Metrics(Structure):
    _fields_ = ...


class FT_SizeRec(Structure):
    _fields_ = ...


FT_Size = ...
class FT_FaceRec(Structure):
    _fields_ = ...
    def dump(self): # -> None:
        ...
    
    def has_kerning(self): # -> Any:
        ...
    


FT_Face = ...
FT_FACE_FLAG_SCALABLE = ...
FT_FACE_FLAG_FIXED_SIZES = ...
FT_FACE_FLAG_FIXED_WIDTH = ...
FT_FACE_FLAG_SFNT = ...
FT_FACE_FLAG_HORIZONTAL = ...
FT_FACE_FLAG_VERTICAL = ...
FT_FACE_FLAG_KERNING = ...
FT_FACE_FLAG_FAST_GLYPHS = ...
FT_FACE_FLAG_MULTIPLE_MASTERS = ...
FT_FACE_FLAG_GLYPH_NAMES = ...
FT_FACE_FLAG_EXTERNAL_STREAM = ...
FT_FACE_FLAG_HINTER = ...
FT_STYLE_FLAG_ITALIC = ...
FT_STYLE_FLAG_BOLD = ...
def FT_LOAD_TARGET_(x):
    ...

FT_LOAD_TARGET_NORMAL = ...
FT_LOAD_TARGET_LIGHT = ...
FT_LOAD_TARGET_MONO = ...
FT_LOAD_TARGET_LCD = ...
FT_LOAD_TARGET_LCD_V = ...
def f16p16_to_float(value): # -> float:
    ...

def float_to_f16p16(value): # -> int:
    ...

def f26p6_to_float(value): # -> float:
    ...

def float_to_f26p6(value): # -> int:
    ...

class FreeTypeError(FontException):
    def __init__(self, message, errcode) -> None:
        ...
    
    def __str__(self) -> str:
        ...
    
    @classmethod
    def check_and_raise_on_error(cls, errcode): # -> None:
        ...
    
    _ft_errors = ...


FT_LOAD_RENDER = ...
FT_Init_FreeType = ...
FT_Done_FreeType = ...
FT_New_Face = ...
FT_Done_Face = ...
FT_Reference_Face = ...
FT_New_Memory_Face = ...
FT_Set_Char_Size = ...
FT_Set_Pixel_Sizes = ...
FT_Load_Glyph = ...
FT_Get_Char_Index = ...
FT_Load_Char = ...
FT_Get_Kerning = ...
class FT_SfntName(Structure):
    _fields_ = ...


FT_Get_Sfnt_Name_Count = ...
FT_Get_Sfnt_Name = ...
TT_PLATFORM_MICROSOFT = ...
TT_MS_ID_UNICODE_CS = ...
TT_NAME_ID_COPYRIGHT = ...
TT_NAME_ID_FONT_FAMILY = ...
TT_NAME_ID_FONT_SUBFAMILY = ...
TT_NAME_ID_UNIQUE_ID = ...
TT_NAME_ID_FULL_NAME = ...
TT_NAME_ID_VERSION_STRING = ...
TT_NAME_ID_PS_NAME = ...
TT_NAME_ID_TRADEMARK = ...
TT_NAME_ID_MANUFACTURER = ...
TT_NAME_ID_DESIGNER = ...
TT_NAME_ID_DESCRIPTION = ...
TT_NAME_ID_VENDOR_URL = ...
TT_NAME_ID_DESIGNER_URL = ...
TT_NAME_ID_LICENSE = ...
TT_NAME_ID_LICENSE_URL = ...
TT_NAME_ID_PREFERRED_FAMILY = ...
TT_NAME_ID_PREFERRED_SUBFAMILY = ...
TT_NAME_ID_MAC_FULL_NAME = ...
TT_NAME_ID_CID_FINDFONT_NAME = ...
_library = ...
def ft_get_library(): # -> _Pointer[FT_LibraryRec]:
    ...
