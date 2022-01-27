import arcade
import charmtests

import charmtests.data.images
from charmtests.lib.settings import Settings
from charmtests.lib.utils import pyglet_img_from_resource

from .views.title import TitleView

SCREEN_WIDTH = Settings.width
SCREEN_HEIGHT = Settings.height
SCREEN_TITLE = "Charm"


class CharmGame(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, update_rate=1/240)
        icon = pyglet_img_from_resource(charmtests.data.images, "charm-icon32t.png")
        self.set_icon(icon)

        self.delta_time = 0.0
        self.time = 0.0

        arcade.draw_text("abc", 0, 0)  # force font init

        self.debug_camera = arcade.Camera(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.fps_label = arcade.pyglet.text.Label("",
                          font_name='bananaslip plus plus',
                          font_size=12,
                          x=0, y=self.height,
                          anchor_x='left', anchor_y='top',
                          color = (0, 0, 0) + (0xFF,))
        self.fps_shadow_label = arcade.pyglet.text.Label("",
                          font_name='bananaslip plus plus',
                          font_size=12,
                          x=2, y=self.height - 2,
                          anchor_x='left', anchor_y='top',
                          color = (0xAA, 0xAA, 0xAA) + (0xFF,))

        self.title_view = TitleView()

    def setup(self):
        self.title_view.setup()
        self.show_view(self.title_view)

    def update(self, delta_time: float):
        self.delta_time = delta_time
        self.time += delta_time

    def fps_draw(self):
        self.debug_camera.use()
        self.fps_label.text = self.fps_shadow_label.text = f"{1/self.delta_time:.1f} FPS"
        with self.ctx.pyglet_rendering():
            self.fps_shadow_label.draw()
            self.fps_label.draw()


def main():
    window = CharmGame()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
