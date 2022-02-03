from functools import cache
import math

import arcade
from arcade import SpriteList
import PIL.Image, PIL.ImageDraw

import charmtests.data.images
from charmtests.lib.utils import img_from_resource


class CharmColors:
    GREEN = (0x95, 0xdf, 0xaa)
    PINK = (0xe6, 0x8e, 0xbe)
    PURPLE = (0x9c, 0x84, 0xd9)
    FADED_GREEN = (0xaa, 0xf2, 0xca)
    FADED_PINK = (0xe8, 0xb3, 0xe7)
    FADED_PURPLE = (0xda, 0xcc, 0xff)

@cache
def generate_missing_texture_image(w, h) -> PIL.Image.Image:
    """Generate a classic missing texture of wxh."""
    mt = PIL.Image.new("RGB", (w, h), arcade.color.MAGENTA)
    d = PIL.ImageDraw.Draw(mt)
    d.rectangle((0, h // 2, w // 2, h), arcade.color.BLACK)
    d.rectangle((w // 2, 0, w, h // 2), arcade.color.BLACK)
    return mt

def generate_gum_wrapper(size: tuple[int], buffer: int = 20, alpha = 128) -> tuple[int, SpriteList, SpriteList]:
    """Generate two SpriteLists that makes a gum wrapper-style background."""
    small_logos_forward = arcade.SpriteList()
    small_logos_backward = arcade.SpriteList()
    small_logo_img = img_from_resource(charmtests.data.images, "small-logo.png")
    small_logo_texture = arcade.Texture("small_logo", small_logo_img)
    sprites_horiz = math.ceil(size[0] / small_logo_texture.width)
    sprites_vert = math.ceil(size[1] / small_logo_texture.height / 1.5)
    logo_width = small_logo_texture.width + buffer
    for i in range(sprites_vert):
        for j in range(sprites_horiz):
            s = arcade.Sprite(texture = small_logo_texture)
            s.original_bottom = s.bottom = small_logo_texture.height * i * 1.5
            s.original_left = s.left = logo_width * (j - 2)
            if i % 2:
                small_logos_backward.append(s)
            else:
                small_logos_forward.append(s)
    small_logos_forward.alpha = alpha
    small_logos_backward.alpha = alpha
    return (logo_width, small_logos_forward, small_logos_backward)

def move_gum_wrapper(logo_width: int, small_logos_forward: SpriteList, small_logos_backward: SpriteList, delta_time: float, speed = 4) -> None:
    """Move background logos forwards and backwards, looping."""
    small_logos_forward.move((logo_width * delta_time / speed), 0)
    if small_logos_forward[0].left - small_logos_forward[0].original_left >= logo_width:
        small_logos_forward.move(-(small_logos_forward[0].left - small_logos_forward[0].original_left), 0)
    small_logos_backward.move(-(logo_width * delta_time / speed), 0)
    if small_logos_backward[0].original_left - small_logos_backward[0].left >= logo_width:
        small_logos_backward.move(small_logos_backward[0].original_left - small_logos_backward[0].left, 0)
