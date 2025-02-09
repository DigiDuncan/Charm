from importlib.resources import files, as_file

import pyglet
import arcade

import charm.data.fonts
import charm.data.images
from charm.core.settings import settings
from charm.lib import charm_logger
from charm.lib.utils import pyglet_img_from_path
from charm.core.digiwindow import DigiWindow

# Fix font
pyglet.options["win32_disable_shaping"] = True


with as_file(files(charm.data.fonts) / "bananaslipplus.otf") as p:
    arcade.load_font(p)


class CharmGame(DigiWindow):
    def __init__(self):
        super().__init__(settings.window.size, "Charm", settings.window.ups, settings.window.fps)
        self.set_minimum_size(*settings.window.size)
        icon = pyglet_img_from_path(files(charm.data.images) / "charm-icon32t.png")
        self.set_icon(icon)
        arcade.hitbox.algo_default = arcade.hitbox.algo_bounding_box


def main() -> None:
    charm_logger.setup()
    window = CharmGame()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
