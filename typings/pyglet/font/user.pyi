"""
This type stub file was generated by pyright.
"""

from typing import List, Optional, Protocol, TYPE_CHECKING
from pyglet.font import base
from pyglet.image import ImageData
from pyglet.font.base import Glyph

SCALING_ENABLED = ...
SCALING_ENABLED = ...
if TYPE_CHECKING:
    ...
class UserDefinedGlyphRenderer(base.GlyphRenderer):
    def __init__(self, font: UserDefinedFontBase) -> None:
        ...
    
    def render(self, image_data: ImageData): # -> TextureRegion:
        ...
    


class UserDefinedFontBase(base.Font):
    glyph_renderer_class = UserDefinedGlyphRenderer
    def __init__(self, name: str, default_char: str, size: int, ascent: Optional[int] = ..., descent: Optional[int] = ..., bold: bool = ..., italic: bool = ..., stretch: bool = ..., dpi: int = ..., locale: Optional[str] = ...) -> None:
        ...
    
    @property
    def name(self) -> str:
        ...
    
    def enable_scaling(self, base_size: int): # -> None:
        ...
    


class UserDefinedFontException(Exception):
    ...


class DictLikeObject(Protocol):
    def get(self, char: str) -> Optional[ImageData]:
        ...
    


class UserDefinedMappingFont(UserDefinedFontBase):
    """The default UserDefinedFont, it can take mappings of characters to ImageData to make a User defined font."""
    def __init__(self, name: str, default_char: str, size: int, mappings: DictLikeObject, ascent: Optional[int] = ..., descent: Optional[int] = ..., bold: bool = ..., italic: bool = ..., stretch: bool = ..., dpi: int = ..., locale: Optional[str] = ...) -> None:
        """Create a custom font using the mapping dict.

        :Parameters:
            `name` : str
                Name of the font.
            `default_char` : str
                If a character in a string is not found in the font,
                it will use this as fallback.
            `size` : int
                Font size.
            `mappings` : DictLikeObject
                A dict or dict-like object with a get function.
                The get function must take a string character, and output ImageData if found.
                It also must return None if no character is found.
            `ascent` : int
                Maximum ascent above the baseline, in pixels. If None, the image height is used.
            `descent` : int
                Maximum descent below the baseline, in pixels. Usually negative.
        """
        ...
    
    def enable_scaling(self, base_size: int) -> None:
        ...
    
    def get_glyphs(self, text: str) -> List[Glyph]:
        """Create and return a list of Glyphs for `text`.

        If any characters do not have a known glyph representation in this
        font, a substitution will be made with the default_char.

        :Parameters:
            `text` : str or unicode
                Text to render.

        :rtype: list of `Glyph`
        """
        ...
    


def get_scaled_user_font(font_base: UserDefinedMappingFont, size: int): # -> UserDefinedMappingFont:
    """This function will return a new font that can scale it's size based off the original base font."""
    ...

__all__ = ("UserDefinedFontBase", "UserDefinedFontException", "UserDefinedMappingFont", "get_scaled_user_font")
