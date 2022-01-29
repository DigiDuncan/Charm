import importlib.resources as pkg_resources
import math
import random

import arcade

import charmtests.data.audio
import charmtests.data.images
from charmtests.lib.anim import bounce, ease_linear, ease_quadinout
from charmtests.lib.charm import CharmColors, generate_gum_wrapper, move_gum_wrapper
from charmtests.lib.digiview import DigiView
from charmtests.lib.utils import img_from_resource
from charmtests.views.menu import MainMenuView

FADE_DELAY = 1
SWITCH_DELAY = 0.5 + FADE_DELAY

class TitleView(DigiView):
    def __init__(self):
        super().__init__(bg_color=CharmColors.FADED_GREEN, show_fps=True)
        self.logo = None
        self.main_sprites = None
        self.song = None
        self.volume = 0.1
        self.hit_start: None
        self.sounds: dict[str, arcade.Sound] = {}
        self.main_menu_view = MainMenuView()

    def setup(self):
        self.hit_start = None

        arcade.set_background_color(CharmColors.FADED_GREEN)
        self.main_sprites = arcade.SpriteList()

        # Set up main logo
        logo_img = img_from_resource(charmtests.data.images, "logo.png")
        logo_texture = arcade.Texture("logo", logo_img)
        self.logo = arcade.Sprite(texture = logo_texture)
        self.logo.scale = 1 / 3
        self.logo.center_x = self.size[0] // 2
        self.logo.bottom = self.size[1] // 2

        self.main_sprites.append(self.logo)

        # Splash text
        self.splash_text = random.choice(pkg_resources.read_text(charmtests.data, "splashes.txt").splitlines())
        self.splash_label = arcade.pyglet.text.Label("",
                          font_name='bananaslip plus plus',
                          font_size=24,
                          x=self.window.width//2, y=self.window.height//2,
                          anchor_x='left', anchor_y='top',
                          color = CharmColors.PURPLE + (0xFF,))

        # Generate "gum wrapper" background
        self.logo_width, self.small_logos_forward, self.small_logos_backward = generate_gum_wrapper(self.size)

        # Play music
        with pkg_resources.path(charmtests.data.audio, "song.mp3") as p:
            song = arcade.load_sound(p)
            self.song = arcade.play_sound(song, self.volume, looping = True)
        self.song.seek(self.local_time + 3)

        # Song details
        self.song_label = arcade.pyglet.text.Label("Run Around The Character Code!\nCamellia feat. nanahira\n3LEEP!",
                          width=540,
                          font_name='bananaslip plus plus',
                          font_size=16,
                          x=5, y=5,
                          anchor_x='left', anchor_y='bottom',
                          multiline=True,
                          color = CharmColors.PURPLE + (0xFF,))
        self.song_label.original_x = self.song_label.x
        self.song_label.x = -self.song_label.width

        # Press start prompt
        self.press_label = arcade.pyglet.text.Label("<press start>",
                          font_name='bananaslip plus plus',
                          font_size=32,
                          x=self.window.width//2, y=self.window.height//4,
                          anchor_x='center', anchor_y='center',
                          color = CharmColors.PURPLE + (0xFF,))

        # Load sound
        with pkg_resources.path(charmtests.data.audio, "sfx-valid.wav") as p:
            self.sounds["valid"] = arcade.load_sound(p)

    def on_key_press(self, symbol: int, modifiers: int):
        match symbol:
            case arcade.key.ENTER:
                self.hit_start = self.local_time
                arcade.play_sound(self.sounds["valid"])
            case arcade.key.KEY_0:
                self.song.delete()
                self.setup()
            case arcade.key.KEY_7:
                self.window.debug = not self.window.debug
                if self.window.debug:
                    self.camera.scale = 2
                else:
                    self.camera.scale = 1

        return super().on_key_press(symbol, modifiers)

    def on_update(self, delta_time):
        self.local_time += delta_time

        move_gum_wrapper(self.logo_width, self.small_logos_forward, self.small_logos_backward, delta_time)
        
        # Logo bounce
        m = 0.325
        bpm = 220
        n = 0.3
        self.logo.scale = bounce(n, m, bpm, self.window.time)

        # Splash text typewriter effect
        self.splash_label.text = self.splash_text[:max(0, int((self.local_time - 3) * 20))]

        # Song name in and out
        if 3 <= self.local_time <= 5:  # constraining the time when we update the position should decrease lag,
                                       # even though it's technically unnecessary because the function is clamped
            self.song_label.x = ease_quadinout(-self.song_label.width, self.song_label.original_x, 3, 5, self.local_time)
        elif 8 <= self.local_time <= 10:
            self.song_label.x = ease_quadinout(self.song_label.original_x, -self.song_label.width, 8, 10, self.local_time)

        if self.hit_start is not None:
            # Fade music
            if self.local_time >= self.hit_start + FADE_DELAY:
                self.song.volume = ease_linear(self.volume, 0, self.hit_start + FADE_DELAY, self.hit_start + SWITCH_DELAY, self.local_time)
            # Go to main menu
            if self.local_time >= self.hit_start + SWITCH_DELAY:
                arcade.stop_sound(self.song)
                self.main_menu_view.setup()
                self.window.show_view(self.main_menu_view)

    def on_draw(self):
        arcade.start_render()
        self.camera.use()

        # Charm BG
        self.small_logos_forward.draw()
        self.small_logos_backward.draw()

        # Logo and text
        self.main_sprites.draw()
        with self.window.ctx.pyglet_rendering():
            self.splash_label.draw()
            self.song_label.draw()
            if self.hit_start is None:
                if int(self.local_time) % 2:
                    self.press_label.draw()
            else:
                if int(self.local_time * 4) % 2:
                    self.press_label.draw()

        super().on_draw()
