"""
This type stub file was generated by pyright.
"""

import re
from typing import IO
import weakref
import pyglet
from ctypes import *
from io import BytesIO, open
from pyglet.gl import *
from pyglet.gl import gl_info
from pyglet.util import asbytes
from .codecs import ImageDecodeException, ImageEncodeException, add_default_codecs as _add_default_codecs, registry as _codec_registry
from .animation import Animation, AnimationFrame
from .buffer import *
from . import atlas
from pyglet.image.codecs import ImageDecoder

"""Image load, capture and high-level texture functions.

Only basic functionality is described here; for full reference see the
accompanying documentation.

To load an image::

    from pyglet import image
    pic = image.load('picture.png')

The supported image file types include PNG, BMP, GIF, JPG, and many more,
somewhat depending on the operating system.  To load an image from a file-like
object instead of a filename::

    pic = image.load('hint.jpg', file=fileobj)

The hint helps the module locate an appropriate decoder to use based on the
file extension.  It is optional.

Once loaded, images can be used directly by most other modules of pyglet.  All
images have a width and height you can access::

    width, height = pic.width, pic.height

You can extract a region of an image (this keeps the original image intact;
the memory is shared efficiently)::

    subimage = pic.get_region(x, y, width, height)

Remember that y-coordinates are always increasing upwards.

Drawing images
--------------

To draw an image at some point on the screen::

    pic.blit(x, y, z)

This assumes an appropriate view transform and projection have been applied.

Some images have an intrinsic "anchor point": this is the point which will be
aligned to the ``x`` and ``y`` coordinates when the image is drawn.  By
default the anchor point is the lower-left corner of the image.  You can use
the anchor point to center an image at a given point, for example::

    pic.anchor_x = pic.width // 2
    pic.anchor_y = pic.height // 2
    pic.blit(x, y, z)

Texture access
--------------

If you are using OpenGL directly, you can access the image as a texture::

    texture = pic.get_texture()

(This is the most efficient way to obtain a texture; some images are
immediately loaded as textures, whereas others go through an intermediate
form).  To use a texture with pyglet.gl::

    from pyglet.gl import *
    glEnable(texture.target)        # typically target is GL_TEXTURE_2D
    glBindTexture(texture.target, texture.id)
    # ... draw with the texture

Pixel access
------------

To access raw pixel data of an image::

    rawimage = pic.get_image_data()

(If the image has just been loaded this will be a very quick operation;
however if the image is a texture a relatively expensive readback operation
will occur).  The pixels can be accessed as a string::

    format = 'RGBA'
    pitch = rawimage.width * len(format)
    pixels = rawimage.get_data(format, pitch)

"format" strings consist of characters that give the byte order of each color
component.  For example, if rawimage.format is 'RGBA', there are four color
components: red, green, blue and alpha, in that order.  Other common format
strings are 'RGB', 'LA' (luminance, alpha) and 'I' (intensity).

The "pitch" of an image is the number of bytes in a row (this may validly be
more than the number required to make up the width of the image, it is common
to see this for word alignment).  If "pitch" is negative the rows of the image
are ordered from top to bottom, otherwise they are ordered from bottom to top.

Retrieving data with the format and pitch given in `ImageData.format` and
`ImageData.pitch` avoids the need for data conversion (assuming you can make
use of the data in this arbitrary format).

"""
class ImageException(Exception):
    ...


class TextureArraySizeExceeded(Exception):
    """Exception occurs ImageData dimensions are larger than the array supports."""
    ...


class TextureArrayDepthExceeded(Exception):
    """Exception occurs when depth has hit the maximum supported of the array."""
    ...


def load(filename: str, file: IO[bytes] | None =..., decoder: ImageDecoder | None =...) -> AbstractImage:
    """Load an image from a file.

    :Parameters:
        `filename` : str
            Used to guess the image format, and to load the file if `file` is
            unspecified.
        `file` : file-like object or None
            Source of image data in any supported format.
        `decoder` : ImageDecoder or None
            If unspecified, all decoders that are registered for the filename
            extension are tried.  If none succeed, the exception from the
            first decoder is raised.

    :rtype: AbstractImage

    .. note:: You can make no assumptions about the return type; usually it will
        be ImageData or CompressedImageData, but decoders are free to return
        any subclass of AbstractImage.

    """
    ...

