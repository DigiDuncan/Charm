"""
This type stub file was generated by pyright.
"""

import platform
import pyglet
from ctypes import *
from typing import List, Optional, Tuple
from pyglet.font import base
from pyglet.libs.win32.constants import *
from pyglet.libs.win32.types import *

dwrite = ...
if platform.architecture()[0] == '32bit':
    ...
dwrite_lib = ...
_debug_font = pyglet.options['debug_font']
_debug_print = ...
def DWRITE_MAKE_OPENTYPE_TAG(a, b, c, d): # -> int:
    ...

DWRITE_FACTORY_TYPE = UINT
DWRITE_FACTORY_TYPE_SHARED = ...
DWRITE_FACTORY_TYPE_ISOLATED = ...
DWRITE_FONT_WEIGHT = UINT
DWRITE_FONT_WEIGHT_THIN = ...
DWRITE_FONT_WEIGHT_EXTRA_LIGHT = ...
DWRITE_FONT_WEIGHT_ULTRA_LIGHT = ...
DWRITE_FONT_WEIGHT_LIGHT = ...
DWRITE_FONT_WEIGHT_SEMI_LIGHT = ...
DWRITE_FONT_WEIGHT_NORMAL = ...
DWRITE_FONT_WEIGHT_REGULAR = ...
DWRITE_FONT_WEIGHT_MEDIUM = ...
DWRITE_FONT_WEIGHT_DEMI_BOLD = ...
DWRITE_FONT_WEIGHT_SEMI_BOLD = ...
DWRITE_FONT_WEIGHT_BOLD = ...
DWRITE_FONT_WEIGHT_EXTRA_BOLD = ...
DWRITE_FONT_WEIGHT_ULTRA_BOLD = ...
DWRITE_FONT_WEIGHT_BLACK = ...
DWRITE_FONT_WEIGHT_HEAVY = ...
DWRITE_FONT_WEIGHT_EXTRA_BLACK = ...
name_to_weight = ...
DWRITE_FONT_STRETCH = UINT
DWRITE_FONT_STRETCH_UNDEFINED = ...
DWRITE_FONT_STRETCH_ULTRA_CONDENSED = ...
DWRITE_FONT_STRETCH_EXTRA_CONDENSED = ...
DWRITE_FONT_STRETCH_CONDENSED = ...
DWRITE_FONT_STRETCH_SEMI_CONDENSED = ...
DWRITE_FONT_STRETCH_NORMAL = ...
DWRITE_FONT_STRETCH_MEDIUM = ...
DWRITE_FONT_STRETCH_SEMI_EXPANDED = ...
DWRITE_FONT_STRETCH_EXPANDED = ...
DWRITE_FONT_STRETCH_EXTRA_EXPANDED = ...
name_to_stretch = ...
DWRITE_GLYPH_IMAGE_FORMATS = c_int
DWRITE_GLYPH_IMAGE_FORMATS_NONE = ...
DWRITE_GLYPH_IMAGE_FORMATS_TRUETYPE = ...
DWRITE_GLYPH_IMAGE_FORMATS_CFF = ...
DWRITE_GLYPH_IMAGE_FORMATS_COLR = ...
DWRITE_GLYPH_IMAGE_FORMATS_SVG = ...
DWRITE_GLYPH_IMAGE_FORMATS_PNG = ...
DWRITE_GLYPH_IMAGE_FORMATS_JPEG = ...
DWRITE_GLYPH_IMAGE_FORMATS_TIFF = ...
DWRITE_GLYPH_IMAGE_FORMATS_PREMULTIPLIED_B8G8R8A8 = ...
DWRITE_MEASURING_MODE = UINT
DWRITE_MEASURING_MODE_NATURAL = ...
DWRITE_MEASURING_MODE_GDI_CLASSIC = ...
DWRITE_MEASURING_MODE_GDI_NATURAL = ...
DWRITE_GLYPH_IMAGE_FORMATS_ALL = ...
DWRITE_FONT_STYLE = UINT
DWRITE_FONT_STYLE_NORMAL = ...
DWRITE_FONT_STYLE_OBLIQUE = ...
DWRITE_FONT_STYLE_ITALIC = ...
name_to_style = ...
UINT8 = c_uint8
UINT16 = c_uint16
INT16 = c_int16
INT32 = c_int32
UINT32 = c_uint32
UINT64 = c_uint64
DWRITE_INFORMATIONAL_STRING_ID = UINT32
DWRITE_INFORMATIONAL_STRING_NONE = ...
DWRITE_INFORMATIONAL_STRING_COPYRIGHT_NOTICE = ...
DWRITE_INFORMATIONAL_STRING_VERSION_STRINGS = ...
DWRITE_INFORMATIONAL_STRING_TRADEMARK = ...
DWRITE_INFORMATIONAL_STRING_MANUFACTURER = ...
DWRITE_INFORMATIONAL_STRING_DESIGNER = ...
DWRITE_INFORMATIONAL_STRING_DESIGNER_URL = ...
DWRITE_INFORMATIONAL_STRING_DESCRIPTION = ...
DWRITE_INFORMATIONAL_STRING_FONT_VENDOR_URL = ...
DWRITE_INFORMATIONAL_STRING_LICENSE_DESCRIPTION = ...
DWRITE_INFORMATIONAL_STRING_LICENSE_INFO_URL = ...
DWRITE_INFORMATIONAL_STRING_WIN32_FAMILY_NAMES = ...
DWRITE_INFORMATIONAL_STRING_WIN32_SUBFAMILY_NAMES = ...
DWRITE_INFORMATIONAL_STRING_TYPOGRAPHIC_FAMILY_NAMES = ...
DWRITE_INFORMATIONAL_STRING_TYPOGRAPHIC_SUBFAMILY_NAMES = ...
DWRITE_INFORMATIONAL_STRING_SAMPLE_TEXT = ...
DWRITE_INFORMATIONAL_STRING_FULL_NAME = ...
DWRITE_INFORMATIONAL_STRING_POSTSCRIPT_NAME = ...
DWRITE_INFORMATIONAL_STRING_POSTSCRIPT_CID_NAME = ...
DWRITE_INFORMATIONAL_STRING_WEIGHT_STRETCH_STYLE_FAMILY_NAME = ...
DWRITE_INFORMATIONAL_STRING_DESIGN_SCRIPT_LANGUAGE_TAG = ...
DWRITE_INFORMATIONAL_STRING_SUPPORTED_SCRIPT_LANGUAGE_TAG = ...
DWRITE_INFORMATIONAL_STRING_PREFERRED_FAMILY_NAMES = ...
DWRITE_INFORMATIONAL_STRING_PREFERRED_SUBFAMILY_NAMES = ...
DWRITE_INFORMATIONAL_STRING_WWS_FAMILY_NAME = ...
class D2D_POINT_2F(Structure):
    _fields_ = ...


