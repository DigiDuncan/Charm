import importlib.resources as pkg_resources
import math
import PIL.Image
import arcade


def img_from_resource(package: pkg_resources.Package, resource: pkg_resources.Resource) -> PIL.Image.Image:
    with pkg_resources.open_binary(package, resource) as f:
        image = PIL.Image.open(f)
        image.load()
    return image

def pyglet_img_from_resource(package: pkg_resources.Package, resource: pkg_resources.Resource):
    with pkg_resources.open_binary(package, resource) as f:
        image = arcade.pyglet.image.load("icon.png", file = f)
    return image


def bounce(n: float, m: float, s: float, x: float) -> float:
    """Create a bouncing motion between max(0, n) and m with period 1/s at time x."""
    return max(abs(math.sin(x * math.pi * s)) * m, n)
