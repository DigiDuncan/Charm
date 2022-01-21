import math
import arcade

import charmtests.data.images
from charmtests.lib.charm import CharmColors
from charmtests.lib.utils import img_from_resource, bounce

class TitleView(arcade.View):
    def __init__(self):
        super().__init__()
        self.size = self.window.get_size()
        self.logo = None
        self.sprite_list = None
        self.local_time = 0

    def setup(self):
        self.local_time = 0

        arcade.set_background_color(CharmColors.FADED_GREEN)
        self.sprite_list = arcade.SpriteList()
        logo_img = img_from_resource(charmtests.data.images, "logo.png")
        logo_texture = arcade.Texture("logo", logo_img)
        self.logo = arcade.Sprite(texture = logo_texture)
        self.logo.scale = 1 / 3
        self.logo.center_x = self.size[0] // 2
        self.logo.bottom = self.size[1] // 2

        self.sprite_list.append(self.logo)

        self.splash_text = "it has splash text!"
        self.splash_label = arcade.pyglet.text.Label("",
                          font_name='bananaslip plus plus',
                          font_size=24,
                          x=self.window.width//2, y=self.window.height//2,
                          anchor_x='left', anchor_y='top',
                          color = CharmColors.PURPLE + (0xFF,))

    def on_show(self):
        pass

    def on_update(self, delta_time):
        self.local_time += delta_time
        m = 0.375
        s = 3
        n = 0.3
        self.logo.scale = bounce(n, m, s, self.window.time)
        self.splash_label.text = self.splash_text[:max(0, int((self.local_time - 3) * 10))]

    def on_draw(self):
        arcade.start_render()
        self.sprite_list.draw()
        with self.window.ctx.pyglet_rendering():
            self.splash_label.draw()