class D2D1_RECT_F(Structure):
    _fields_ = ...


class D2D1_COLOR_F(Structure):
    _fields_ = ...


class DWRITE_TEXT_METRICS(ctypes.Structure):
    _fields_ = ...


class DWRITE_FONT_METRICS(ctypes.Structure):
    _fields_ = ...


class DWRITE_GLYPH_METRICS(ctypes.Structure):
    _fields_ = ...


class DWRITE_GLYPH_OFFSET(ctypes.Structure):
    _fields_ = ...
    def __repr__(self): # -> str:
        ...
    


class DWRITE_CLUSTER_METRICS(ctypes.Structure):
    _fields_ = ...


class IDWriteFontFileStream(com.IUnknown):
    _methods_ = ...


class IDWriteFontFileLoader_LI(com.IUnknown):
    _methods_ = ...


class IDWriteFontFileLoader(com.pIUnknown):
    _methods_ = ...


class IDWriteLocalFontFileLoader(IDWriteFontFileLoader, com.pIUnknown):
    _methods_ = ...


IID_IDWriteLocalFontFileLoader = ...
class IDWriteFontFile(com.pIUnknown):
    _methods_ = ...


class IDWriteFontFace(com.pIUnknown):
    _methods_ = ...


IID_IDWriteFontFace1 = ...
class IDWriteFontFace1(IDWriteFontFace, com.pIUnknown):
    _methods_ = ...


class DWRITE_GLYPH_RUN(ctypes.Structure):
    _fields_ = ...


