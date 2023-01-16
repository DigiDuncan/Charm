import arcade
import arcade.color
import PIL, PIL.Image, PIL.ImageDraw  # noqa: E401
from arcade import Sprite

import charm.data.images.errors
from charm.lib.utils import img_from_resource
from charm.lib.settings import Settings


class CharmException(Exception):
    def __init__(self, title: str, show_message: str, icon: str = "error", *args: object):
        self.title = title
        self.show_message = show_message
        self._icon = icon
        super().__init__(show_message, *args)
        try:
            arcade.get_window()
        except RuntimeError:
            # If we aren't in an arcade Window (e.g., unit esting) we don't need the sprite stuff.
            return
        self.icon = img_from_resource(charm.data.images.errors, f"{icon}.png")
        self.icon.resize((32, 32), PIL.Image.LANCZOS)
        self.sprite = self.get_sprite()
        self.sprite.set_position(Settings.width / 2, Settings.height / 2)

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
            arcade.draw_text(self.title, 50, 165, font_size=24, bold=True)
            arcade.draw_text(self.show_message, 5, 146, font_size=16, anchor_y="top", multiline=True, width=492, color=arcade.color.BLACK)
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


class ChartParseError(CharmException):
    def __init__(self, line_num: int, show_message: str, *args: object):
        super().__init__("Chart parsing error!", f"[Line {line_num}] " + show_message, "error", *args)


class ChartPostReadParseError(CharmException):
    def __init__(self, show_message: str, *args: object):
        super().__init__("Chart post-read parse error!", show_message, "error", *args)


class UnknownLanesError(CharmException):
    def __init__(self, show_message: str, *args: object):
        super().__init__("Unknown lanes found", show_message, "warning", *args)


class AssetNotFoundError(CharmException):
    def __init__(self, asset_name: str, *args: object):
        super().__init__("Asset missing!", f"No asset named '{asset_name}' exists!", "error", *args)


class MultipleKeyBindsError(CharmException):
    def __init__(self, action: str, *args: object):
        super().__init__("Multiple key binds set!", f"Action '{action}' has multiple key binds!", "error", *args)


class ExclusiveKeyBindError(CharmException):
    def __init__(self, input: str, actions: list[str] = [], *args: object):
        super().__init__("Key bound to multiple actions!", f"Key '{input}' has multiple actions assigned! ({actions})", "error", *args)


class KeyUnboundError(CharmException):
    def __init__(self, action: str, *args: object):
        super().__init__("Action unbound!", f"Action '{action}' not bound to a key!", "error", *args)


class ActionNameConflictError(CharmException):
    def __init__(self, action: str, *args: object):
        super().__init__("Action conflict!", f"Action '{action}' created multiple times!", "error", *args)


class ActionNotFoundError(CharmException):
    def __init__(self, action: str, *args: object):
        super().__init__("Action not found!", f"Action '{action}' not found!", "error", *args)


class SameInputMultipleError(CharmException):
    def __init__(self, action: str, input: str, *args: object):
        super().__init__("Input bound multiple times!", f"Input '{input}' bound multiple times on '{action}'!", "error", *args)


class SetNotFoundError(CharmException):
    def __init__(self, set: str, *args: object):
        super().__init__("Set not found!", f"Action set '{set}' not found!", "error", *args)


class KeyNotFoundInActionError(CharmException):
    def __init__(self, action: str, key: str, *args: object):
        super().__init__("Key not in action!", f"Key '{key}' not found in action {action}!", "error", *args)


class KeyUnrecognizedError(CharmException):
    def __init__(self, key: str, *args: object):
        super().__init__("Key unrecognized!", f"Key '{key}' unrecognized!", "error", *args)


class ActionNotInSetError(CharmException):
    def __init__(self, action: str, *args: object):
        super().__init__("Action not in set!", f"Action {action} not in set!", "error", *args)