def load_animation(filename, file=..., decoder=...):
    """Load an animation from a file.

    Currently, the only supported format is GIF.

    :Parameters:
        `filename` : str
            Used to guess the animation format, and to load the file if `file`
            is unspecified.
        `file` : file-like object or None
            File object containing the animation stream.
        `decoder` : ImageDecoder or None
            If unspecified, all decoders that are registered for the filename
            extension are tried.  If none succeed, the exception from the
            first decoder is raised.

    :rtype: Animation
    """
    ...

def create(width, height, pattern=...): # -> ImageData:
    """Create an image optionally filled with the given pattern.

    :Parameters:
        `width` : int
            Width of image to create
        `height` : int
            Height of image to create
        `pattern` : ImagePattern or None
            Pattern to fill image with.  If unspecified, the image will
            initially be transparent.

    :rtype: AbstractImage

    .. note:: You can make no assumptions about the return type; usually it will
              be ImageData or CompressedImageData, but patterns are free to return
              any subclass of AbstractImage.
    """
    ...

def get_max_texture_size(): # -> int:
    """Query the maximum texture size available"""
    ...

def get_max_array_texture_layers(): # -> int:
    """Query the maximum TextureArray depth"""
    ...

class ImagePattern:
    """Abstract image creation class."""
    def create_image(self, width, height):
        """Create an image of the given size.

        :Parameters:
            `width` : int
                Width of image to create
            `height` : int
                Height of image to create

        :rtype: AbstractImage
        """
        ...
    


class SolidColorImagePattern(ImagePattern):
    """Creates an image filled with a solid color."""
    def __init__(self, color=...) -> None:
        """Create a solid image pattern with the given color.

        :Parameters:
            `color` : (int, int, int, int)
                4-tuple of ints in range [0,255] giving RGBA components of
                color to fill with.

        """
        ...
    
    def create_image(self, width, height): # -> ImageData:
        ...
    


class CheckerImagePattern(ImagePattern):
    """Create an image with a tileable checker image.
    """
    def __init__(self, color1=..., color2=...) -> None:
        """Initialise with the given colors.

        :Parameters:
            `color1` : (int, int, int, int)
                4-tuple of ints in range [0,255] giving RGBA components of
                color to fill with.  This color appears in the top-left and
                bottom-right corners of the image.
            `color2` : (int, int, int, int)
                4-tuple of ints in range [0,255] giving RGBA components of
                color to fill with.  This color appears in the top-right and
                bottom-left corners of the image.

        """
        ...
    
    def create_image(self, width, height): # -> ImageData:
        ...
    