DWRITE_SCRIPT_SHAPES = UINT
DWRITE_SCRIPT_SHAPES_DEFAULT = ...
class DWRITE_SCRIPT_ANALYSIS(ctypes.Structure):
    _fields_ = ...


DWRITE_FONT_FEATURE_TAG = UINT
class DWRITE_FONT_FEATURE(ctypes.Structure):
    _fields_ = ...


class DWRITE_TYPOGRAPHIC_FEATURES(ctypes.Structure):
    _fields_ = ...


class DWRITE_SHAPING_TEXT_PROPERTIES(ctypes.Structure):
    _fields_ = ...
    def __repr__(self): # -> str:
        ...
    


class DWRITE_SHAPING_GLYPH_PROPERTIES(ctypes.Structure):
    _fields_ = ...


DWRITE_READING_DIRECTION = UINT
DWRITE_READING_DIRECTION_LEFT_TO_RIGHT = ...
class IDWriteTextAnalysisSource(com.IUnknown):
    _methods_ = ...


class IDWriteTextAnalysisSink(com.IUnknown):
    _methods_ = ...


class Run:
    def __init__(self) -> None:
        ...
    
    def ContainsTextPosition(self, textPosition):
        ...
    


class TextAnalysis(com.COMObject):
    _interfaces_ = ...
    def __init__(self) -> None:
        ...
    
    def GenerateResults(self, analyzer, text, text_length): # -> None:
        ...
    
    def SetScriptAnalysis(self, textPosition, textLength, scriptAnalysis): # -> Literal[0]:
        ...
    
    def GetTextBeforePosition(self, textPosition, textString, textLength):
        ...
    
    def GetTextAtPosition(self, textPosition, textString, textLength): # -> Literal[0]:
        ...
    
    def GetParagraphReadingDirection(self): # -> Literal[0]:
        ...
    
    def GetLocaleName(self, textPosition, textLength, localeName): # -> Literal[0]:
        ...
    
    def GetNumberSubstitution(self): # -> Literal[0]:
        ...
    
    def SetCurrentRun(self, textPosition): # -> None:
        ...
    
    def SplitCurrentRun(self, textPosition): # -> None:
        ...
    
    def FetchNextRun(self, textLength): # -> tuple[Run | None, Any]:
        ...
    


class IDWriteTextAnalyzer(com.pIUnknown):
    _methods_ = ...


class IDWriteLocalizedStrings(com.pIUnknown):
    _methods_ = ...


class IDWriteFontList(com.pIUnknown):
    _methods_ = ...


class IDWriteFontFamily(IDWriteFontList, com.pIUnknown):
    _methods_ = ...


class IDWriteFontFamily1(IDWriteFontFamily, IDWriteFontList, com.pIUnknown):
    _methods_ = ...


class IDWriteFont(com.pIUnknown):
    _methods_ = ...


class IDWriteFont1(IDWriteFont, com.pIUnknown):
    _methods_ = ...


class IDWriteFontCollection(com.pIUnknown):
    _methods_ = ...


class IDWriteFontCollection1(IDWriteFontCollection, com.pIUnknown):
    _methods_ = ...


DWRITE_TEXT_ALIGNMENT = UINT
DWRITE_TEXT_ALIGNMENT_LEADING = ...
DWRITE_TEXT_ALIGNMENT_TRAILING = ...
DWRITE_TEXT_ALIGNMENT_CENTER = ...
DWRITE_TEXT_ALIGNMENT_JUSTIFIED = ...
class IDWriteGdiInterop(com.pIUnknown):
    _methods_ = ...


class IDWriteTextFormat(com.pIUnknown):
    _methods_ = ...


class IDWriteTypography(com.pIUnknown):
    _methods_ = ...


class DWRITE_TEXT_RANGE(ctypes.Structure):
    _fields_ = ...


class DWRITE_OVERHANG_METRICS(ctypes.Structure):
    _fields_ = ...


class IDWriteTextLayout(IDWriteTextFormat, com.pIUnknown):
    _methods_ = ...


class IDWriteTextLayout1(IDWriteTextLayout, IDWriteTextFormat, com.pIUnknown):
    _methods_ = ...


class IDWriteFontFileEnumerator(com.IUnknown):
    _methods_ = ...


class IDWriteFontCollectionLoader(com.IUnknown):
    _methods_ = ...


