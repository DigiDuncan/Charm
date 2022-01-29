import math
from arcade import SpriteList
import arcade

import charmtests.data.images
from charmtests.lib.utils import img_from_resource


class CharmColors:
    GREEN = (0x55, 0xD7, 0x90)
    FADED_GREEN = (0xB5, 0xED, 0xCE)
    PURPLE = (0x83, 0x94, 0xD8)


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
            s.alpha = alpha
            if i % 2:
                small_logos_backward.append(s)
            else:
                small_logos_forward.append(s)
    return (logo_width, small_logos_forward, small_logos_backward)

def move_gum_wrapper(logo_width: int, small_logos_forward: SpriteList, small_logos_backward: SpriteList, delta_time: float, speed = 4) -> None:
    """Move background logos forwards and backwards, looping."""
    small_logos_forward.move((logo_width * delta_time / speed), 0)
    if small_logos_forward[0].left - small_logos_forward[0].original_left >= logo_width:
        small_logos_forward.move(-(small_logos_forward[0].left - small_logos_forward[0].original_left), 0)
    small_logos_backward.move(-(logo_width * delta_time / speed), 0)
    if small_logos_backward[0].original_left - small_logos_backward[0].left >= logo_width:
        small_logos_backward.move(small_logos_backward[0].original_left - small_logos_backward[0].left, 0)
