from functools import cache
import importlib.resources as pkg_resources
from typing import Any
import PIL.Image
import arcade

def int_or_str(i: Any) -> int | str | None:
    try:
        o = int(i)
    except ValueError:
        try:
            o = str(i)  # Does this ever actually raise ValueError?
        except ValueError:
            o = None
    return o


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

def scale_float(nn: float, nm: float, x: float, on: float = -1.0, om: float = 1.0) -> float:
    """Scale a float `x` that is currently somewhere between `on` and `om` to now be in an
    equivalent position between `nn` and `nm`."""
    # Make the range start at 0.
    old_max = om - on  # 16k
    old_x = x - on  # x + 8k
    percentage = old_x / old_max  # 0 - 1

    new_max = nm - nn  # 2
    new_pos = new_max * percentage
    ans = new_pos + nn
    return ans