class MyFontFileStream(com.COMObject):
    _interfaces_ = ...
    def __init__(self, data) -> None:
        ...
    
    def ReadFileFragment(self, fragmentStart, fileOffset, fragmentSize, fragmentContext): # -> Literal[2147500037, 0]:
        ...
    
    def ReleaseFileFragment(self, fragmentContext): # -> Literal[0]:
        ...
    
    def GetFileSize(self, fileSize): # -> Literal[0]:
        ...
    
    def GetLastWriteTime(self, lastWriteTime): # -> Literal[2147500033]:
        ...
    


class LegacyFontFileLoader(com.COMObject):
    _interfaces_ = ...
    def __init__(self) -> None:
        ...
    
    def CreateStreamFromKey(self, fontfileReferenceKey, fontFileReferenceKeySize, fontFileStream): # -> Literal[0]:
        ...
    
    def SetCurrentFont(self, index, data): # -> None:
        ...
    


class MyEnumerator(com.COMObject):
    _interfaces_ = ...
    def __init__(self, factory, loader) -> None:
        ...
    
    def AddFontData(self, fonts): # -> None:
        ...
    
    def MoveNext(self, hasCurrentFile): # -> None:
        ...
    
    def GetCurrentFontFile(self, fontFile): # -> Literal[0]:
        ...
    


class LegacyCollectionLoader(com.COMObject):
    _interfaces_ = ...
    def __init__(self, factory, loader) -> None:
        ...
    
    def AddFontData(self, fonts): # -> None:
        ...
    
    def CreateEnumeratorFromKey(self, factory, key, key_size, enumerator): # -> Literal[0]:
        ...
    


IID_IDWriteFactory = ...
class IDWriteRenderingParams(com.pIUnknown):
    _methods_ = ...


class IDWriteFactory(com.pIUnknown):
    _methods_ = ...


IID_IDWriteFactory1 = ...
class IDWriteFactory1(IDWriteFactory, com.pIUnknown):
    _methods_ = ...


class IDWriteFontFallback(com.pIUnknown):
    _methods_ = ...


class IDWriteColorGlyphRunEnumerator(com.pIUnknown):
    _methods_ = ...


class IDWriteFactory2(IDWriteFactory1, IDWriteFactory, com.pIUnknown):
    _methods_ = ...


IID_IDWriteFactory2 = ...
class IDWriteFontSet(com.pIUnknown):
    _methods_ = ...


class IDWriteFontSetBuilder(com.pIUnknown):
    _methods_ = ...


class IDWriteFontSetBuilder1(IDWriteFontSetBuilder, com.pIUnknown):
    _methods_ = ...


class IDWriteFactory3(IDWriteFactory2, com.pIUnknown):
    _methods_ = ...


class IDWriteColorGlyphRunEnumerator1(IDWriteColorGlyphRunEnumerator, com.pIUnknown):
    _methods_ = ...


class IDWriteFactory4(IDWriteFactory3, com.pIUnknown):
    _methods_ = ...


class IDWriteInMemoryFontFileLoader(com.pIUnknown):
    _methods_ = ...


IID_IDWriteFactory5 = ...
class IDWriteFactory5(IDWriteFactory4, IDWriteFactory3, IDWriteFactory2, IDWriteFactory1, IDWriteFactory, com.pIUnknown):
    _methods_ = ...


DWriteCreateFactory = ...
class ID2D1Resource(com.pIUnknown):
    _methods_ = ...


class ID2D1Brush(ID2D1Resource, com.pIUnknown):
    _methods_ = ...


class ID2D1SolidColorBrush(ID2D1Brush, ID2D1Resource, com.pIUnknown):
    _methods_ = ...


