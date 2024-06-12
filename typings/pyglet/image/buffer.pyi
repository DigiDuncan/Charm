"""
This type stub file was generated by pyright.
"""

from pyglet.gl import *

def get_max_color_attachments(): # -> int:
    """Get the maximum allow Framebuffer Color attachements"""
    ...

class Renderbuffer:
    """OpenGL Renderbuffer Object"""
    def __init__(self, width, height, internal_format, samples=...) -> None:
        ...
    
    @property
    def id(self): # -> int:
        ...
    
    @property
    def width(self): # -> Any:
        ...
    
    @property
    def height(self): # -> Any:
        ...
    
    def bind(self): # -> None:
        ...
    
    @staticmethod
    def unbind(): # -> None:
        ...
    
    def delete(self): # -> None:
        ...
    
    def __del__(self): # -> None:
        ...
    
    def __repr__(self): # -> str:
        ...
    


class Framebuffer:
    """OpenGL Framebuffer Object

    .. versionadded:: 2.0
    """
    def __init__(self, target=...) -> Framebuffer:
        ...
    
    @property
    def id(self): # -> int:
        """The Framebuffer id"""
        ...
    
    @property
    def width(self): # -> int:
        """The width of the widest attachment."""
        ...
    
    @property
    def height(self): # -> int:
        """The height of the tallest attachment."""
        ...
    
    def bind(self): # -> None:
        """Bind the Framebuffer

        This ctivates it as the current drawing target.
        """
        ...
    
    def unbind(self): # -> None:
        """Unbind the Framebuffer

        Unbind should be called to prevent further rendering
        to the framebuffer, or if you wish to access data
        from its Texture atachments.
        """
        ...
    
    def clear(self): # -> None:
        """Clear the attachments"""
        ...
    
    def delete(self): # -> None:
        """Explicitly delete the Framebuffer."""
        ...
    
    def __del__(self): # -> None:
        ...
    
    @property
    def is_complete(self) -> bool:
        """True if the framebuffer is 'complete', else False."""
        ...
    
    @staticmethod
    def get_status() -> str:
        """Get the current Framebuffer status, as a string.

        If `Framebuffer.is_complete` is `False`, this method
        can be used for more information. It will return a
        string with the OpenGL reported status.
        """
        ...
    
    def attach_texture(self, texture, target=..., attachment=...): # -> None:
        """Attach a Texture to the Framebuffer

        :Parameters:
            `texture` : pyglet.image.Texture
                Specifies the texture object to attach to the framebuffer attachment
                point named by attachment.
            `target` : int
                Specifies the framebuffer target. target must be GL_DRAW_FRAMEBUFFER,
                GL_READ_FRAMEBUFFER, or GL_FRAMEBUFFER. GL_FRAMEBUFFER is equivalent
                to GL_DRAW_FRAMEBUFFER.
            `attachment` : int
                Specifies the attachment point of the framebuffer. attachment must be
                GL_COLOR_ATTACHMENTi, GL_DEPTH_ATTACHMENT, GL_STENCIL_ATTACHMENT or
                GL_DEPTH_STENCIL_ATTACHMENT.
        """
        ...
    
    def attach_texture_layer(self, texture, layer, level, target=..., attachment=...): # -> None:
        """Attach a Texture layer to the Framebuffer

        :Parameters:
            `texture` : pyglet.image.TextureArray
                Specifies the texture object to attach to the framebuffer attachment
                point named by attachment.
            `layer` : int
                Specifies the layer of texture to attach.
            `level` : int
                Specifies the mipmap level of texture to attach.
            `target` : int
                Specifies the framebuffer target. target must be GL_DRAW_FRAMEBUFFER,
                GL_READ_FRAMEBUFFER, or GL_FRAMEBUFFER. GL_FRAMEBUFFER is equivalent
                to GL_DRAW_FRAMEBUFFER.
            `attachment` : int
                Specifies the attachment point of the framebuffer. attachment must be
                GL_COLOR_ATTACHMENTi, GL_DEPTH_ATTACHMENT, GL_STENCIL_ATTACHMENT or
                GL_DEPTH_STENCIL_ATTACHMENT.
        """
        ...
    
    def attach_renderbuffer(self, renderbuffer, target=..., attachment=...): # -> None:
        """Attach a Renderbuffer to the Framebuffer

        :Parameters:
            `renderbuffer` : pyglet.image.Renderbuffer
                Specifies the Renderbuffer to attach to the framebuffer attachment
                point named by attachment.
            `target` : int
                Specifies the framebuffer target. target must be GL_DRAW_FRAMEBUFFER,
                GL_READ_FRAMEBUFFER, or GL_FRAMEBUFFER. GL_FRAMEBUFFER is equivalent
                to GL_DRAW_FRAMEBUFFER.
            `attachment` : int
                Specifies the attachment point of the framebuffer. attachment must be
                GL_COLOR_ATTACHMENTi, GL_DEPTH_ATTACHMENT, GL_STENCIL_ATTACHMENT or
                GL_DEPTH_STENCIL_ATTACHMENT.
        """
        ...
    
    def __repr__(self): # -> str:
        ...
    

