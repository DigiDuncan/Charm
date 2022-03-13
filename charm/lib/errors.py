from arcade import Sprite
import arcade
import arcade.color
import PIL, PIL.Image, PIL.ImageDraw  # noqa: E401

import charm.data.images.errors
from charm.lib.utils import img_from_resource
from charm.lib.settings import Settings


class CharmException(Exception):
    def __init__(self, title: str, show_message: str, icon: str = "error", *args: object):
        self.title = title
        self.show_message = show_message
        self._icon = icon
        self.icon = img_from_resource(charm.data.images.errors, f"{icon}.png")
        self.icon.resize((32, 32), PIL.Image.LANCZOS)
        self.sprite = self.get_sprite()
        self.sprite.set_position(Settings.width / 2, Settings.height / 2)
        super().__init__(*args)

    def get_sprite(self) -> Sprite:
        _tex = arcade.Texture.create_empty(f"_error-{self.title}-{self.show_message}", (500, 200))
        _icon_tex = arcade.Texture(f"_error_icon_{self._icon}", self.icon)
        sprite = Sprite(texture=_tex)
        _sprite_list = arcade.SpriteList()
        _sprite_list.append(sprite)

        with _sprite_list.atlas.render_into(_tex) as fbo:
            fbo.clear()
            arcade.draw_lrtb_rectangle_filled(0, 500, 200, 0, arcade.color.BLANCHED_ALMOND)
            arcade.draw_lrtb_rectangle_filled(0, 500, 200, 150, arcade.color.BRANDEIS_BLUE)
            arcade.draw_text(self.title, 50, 154, font_size=24, bold=True, anchor_y="bottom")
            arcade.draw_text(self.show_message, 5, 146, font_size=16, anchor_y="top", multiline=True, width=192, color=arcade.color.BLACK)
            arcade.draw_texture_rectangle(25, 175, 32, 32, _icon_tex)

        return sprite


class GenericError(CharmException):
    def __init__(self, error: Exception, *args: object):
        super().__init__(error.__class__.__name__, str(error), "error", *args)


class TestError(CharmException):
    def __init__(self, show_message: str, *args: object):
        super().__init__("Test", show_message, "error", *args)


class NoChartsError(CharmException):
    def __init__(self, song_name: str, *args: object):
        super().__init__("No charts found!", f"No charts found for song '{song_name}'", "error", *args)