D2D1_TEXT_ANTIALIAS_MODE = UINT
D2D1_TEXT_ANTIALIAS_MODE_DEFAULT = ...
D2D1_TEXT_ANTIALIAS_MODE_CLEARTYPE = ...
D2D1_TEXT_ANTIALIAS_MODE_GRAYSCALE = ...
D2D1_TEXT_ANTIALIAS_MODE_ALIASED = ...
D2D1_RENDER_TARGET_TYPE = UINT
D2D1_RENDER_TARGET_TYPE_DEFAULT = ...
D2D1_RENDER_TARGET_TYPE_SOFTWARE = ...
D2D1_RENDER_TARGET_TYPE_HARDWARE = ...
D2D1_FEATURE_LEVEL = UINT
D2D1_FEATURE_LEVEL_DEFAULT = ...
D2D1_RENDER_TARGET_USAGE = UINT
D2D1_RENDER_TARGET_USAGE_NONE = ...
D2D1_RENDER_TARGET_USAGE_FORCE_BITMAP_REMOTING = ...
D2D1_RENDER_TARGET_USAGE_GDI_COMPATIBLE = ...
DXGI_FORMAT = UINT
DXGI_FORMAT_UNKNOWN = ...
D2D1_ALPHA_MODE = UINT
D2D1_ALPHA_MODE_UNKNOWN = ...
D2D1_ALPHA_MODE_PREMULTIPLIED = ...
D2D1_ALPHA_MODE_STRAIGHT = ...
D2D1_ALPHA_MODE_IGNORE = ...
D2D1_DRAW_TEXT_OPTIONS = UINT
D2D1_DRAW_TEXT_OPTIONS_NO_SNAP = ...
D2D1_DRAW_TEXT_OPTIONS_CLIP = ...
D2D1_DRAW_TEXT_OPTIONS_ENABLE_COLOR_FONT = ...
D2D1_DRAW_TEXT_OPTIONS_DISABLE_COLOR_BITMAP_SNAPPING = ...
D2D1_DRAW_TEXT_OPTIONS_NONE = ...
D2D1_DRAW_TEXT_OPTIONS_FORCE_DWORD = ...
class D2D1_PIXEL_FORMAT(Structure):
    _fields_ = ...


class D2D1_RENDER_TARGET_PROPERTIES(Structure):
    _fields_ = ...


DXGI_FORMAT_B8G8R8A8_UNORM = ...
pixel_format = ...
default_target_properties = ...
class ID2D1RenderTarget(ID2D1Resource, com.pIUnknown):
    _methods_ = ...


IID_ID2D1Factory = ...
class ID2D1Factory(com.pIUnknown):
    _methods_ = ...


d2d_lib = ...
D2D1_FACTORY_TYPE = UINT
D2D1_FACTORY_TYPE_SINGLE_THREADED = ...
D2D1_FACTORY_TYPE_MULTI_THREADED = ...
D2D1CreateFactory = ...
wic_decoder = ...
if not wic_decoder:
    ...
def get_system_locale() -> str:
    """Retrieve the string representing the system locale."""
    ...

class DirectWriteGlyphRenderer(base.GlyphRenderer):
    antialias_mode = ...
    draw_options = ...
    measuring_mode = ...
    def __init__(self, font) -> None:
        ...
    
    def render_to_image(self, text, width, height): # -> ImageData:
        """This process takes Pyglet out of the equation and uses only DirectWrite to shape and render text.
        This may allows more accurate fonts (bidi, rtl, etc) in very special circumstances."""
        ...
    
    def get_string_info(self, text, font_face): # -> tuple[Array[c_wchar], int, Array[UINT16], Array[FLOAT], Array[DWRITE_GLYPH_OFFSET], Array[UINT16]]:
        """Converts a string of text into a list of indices and advances used for shaping."""
        ...
    
    def get_glyph_metrics(self, font_face, indices, count): # -> list[Any]:
        """Returns a list of tuples with the following metrics per indice:
            (glyph width, glyph height, lsb, advanceWidth)
        """
        ...
    
    def is_color_run(self, run): # -> bool:
        """Will return True if the run contains a colored glyph."""
        ...
    
    def render_single_glyph(self, font_face, indice, advance, offset, metrics): # -> None:
        """Renders a single glyph using D2D DrawGlyphRun"""
        ...
    
    def render_using_layout(self, text): # -> None:
        """This will render text given the built in DirectWrite layout. This process allows us to take
        advantage of color glyphs and fallback handling that is built into DirectWrite.
        This can also handle shaping and many other features if you want to render directly to a texture."""
        ...
    
    def create_zero_glyph(self):
        """Zero glyph is a 1x1 image that has a -1 advance. This is to fill in for ligature substitutions since
        font system requires 1 glyph per character in a string."""
        ...
    


