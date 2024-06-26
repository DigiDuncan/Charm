"""
This type stub file was generated by pyright.
"""

"""Information about version and extensions of current GL implementation.

Usage::
    
    from pyglet.gl import gl_info

    if gl_info.have_extension('GL_NV_register_combiners'):
        # ...

If you are using more than one context, you can set up a separate GLInfo
object for each context.  Call `set_active_context` after switching to the
context::

    from pyglet.gl.gl_info import GLInfo

    info = GLInfo()
    info.set_active_context()

    if info.have_version(4, 5):
        # ...

"""
class GLInfo:
    """Information interface for a single GL context.

    A default instance is created automatically when the first OpenGL context
    is created.  You can use the module functions as a convenience for
    this default instance's methods.

    If you are using more than one context, you must call `set_active_context`
    when the context is active for this `GLInfo` instance.
    """
    _have_context = ...
    vendor = ...
    renderer = ...
    version = ...
    major_version = ...
    minor_version = ...
    opengl_api = ...
    extensions = ...
    _have_info = ...
    def set_active_context(self): # -> None:
        """Store information for the currently active context.

        This method is called automatically for the default context.
        """
        ...
    
    def remove_active_context(self): # -> None:
        ...
    
    def have_context(self): # -> bool:
        ...
    
    def have_extension(self, extension): # -> bool:
        """Determine if an OpenGL extension is available.

        :Parameters:
            `extension` : str
                The name of the extension to test for, including its
                ``GL_`` prefix.

        :return: True if the extension is provided by the driver.
        :rtype: bool
        """
        ...
    
    def get_extensions(self): # -> set[Any] | Generator[str, None, None] | set[str]:
        """Get a list of available OpenGL extensions.

        :return: a list of the available extensions.
        :rtype: list of str
        """
        ...
    
    def get_version(self): # -> tuple[int, int]:
        """Get the current OpenGL version.

        :return: The major and minor version as a tuple
        :rtype: tuple
        """
        ...
    
    def get_version_string(self): # -> str:
        """Get the current OpenGL version string.

        :return: The OpenGL version string
        :rtype: str
        """
        ...
    
    def have_version(self, major, minor=...): # -> bool:
        """Determine if a version of OpenGL is supported.

        :Parameters:
            `major` : int
                The major revision number (typically 1 or 2).
            `minor` : int
                The minor revision number.

        :rtype: bool
        :return: True if the requested or a later version is supported.
        """
        ...
    
    def get_renderer(self): # -> str:
        """Determine the renderer string of the OpenGL context.

        :rtype: str
        """
        ...
    
    def get_vendor(self): # -> str:
        """Determine the vendor string of the OpenGL context.

        :rtype: str
        """
        ...
    
    def get_opengl_api(self): # -> str:
        """Determine the OpenGL API version.
        Usually ``gl`` or ``gles``.

        :rtype: str
        """
        ...
    


_gl_info = ...
get_extensions = ...
get_version = ...
get_version_string = ...
have_version = ...
get_renderer = ...
get_vendor = ...
get_opengl_api = ...
have_extension = ...
have_context = ...
remove_active_context = ...
set_active_context = ...
