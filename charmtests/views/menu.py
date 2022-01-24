import importlib.resources as pkg_resources
import math

import arcade

import charmtests.data.audio
import charmtests.data.images
from charmtests.lib.anim import ease_linear
from charmtests.lib.charm import CharmColors
from charmtests.lib.utils import img_from_resource

FADE_DELAY = 0.5

class MainMenuView(arcade.View):
    def __init__(self):
        super().__init__()
        self.size = self.window.get_size()
        self.main_sprites = None
        self.local_time = 0
        self.camera = arcade.Camera(1280, 720, self.window)
        self.song = None
        self.volume = 0.75
        self.sounds: dict[str, arcade.Sound] = {}

    def setup(self):
        self.local_time = 0
        self.hit_start = None

        arcade.set_background_color(CharmColors.FADED_GREEN)
        self.main_sprites = arcade.SpriteList()

        # Generate "gum wrapper" background
        self.small_logos_forward = arcade.SpriteList()
        self.small_logos_backward = arcade.SpriteList()
        small_logo_img = img_from_resource(charmtests.data.images, "small-logo.png")
        small_logo_texture = arcade.Texture("small_logo", small_logo_img)
        sprites_horiz = math.ceil(self.size[0] / small_logo_texture.width)
        sprites_vert = math.ceil(self.size[1] / small_logo_texture.height / 1.5)
        self.logo_width = small_logo_texture.width + 20
        for i in range(sprites_vert):
            for j in range(sprites_horiz):
                s = arcade.Sprite(texture = small_logo_texture)
                s.original_bottom = s.bottom = small_logo_texture.height * i * 1.5
                s.original_left = s.left = self.logo_width * (j - 2)
                s.alpha = 128
                if i % 2:
                    self.small_logos_backward.append(s)
                else:
                    self.small_logos_forward.append(s)

        self.test_label = arcade.Text("this is the main menu!",
                          font_name='bananaslip plus plus',
                          font_size=60,
                          start_x=self.window.width//2, start_y=self.window.height//2,
                          anchor_x='center', anchor_y='center',
                          color = CharmColors.PURPLE + (0xFF,))

        # Play music
        with pkg_resources.path(charmtests.data.audio, "petscop.mp3") as p:
            song = arcade.load_sound(p)
            self.song = arcade.play_sound(song, self.volume, looping = True)

        print("Loaded menu...")

    def on_update(self, delta_time):
        self.local_time += delta_time

        # Move background logos forwards and backwards, looping
        self.small_logos_forward.move((self.logo_width * delta_time / 4), 0)
        if self.small_logos_forward[0].left - self.small_logos_forward[0].original_left >= self.logo_width:
            self.small_logos_forward.move(-(self.small_logos_forward[0].left - self.small_logos_forward[0].original_left), 0)
        self.small_logos_backward.move(-(self.logo_width * delta_time / 4), 0)
        if self.small_logos_backward[0].original_left - self.small_logos_backward[0].left >= self.logo_width:
            self.small_logos_backward.move(self.small_logos_backward[0].original_left - self.small_logos_backward[0].left, 0)

        self.test_label.rotation = math.sin(self.local_time * 4) * 6.25

    def on_draw(self):
        arcade.start_render()
        self.camera.use()

        # Charm BG
        self.small_logos_forward.draw()
        self.small_logos_backward.draw()

        self.test_label.draw()

        if self.local_time <= FADE_DELAY:
            alpha = ease_linear(255, 0, 0, FADE_DELAY, self.local_time)
            arcade.draw_lrtb_rectangle_filled(0, 1280, 720, 0,
                (0, 0, 0, alpha)
            )
