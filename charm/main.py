import importlib.resources as pkg_resources
import logging

import arcade
import pyglet
from digiformatter import logger as digilogger

import charm
import charm.data.fonts
import charm.data.images
from charm.lib.settings import Settings
from charm.lib.utils import pyglet_img_from_resource
from charm.lib.digiwindow import DigiWindow
from charm.objects.debug_log import PygletHandler

from .views.title import TitleView

SCREEN_WIDTH = Settings.width
SCREEN_HEIGHT = Settings.height
FPS_CAP = Settings.fps
SCREEN_TITLE = "Charm"

# Set up logging
logging.basicConfig(level=logging.INFO)
dfhandler = digilogger.DigiFormatterHandler()
dfhandlersource = digilogger.DigiFormatterHandler(showsource=True)
phandler = PygletHandler()
phandlersource = PygletHandler(showsource=True)

logger = logging.getLogger("charm")
logger.setLevel(logging.DEBUG)
logger.handlers = []
logger.propagate = False
logger.addHandler(dfhandler)
logger.addHandler(phandler)

arcadelogger = logging.getLogger("arcade")
arcadelogger.setLevel(logging.WARN)
arcadelogger.handlers = []
arcadelogger.propagate = False
arcadelogger.addHandler(dfhandlersource)
arcadelogger.addHandler(phandlersource)

# Fix font lag
pyglet.options["advanced_font_features"] = True
arcade.pyglet.options["advanced_font_features"] = True

with pkg_resources.path(charm.data.fonts, "bananaslipplus.otf") as p:
    arcade.text_pyglet.load_font(str(p))


class CharmGame(DigiWindow):
    def __init__(self):
        super().__init__((SCREEN_WIDTH, SCREEN_HEIGHT), SCREEN_TITLE, FPS_CAP, None)

        icon = pyglet_img_from_resource(charm.data.images, "charm-icon32t.png")
        self.set_icon(icon)

        # Menu sounds
        for soundname in ["back", "select", "valid"]:
            with pkg_resources.path(charm.data.audio, f"sfx-{soundname}.wav") as p:
                self.sounds[soundname] = arcade.load_sound(p)
        for soundname in ["error", "warning", "info"]:
            with pkg_resources.path(charm.data.audio, f"error-{soundname}.wav") as p:
                self.sounds["error-" + soundname] = arcade.load_sound(p)

        self.initial_view = TitleView()


def main():
    window = CharmGame()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