class AbstractImage:
    """Abstract class representing an image.

    :Parameters:
        `width` : int
            Width of image
        `height` : int
            Height of image
        `anchor_x` : int
            X coordinate of anchor, relative to left edge of image data
        `anchor_y` : int
            Y coordinate of anchor, relative to bottom edge of image data
    """
    width: int
    height: int
    anchor_x = ...
    anchor_y = ...
    def __init__(self, width: int, height: int) -> None:
        ...
    
    def __repr__(self): # -> str:
        ...
    
    def get_image_data(self):
        """Get an ImageData view of this image.

        Changes to the returned instance may or may not be reflected in this
        image.

        :rtype: :py:class:`~pyglet.image.ImageData`

        .. versionadded:: 1.1
        """
        ...
    
    def get_texture(self, rectangle=...):
        """A :py:class:`~pyglet.image.Texture` view of this image.

        :Parameters:
            `rectangle` : bool
                Unused. Kept for compatibility.

                .. versionadded:: 1.1.4.
        :rtype: :py:class:`~pyglet.image.Texture`

        .. versionadded:: 1.1
        """
        ...
    
    def get_mipmapped_texture(self):
        """Retrieve a :py:class:`~pyglet.image.Texture` instance with all mipmap levels filled in.

        :rtype: :py:class:`~pyglet.image.Texture`

        .. versionadded:: 1.1
        """
        ...
    
    def get_region(self, x: int, y: int, width: int, height: int) -> AbstractImage:
        """Retrieve a rectangular region of this image.

        :Parameters:
            `x` : int
                Left edge of region.
            `y` : int
                Bottom edge of region.
            `width` : int
                Width of region.
            `height` : int
                Height of region.

        :rtype: AbstractImage
        """
        ...
    
    def save(self, filename=..., file=..., encoder=...): # -> None:
        """Save this image to a file.

        :Parameters:
            `filename` : str
                Used to set the image file format, and to open the output file
                if `file` is unspecified.
            `file` : file-like object or None
                File to write image data to.
            `encoder` : ImageEncoder or None
                If unspecified, all encoders matching the filename extension
                are tried.  If all fail, the exception from the first one
                attempted is raised.

        """
        ...
    
    def blit(self, x, y, z=...):
        """Draw this image to the active framebuffers.

        The image will be drawn with the lower-left corner at
        (``x -`` `anchor_x`, ``y -`` `anchor_y`, ``z``).
        """
        ...
    
    def blit_into(self, source, x, y, z):
        """Draw `source` on this image.

        `source` will be copied into this image such that its anchor point
        is aligned with the `x` and `y` parameters.  If this image is a 3D
        texture, the `z` coordinate gives the image slice to copy into.

        Note that if `source` is larger than this image (or the positioning
        would cause the copy to go out of bounds) then you must pass a
        region of `source` to this method, typically using get_region().
        """
        ...
    
    def blit_to_texture(self, target, level, x, y, z=...):
        """Draw this image on the currently bound texture at `target`.

        This image is copied into the texture such that this image's anchor
        point is aligned with the given `x` and `y` coordinates of the
        destination texture.  If the currently bound texture is a 3D texture,
        the `z` coordinate gives the image slice to blit into.
        """
        ...
    


class AbstractImageSequence:
    """Abstract sequence of images.

    The sequence is useful for storing image animations or slices of a volume.
    For efficient access, use the `texture_sequence` member.  The class
    also implements the sequence interface (`__len__`, `__getitem__`,
    `__setitem__`).
    """
    def get_texture_sequence(self):
        """Get a TextureSequence.

        :rtype: `TextureSequence`

        .. versionadded:: 1.1
        """
        ...
    
    def get_animation(self, period, loop=...): # -> Animation:
        """Create an animation over this image sequence for the given constant
        framerate.

        :Parameters
            `period` : float
                Number of seconds to display each frame.
            `loop` : bool
                If True, the animation will loop continuously.

        :rtype: :py:class:`~pyglet.image.Animation`

        .. versionadded:: 1.1
        """
        ...
    
    def __getitem__(self, slice):
        """Retrieve a (list of) image.

        :rtype: AbstractImage
        """
        ...
    
    def __setitem__(self, slice, image):
        """Replace one or more images in the sequence.

        :Parameters:
            `image` : `~pyglet.image.AbstractImage`
                The replacement image.  The actual instance may not be used,
                depending on this implementation.

        """
        ...
    
    def __len__(self):
        ...
    
    def __iter__(self):
        """Iterate over the images in sequence.

        :rtype: Iterator

        .. versionadded:: 1.1
        """
        ...
    


class TextureSequence(AbstractImageSequence):
    """Interface for a sequence of textures.

    Typical implementations store multiple :py:class:`~pyglet.image.TextureRegion` s within one
    :py:class:`~pyglet.image.Texture` so as to minimise state changes.
    """
    def get_texture_sequence(self): # -> Self:
        ...
    


class UniformTextureSequence(TextureSequence):
    """Interface for a sequence of textures, each with the same dimensions.

    :Parameters:
        `item_width` : int
            Width of each texture in the sequence.
        `item_height` : int
            Height of each texture in the sequence.

    """
    @property
    def item_width(self):
        ...
    
    @property
    def item_height(self):
        ...
    


