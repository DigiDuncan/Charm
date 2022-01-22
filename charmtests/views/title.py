import math
import random
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
        self.camera = arcade.Camera(1280, 720, self.window)

    def setup(self):
        self.local_time = 0

        arcade.set_background_color(CharmColors.FADED_GREEN)
        self.main_sprites = arcade.SpriteList()
        logo_img = img_from_resource(charmtests.data.images, "logo.png")
        logo_texture = arcade.Texture("logo", logo_img)
        self.logo = arcade.Sprite(texture = logo_texture)
        self.logo.scale = 1 / 3
        self.logo.center_x = self.size[0] // 2
        self.logo.bottom = self.size[1] // 2

        self.main_sprites.append(self.logo)

        self.splash_text = "it has splash text!"
        self.splash_label = arcade.pyglet.text.Label("",
                          font_name='bananaslip plus plus',
                          font_size=24,
                          x=self.window.width//2, y=self.window.height//2,
                          anchor_x='left', anchor_y='top',
                          color = CharmColors.PURPLE + (0xFF,))

        self.small_logos_forward = arcade.SpriteList()
        self.small_logos_backward = arcade.SpriteList()
        small_logo_img = img_from_resource(charmtests.data.images, "small-logo.png")
        small_logo_texture = arcade.Texture("small_logo", small_logo_img)
        sprites_horiz = math.ceil(self.size[0] / small_logo_texture.width) + 2
        sprites_vert = math.ceil(self.size[1] / small_logo_texture.height)
        self.logo_width = small_logo_texture.width + 20
        for i in range(sprites_vert):
            for j in range(sprites_horiz):
                s = arcade.Sprite(texture = small_logo_texture)
                s.original_bottom = s.bottom = small_logo_texture.height * i * 1.5
                s.original_left = s.left = self.logo_width * (j - 1)
                if i % 2:
                    self.small_logos_backward.append(s)
                else:
                    self.small_logos_forward.append(s)

    def on_show(self):
        pass

    def on_update(self, delta_time):
        self.local_time += delta_time

        for s in self.small_logos_forward:
            s.left = s.original_left + ((self.local_time * self.logo_width / 4) % self.logo_width)
        for s in self.small_logos_backward:
            s.left = s.original_left - ((self.local_time * self.logo_width / 4) % self.logo_width)


        m = 0.325
        s = 3
        n = 0.3
        self.logo.scale = bounce(n, m, s, self.window.time)
        self.splash_label.text = self.splash_text[:max(0, int((self.local_time - 3) * 10))]


    def on_draw(self):
        arcade.start_render()
        self.camera.use()

        # Charm BG
        self.small_logos_forward.draw()
        self.small_logos_backward.draw()

        # Logo and splash
        self.main_sprites.draw()
        with self.window.ctx.pyglet_rendering():
            self.splash_label.draw()

        self.window.fps_draw()
