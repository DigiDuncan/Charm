import math
import arcade

import charmtests.data.images
from charmtests.lib.charm import CharmColors
from charmtests.lib.utils import img_from_resource

class TitleView(arcade.View):
    def __init__(self):
        super().__init__()
        self.size = self.window.get_size()
        self.logo = None
        self.sprite_list = None
        self.time = 0

    def setup(self):
        arcade.set_background_color(CharmColors.FADED_GREEN)
        self.sprite_list = arcade.SpriteList()
        logo_img = img_from_resource(charmtests.data.images, "logo.png")
        logo_texture = arcade.Texture("logo", logo_img)
        self.logo = arcade.Sprite(texture = logo_texture)
        self.logo.scale = 1 / 3
        self.logo.center_x = self.size[0] // 2
        self.logo.bottom = self.size[1] // 2

        self.sprite_list.append(self.logo)

    def on_show(self):
        pass

    def on_update(self, delta_time):
        m = 0.4
        s = 2.5
        n = 0.3
        self.time += delta_time
        self.logo.scale = max(abs(math.sin(self.time * math.pi * s)) * m, n)

    def on_draw(self):
        arcade.start_render()
        self.sprite_list.draw()