class ImageData(AbstractImage):
    """An image represented as a string of unsigned bytes.

    :Parameters:
        `data` : str
            Pixel data, encoded according to `format` and `pitch`.
        `format` : str
            The format string to use when reading or writing `data`.
        `pitch` : int
            Number of bytes per row.  Negative values indicate a top-to-bottom
            arrangement.

    """
    _swap1_pattern = ...
    _swap2_pattern = ...
    _swap3_pattern = ...
    _swap4_pattern = ...
    _current_texture = ...
    _current_mipmap_texture = ...
    def __init__(self, width, height, fmt, data, pitch=...) -> None:
        """Initialise image data.

        :Parameters:
            `width` : int
                Width of image data
            `height` : int
                Height of image data
            `fmt` : str
                A valid format string, such as 'RGB', 'RGBA', 'ARGB', etc.
            `data` : sequence
                String or array/list of bytes giving the decoded data.
            `pitch` : int or None
                If specified, the number of bytes per row.  Negative values
                indicate a top-to-bottom arrangement.  Defaults to
                ``width * len(format)``.

        """
        ...
    
    def __getstate__(self): # -> dict[str, Any | bytes | list[Any]]:
        ...
    
    def get_image_data(self): # -> Self:
        ...
    
    @property
    def format(self):
        """Format string of the data.  Read-write.

        :type: str
        """
        ...
    
    @format.setter
    def format(self, fmt): # -> None:
        ...
    
    def get_data(self, fmt=..., pitch=...): # -> Any | bytes:
        """Get the byte data of the image.

        :Parameters:
            `fmt` : str
                Format string of the return data.
            `pitch` : int
                Number of bytes per row.  Negative values indicate a
                top-to-bottom arrangement.

        .. versionadded:: 1.1

        :rtype: sequence of bytes, or str
        """
        ...
    
    def set_data(self, fmt, pitch, data): # -> None:
        """Set the byte data of the image.

        :Parameters:
            `fmt` : str
                Format string of the return data.
            `pitch` : int
                Number of bytes per row.  Negative values indicate a
                top-to-bottom arrangement.
            `data` : str or sequence of bytes
                Image data.

        .. versionadded:: 1.1
        """
        ...
    
    def set_mipmap_image(self, level, image): # -> None:
        """Set a mipmap image for a particular level.

        The mipmap image will be applied to textures obtained via
        `get_mipmapped_texture`.

        :Parameters:
            `level` : int
                Mipmap level to set image at, must be >= 1.
            `image` : AbstractImage
                Image to set.  Must have correct dimensions for that mipmap
                level (i.e., width >> level, height >> level)
        """
        ...
    
    def create_texture(self, cls, rectangle=...):
        """Create a texture containing this image.

        :Parameters:
            `cls` : class (subclass of Texture)
                Class to construct.
            `rectangle` : bool
                Unused. kept for compatibility.

                .. versionadded:: 1.1

        :rtype: cls or cls.region_class
        """
        ...
    
    def get_texture(self, rectangle=...): # -> Texture:
        ...
    
    def get_mipmapped_texture(self): # -> Texture:
        """Return a Texture with mipmaps.

        If :py:class:`~pyglet.image.set_mipmap_Image` has been called with at least one image, the set
        of images defined will be used.  Otherwise, mipmaps will be
        automatically generated.

        :rtype: :py:class:`~pyglet.image.Texture`

        .. versionadded:: 1.1
        """
        ...
    
    def get_region(self, x, y, width, height): # -> ImageDataRegion:
        """Retrieve a rectangular region of this image data.

        :Parameters:
            `x` : int
                Left edge of region.
            `y` : int
                Bottom edge of region.
            `width` : int
                Width of region.
            `height` : int
                Height of region.

        :rtype: ImageDataRegion
        """
        ...
    
    def blit(self, x, y, z=..., width=..., height=...): # -> None:
        ...
    
    def blit_to_texture(self, target, level, x, y, z, internalformat=...): # -> None:
        """Draw this image to to the currently bound texture at `target`.

        This image's anchor point will be aligned to the given `x` and `y`
        coordinates.  If the currently bound texture is a 3D texture, the `z`
        parameter gives the image slice to blit into.

        If `internalformat` is specified, glTexImage is used to initialise
        the texture; otherwise, glTexSubImage is used to update a region.
        """
        ...
    


