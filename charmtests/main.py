import arcade
import charmtests

import charmtests.data.images
from charmtests.lib.utils import pyglet_img_from_resource

from .views.title import TitleView

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
SCREEN_TITLE = "Charm"


class MyGame(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, update_rate=1/120)
        icon = pyglet_img_from_resource(charmtests.data.images, "charm-icon32t.png")
        self.set_icon(icon)

        self.time = 0

        self.title_view = TitleView()
        arcade.draw_text("abc", 0, 0)  # force font init

    def setup(self):
        self.title_view.setup()
        self.show_view(self.title_view)

    def update(self, delta_time: float):
        self.time += delta_time


def main():
    window = MyGame()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
