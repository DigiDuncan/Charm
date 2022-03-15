from functools import cache
import importlib.resources as pkg_resources
import PIL.Image
import arcade


def clamp(minVal, val, maxVal):
    """Clamp a `val` to be no lower than `minVal`, and no higher than `maxVal`."""
    return max(minVal, min(maxVal, val))


@cache
def img_from_resource(package: pkg_resources.Package, resource: pkg_resources.Resource) -> PIL.Image.Image:
    with pkg_resources.open_binary(package, resource) as f:
        image = PIL.Image.open(f)
        image.load()
    return image


@cache
def pyglet_img_from_resource(package: pkg_resources.Package, resource: pkg_resources.Resource):
    with pkg_resources.open_binary(package, resource) as f:
        image = arcade.pyglet.image.load("icon.png", file=f)
    return image