class ImageDataRegion(ImageData):
    def __init__(self, x, y, width, height, image_data) -> None:
        ...
    
    def __getstate__(self): # -> dict[str, Any | bytes | int | list[Any]]:
        ...
    
    def get_data(self, fmt=..., pitch=...): # -> Any | bytes:
        ...
    
    def set_data(self, fmt, pitch, data): # -> None:
        ...
    
    def get_region(self, x, y, width, height): # -> ImageDataRegion:
        ...
    


class CompressedImageData(AbstractImage):
    """Image representing some compressed data suitable for direct uploading
    to driver.
    """
    _current_texture = ...
    _current_mipmap_texture = ...
    def __init__(self, width, height, gl_format, data, extension=..., decoder=...) -> None:
        """Construct a CompressedImageData with the given compressed data.

        :Parameters:
            `width` : int
                Width of image
            `height` : int
                Height of image
            `gl_format` : int
                GL constant giving format of compressed data; for example,
                ``GL_COMPRESSED_RGBA_S3TC_DXT5_EXT``.
            `data` : sequence
                String or array/list of bytes giving compressed image data.
            `extension` : str or None
                If specified, gives the name of a GL extension to check for
                before creating a texture.
            `decoder` : function(data, width, height) -> AbstractImage
                A function to decode the compressed data, to be used if the
                required extension is not present.

        """
        ...
    
    def set_mipmap_data(self, level, data): # -> None:
        """Set data for a mipmap level.

        Supplied data gives a compressed image for the given mipmap level.
        The image must be of the correct dimensions for the level
        (i.e., width >> level, height >> level); but this is not checked.  If
        any mipmap levels are specified, they are used; otherwise, mipmaps for
        `mipmapped_texture` are generated automatically.

        :Parameters:
            `level` : int
                Level of mipmap image to set.
            `data` : sequence
                String or array/list of bytes giving compressed image data.
                Data must be in same format as specified in constructor.

        """
        ...
    
    def get_texture(self, rectangle=...): # -> Texture:
        ...
    
    def get_mipmapped_texture(self): # -> Texture:
        ...
    
    def blit_to_texture(self, target, level, x, y, z): # -> None:
        ...
    