class Win32DirectWriteFont(base.Font):
    _custom_collection = ...
    _write_factory = ...
    _font_loader = ...
    _font_builder = ...
    _font_set = ...
    _font_collection_loader = ...
    _font_cache = ...
    _font_loader_key = ...
    _default_name = ...
    _glyph_renderer = ...
    _empty_glyph = ...
    _zero_glyph = ...
    glyph_renderer_class = DirectWriteGlyphRenderer
    texture_internalformat = ...
    def __init__(self, name, size, bold=..., italic=..., stretch=..., dpi=..., locale=...) -> None:
        ...
    
    @property
    def filename(self): # -> str:
        """Returns a filename associated with the font face.
        Note: Capable of returning more than 1 file in the future, but will do just one for now."""
        ...
    
    @property
    def name(self): # -> str | Any:
        ...
    
    def render_to_image(self, text, width=..., height=...): # -> ImageData:
        """This process takes Pyglet out of the equation and uses only DirectWrite to shape and render text.
        This may allow more accurate fonts (bidi, rtl, etc) in very special circumstances at the cost of
        additional texture space.

        :Parameters:
            `text` : str
                String of text to render.

        :rtype: `ImageData`
        :return: An image of the text.
        """
        ...
    
    def copy_glyph(self, glyph, advance, offset): # -> Glyph:
        """This takes the existing glyph texture and puts it into a new Glyph with a new advance.
        Texture memory is shared between both glyphs."""
        ...
    
    def is_fallback_str_colored(self, font_face, text): # -> bool:
        ...
    
    def get_glyphs_no_shape(self, text): # -> list[Any]:
        """This differs in that it does not attempt to shape the text at all. May be useful in cases where your font
        has no special shaping requirements, spacing is the same, or some other reason where faster performance is
        wanted and you can get away with this."""
        ...
    
    def get_glyphs(self, text): # -> list[Any]:
        ...
    
    def create_text_layout(self, text): # -> IDWriteTextLayout:
        ...
    
    @classmethod
    def add_font_data(cls, data): # -> None:
        ...
    
    @classmethod
    def get_collection(cls, font_name) -> Tuple[Optional[int], Optional[IDWriteFontCollection1]]:
        """Returns which collection this font belongs to (system or custom collection), as well as its index in the
        collection."""
        ...
    
    @classmethod
    def find_font_face(cls, font_name, bold, italic, stretch) -> Tuple[Optional[IDWriteFont], Optional[IDWriteFontCollection]]:
        """This will search font collections for legacy RBIZ names. However, matching to bold, italic, stretch is
        problematic in that there are many values. We parse the font name looking for matches to the name database,
        and attempt to pick the closest match.
        This will search all fonts on the system and custom loaded, and all of their font faces. Returns a collection
        and IDWriteFont if successful.
        """
        ...
    
    @classmethod
    def have_font(cls, name: str): # -> bool:
        ...
    
    @staticmethod
    def parse_name(font_name: str, weight: int, style: int, stretch: int): # -> tuple[int, int, int]:
        """Attempt at parsing any special names in a font for legacy checks. Takes the first found."""
        ...
    
    @staticmethod
    def find_legacy_font(collection: IDWriteFontCollection, font_name: str, bold, italic, stretch, full_debug=...) -> Optional[IDWriteFont]:
        ...
    
    @staticmethod
    def match_closest_font(font_list: List[Tuple[int, int, int, IDWriteFont]], bold: int, italic: int, stretch: int) -> Optional[IDWriteFont]:
        """Match the closest font to the parameters specified. If a full match is not found, a secondary match will be
        found based on similar features. This can probably be improved, but it is possible you could get a different
        font style than expected."""
        ...
    
    @staticmethod
    def unpack_localized_string(local_string: IDWriteLocalizedStrings, locale: str) -> List[str]:
        """Takes IDWriteLocalizedStrings and unpacks the strings inside of it into a list."""
        ...
    
    @staticmethod
    def get_localized_index(strings: IDWriteLocalizedStrings, locale: str): # -> int:
        ...
    


d2d_factory = ...
hr = ...
WICBitmapCreateCacheOption = UINT
WICBitmapNoCache = ...
WICBitmapCacheOnDemand = ...
WICBitmapCacheOnLoad = ...
transparent = ...
white = ...
no_offset = ...
if pyglet.options["win32_disable_shaping"]:
    ...