class Texture(AbstractImage):
    """An image loaded into video memory that can be efficiently drawn
    to the framebuffer.

    Typically, you will get an instance of Texture by accessing the `texture`
    member of any other AbstractImage.

    :Parameters:
        `region_class` : class (subclass of TextureRegion)
            Class to use when constructing regions of this texture.
        `tex_coords` : tuple
            12-tuple of float, named (u1, v1, r1, u2, v2, r2, ...).  u, v, r
            give the 3D texture coordinates for vertices 1-4.  The vertices
            are specified in the order bottom-left, bottom-right, top-right
            and top-left.
        `target` : int
            The GL texture target (e.g., ``GL_TEXTURE_2D``).
        `level` : int
            The mipmap level of this texture.

    """
    region_class = ...
    tex_coords = ...
    tex_coords_order = ...
    colors = ...
    level = ...
    images = ...
    z = ...
    default_min_filter = ...
    default_mag_filter = ...
    def __init__(self, width, height, target, tex_id) -> None:
        ...
    
    def delete(self): # -> None:
        """Delete this texture and the memory it occupies.
        After this, it may not be used anymore.
        """
        ...
    
    def __del__(self): # -> None:
        ...
    
    def bind(self, texture_unit: int = ...): # -> None:
        """Bind to a specific Texture Unit by number."""
        ...
    
    def bind_image_texture(self, unit, level=..., layered=..., layer=..., access=..., fmt=...): # -> None:
        """Bind as an ImageTexture for use with a :py:class:`~pyglet.shader.ComputeShaderProgram`.

        .. note:: OpenGL 4.3, or 4.2 with the GL_ARB_compute_shader extention is required.
        """
        ...
    
    @classmethod
    def create(cls, width, height, target=..., internalformat=..., min_filter=..., mag_filter=..., fmt=..., blank_data=...): # -> Self:
        """Create a Texture

        Create a Texture with the specified dimentions, target and format.
        On return, the texture will be bound.

        :Parameters:
            `width` : int
                Width of texture in pixels.
            `height` : int
                Height of texture in pixels.
            `target` : int
                GL constant giving texture target to use, typically ``GL_TEXTURE_2D``.
            `internalformat` : int
                GL constant giving internal format of texture; for example, ``GL_RGBA``.
                The internal format decides how the texture data will be stored internally.
                If ``None``, the texture will be created but not initialized.
            `min_filter` : int
                The minifaction filter used for this texture, commonly ``GL_LINEAR`` or ``GL_NEAREST``
            `mag_filter` : int
                The magnification filter used for this texture, commonly ``GL_LINEAR`` or ``GL_NEAREST``
            `fmt` : int
                GL constant giving format of texture; for example, ``GL_RGBA``.
                The format specifies what format the pixel data we're expecting to write
                to the texture and should ideally be the same as for internal format.
            `blank_data` : bool
                Setting to True will initialize the texture data with all zeros. Setting False, will initialize Texture
                with no data.

        :rtype: :py:class:`~pyglet.image.Texture`
        """
        ...
    
    def get_image_data(self, z=...): # -> ImageDataRegion | ImageData:
        """Get the image data of this texture.

        Changes to the returned instance will not be reflected in this
        texture.

        :Parameters:
            `z` : int
                For 3D textures, the image slice to retrieve.

        :rtype: :py:class:`~pyglet.image.ImageData`
        """
        ...
    
    def get_texture(self, rectangle=...): # -> Self:
        ...
    
    def blit(self, x, y, z=..., width=..., height=...): # -> None:
        ...
    
    def blit_into(self, source, x, y, z): # -> None:
        ...
    
    def get_region(self, x, y, width, height):
        ...
    
    def get_transform(self, flip_x=..., flip_y=..., rotate=...):
        """Create a copy of this image applying a simple transformation.

        The transformation is applied to the texture coordinates only;
        :py:meth:`~pyglet.image.ImageData.get_image_data` will return the untransformed data.  The
        transformation is applied around the anchor point.

        :Parameters:
            `flip_x` : bool
                If True, the returned image will be flipped horizontally.
            `flip_y` : bool
                If True, the returned image will be flipped vertically.
            `rotate` : int
                Degrees of clockwise rotation of the returned image.  Only
                90-degree increments are supported.

        :rtype: :py:class:`~pyglet.image.TextureRegion`
        """
        ...
    
    @property
    def uv(self): # -> tuple[Any | Literal[0], Any | Literal[0], Any | Literal[1], Any | Literal[1]]:
        """Tuple containing the left, bottom, right, top 2D texture coordinates."""
        ...
    
    def __repr__(self): # -> str:
        ...
    


class TextureRegion(Texture):
    """A rectangular region of a texture, presented as if it were a separate texture.
    """
    def __init__(self, x, y, z, width, height, owner) -> None:
        ...
    
    def get_image_data(self):
        ...
    
    def get_region(self, x, y, width, height):
        ...
    
    def blit_into(self, source, x, y, z): # -> None:
        ...
    
    def __repr__(self): # -> str:
        ...
    
    def delete(self): # -> None:
        """Deleting a TextureRegion has no effect. Operate on the owning
        texture instead.
        """
        ...
    
    def __del__(self): # -> None:
        ...
    


class Texture3D(Texture, UniformTextureSequence):
    """A texture with more than one image slice.

    Use `create_for_images` or `create_for_image_grid` classmethod to
    construct.
    """
    item_width = ...
    item_height = ...
    items = ...
    @classmethod
    def create_for_images(cls, images, internalformat=..., blank_data=...): # -> Self:
        ...
    
    @classmethod
    def create_for_image_grid(cls, grid, internalformat=...): # -> Self:
        ...
    
    def __len__(self): # -> int:
        ...
    
    def __getitem__(self, index): # -> tuple[Any, ...]:
        ...
    
    def __setitem__(self, index, value): # -> None:
        ...
    
    def __iter__(self): # -> Iterator[Never]:
        ...
    


class TextureArrayRegion(TextureRegion):
    """A region of a TextureArray, presented as if it were a separate texture.
    """
    def __repr__(self): # -> str:
        ...
    


class TextureArray(Texture, UniformTextureSequence):
    def __init__(self, width, height, target, tex_id, max_depth) -> None:
        ...
    
    @classmethod
    def create(cls, width, height, internalformat=..., min_filter=..., mag_filter=..., max_depth=...): # -> Self:
        """Create an empty TextureArray.

        You may specify the maximum depth, or layers, the Texture Array should have. This defaults
        to 256, but will be hardware and driver dependent.

        :Parameters:
            `width` : int
                Width of the texture.
            `height` : int
                Height of the texture.
            `internalformat` : int
                GL constant giving the internal format of the texture array; for example, ``GL_RGBA``.
            `min_filter` : int
                The minifaction filter used for this texture array, commonly ``GL_LINEAR`` or ``GL_NEAREST``
            `mag_filter` : int
                The magnification filter used for this texture array, commonly ``GL_LINEAR`` or ``GL_NEAREST``
            `max_depth` : int
                The number of layers in the texture array.

        :rtype: :py:class:`~pyglet.image.TextureArray`

        .. versionadded:: 2.0
        """
        ...
    
    def add(self, image: pyglet.image.ImageData):
        ...
    
    def allocate(self, *images): # -> list[Any]:
        """Allocates multiple images at once."""
        ...
    
    @classmethod
    def create_for_image_grid(cls, grid, internalformat=...): # -> Self:
        ...
    
    def __len__(self): # -> int:
        ...
    
    def __getitem__(self, index):
        ...
    
    def __setitem__(self, index, value): # -> None:
        ...
    
    def __iter__(self): # -> Iterator[Any]:
        ...
    


class TileableTexture(Texture):
    """A texture that can be tiled efficiently.

    Use :py:class:`~pyglet.image.create_for_image` classmethod to construct.
    """
    def get_region(self, x, y, width, height):
        ...
    
    def blit_tiled(self, x, y, z, width, height): # -> None:
        """Blit this texture tiled over the given area.

        The image will be tiled with the bottom-left corner of the destination
        rectangle aligned with the anchor point of this texture.
        """
        ...
    
    @classmethod
    def create_for_image(cls, image):
        ...
    


class ImageGrid(AbstractImage, AbstractImageSequence):
    """An imaginary grid placed over an image allowing easy access to
    regular regions of that image.

    The grid can be accessed either as a complete image, or as a sequence
    of images.  The most useful applications are to access the grid
    as a :py:class:`~pyglet.image.TextureGrid`::

        image_grid = ImageGrid(...)
        texture_grid = image_grid.get_texture_sequence()

    or as a :py:class:`~pyglet.image.Texture3D`::

        image_grid = ImageGrid(...)
        texture_3d = Texture3D.create_for_image_grid(image_grid)

    """
    _items = ...
    _texture_grid = ...
    def __init__(self, image, rows, columns, item_width=..., item_height=..., row_padding=..., column_padding=...) -> None:
        """Construct a grid for the given image.

        You can specify parameters for the grid, for example setting
        the padding between cells.  Grids are always aligned to the
        bottom-left corner of the image.

        :Parameters:
            `image` : AbstractImage
                Image over which to construct the grid.
            `rows` : int
                Number of rows in the grid.
            `columns` : int
                Number of columns in the grid.
            `item_width` : int
                Width of each column.  If unspecified, is calculated such
                that the entire image width is used.
            `item_height` : int
                Height of each row.  If unspecified, is calculated such that
                the entire image height is used.
            `row_padding` : int
                Pixels separating adjacent rows.  The padding is only
                inserted between rows, not at the edges of the grid.
            `column_padding` : int
                Pixels separating adjacent columns.  The padding is only
                inserted between columns, not at the edges of the grid.
        """
        ...
    
    def get_texture(self, rectangle=...):
        ...
    
    def get_image_data(self):
        ...
    
    def get_texture_sequence(self): # -> TextureGrid:
        ...
    
    def __len__(self):
        ...
    
    def __getitem__(self, index): # -> tuple[Any, ...]:
        ...
    
    def __iter__(self): # -> Iterator[Never]:
        ...
    


class TextureGrid(TextureRegion, UniformTextureSequence):
    """A texture containing a regular grid of texture regions.

    To construct, create an :py:class:`~pyglet.image.ImageGrid` first::

        image_grid = ImageGrid(...)
        texture_grid = TextureGrid(image_grid)

    The texture grid can be accessed as a single texture, or as a sequence
    of :py:class:`~pyglet.image.TextureRegion`.  When accessing as a sequence, you can specify
    integer indexes, in which the images are arranged in rows from the
    bottom-left to the top-right::

        # assume the texture_grid is 3x3:
        current_texture = texture_grid[3] # get the middle-left image

    You can also specify tuples in the sequence methods, which are addressed
    as ``row, column``::

        # equivalent to the previous example:
        current_texture = texture_grid[1, 0]

    When using tuples in a slice, the returned sequence is over the
    rectangular region defined by the slice::

        # returns center, center-right, center-top, top-right images in that
        # order:
        images = texture_grid[(1,1):]
        # equivalent to
        images = texture_grid[(1,1):(3,3)]

    """
    items = ...
    rows = ...
    columns = ...
    item_width = ...
    item_height = ...
    def __init__(self, grid) -> None:
        ...
    
    def get(self, row, column): # -> tuple[Any, ...] | list[Any] | None:
        ...
    
    def __getitem__(self, index): # -> tuple[Any, ...] | list[Any] | None:
        ...
    
    def __setitem__(self, index, value): # -> None:
        ...
    
    def __len__(self): # -> int:
        ...
    
    def __iter__(self): # -> Iterator[Never]:
        ...
    


class BufferManager:
    """Manages the set of framebuffers for a context.

    Use :py:func:`~pyglet.image.get_buffer_manager` to obtain the instance of this class for the
    current context.
    """
    def __init__(self) -> None:
        ...
    
    @staticmethod
    def get_viewport(): # -> Array[GLint]:
        """Get the current OpenGL viewport dimensions.

        :rtype: 4-tuple of float.
        :return: Left, top, right and bottom dimensions.
        """
        ...
    
    def get_color_buffer(self): # -> ColorBufferImage:
        """Get the color buffer.

        :rtype: :py:class:`~pyglet.image.ColorBufferImage`
        """
        ...
    
    def get_depth_buffer(self): # -> DepthBufferImage:
        """Get the depth buffer.

        :rtype: :py:class:`~pyglet.image.DepthBufferImage`
        """
        ...
    
    def get_buffer_mask(self): # -> BufferImageMask:
        """Get a free bitmask buffer.

        A bitmask buffer is a buffer referencing a single bit in the stencil
        buffer.  If no bits are free, `ImageException` is raised.  Bits are
        released when the bitmask buffer is garbage collected.

        :rtype: :py:class:`~pyglet.image.BufferImageMask`
        """
        ...
    


def get_buffer_manager(): # -> BufferManager:
    """Get the buffer manager for the current OpenGL context.

    :rtype: :py:class:`~pyglet.image.BufferManager`
    """
    ...

class BufferImage(AbstractImage):
    """An abstract framebuffer.
    """
    gl_buffer = ...
    gl_format = ...
    format = ...
    owner = ...
    def __init__(self, x, y, width, height) -> None:
        ...
    
    def get_image_data(self): # -> ImageData:
        ...
    
    def get_region(self, x, y, width, height): # -> Self:
        ...
    


class ColorBufferImage(BufferImage):
    """A color framebuffer.

    This class is used to wrap the primary color buffer (i.e., the back
    buffer)
    """
    gl_format = ...
    format = ...
    def get_texture(self, rectangle=...): # -> Texture:
        ...
    
    def blit_to_texture(self, target, level, x, y, z): # -> None:
        ...
    


class DepthBufferImage(BufferImage):
    """The depth buffer.
    """
    gl_format = ...
    format = ...
    def get_texture(self, rectangle=...): # -> Texture:
        ...
    
    def blit_to_texture(self, target, level, x, y, z): # -> None:
        ...
    


class BufferImageMask(BufferImage):
    """A single bit of the stencil buffer.
    """
    gl_format = ...
    format = ...


