import importlib.resources as pkg_resources
import math

import arcade

import charmtests.data.audio
import charmtests.data.images
from charmtests.lib.anim import ease_linear
from charmtests.lib.charm import CharmColors, generate_gum_wrapper, move_gum_wrapper
from charmtests.lib.digiview import DigiView
from charmtests.lib.utils import img_from_resource
from charmtests.objects.song import Song

FADE_DELAY = 0.5

class SongView(DigiView):
    def __init__(self, song: Song, *args, **kwargs):
        super().__init__(fade_in = 1,
        bg_color = CharmColors.FADED_GREEN,
        show_fps = True, *args, **kwargs)
        
        self.main_sprites = None
        self.camera = arcade.Camera(1280, 720, self.window)
        self.volume = 0.5
        self.songdata = song
        self.back_sound: arcade.Sound = None

    def setup(self):
        super().setup()

        # Generate "gum wrapper" background
        self.logo_width, self.small_logos_forward, self.small_logos_backward = generate_gum_wrapper(self.size)

        self.title_label = arcade.Text(self.songdata.title,
                          font_name='bananaslip plus plus',
                          font_size=60,
                          start_x=self.window.width//2, start_y=self.window.height//2,
                          anchor_x='center', anchor_y='bottom',
                          color = CharmColors.PURPLE + (0xFF,))

        self.artistalbum_label = arcade.Text(self.songdata.artist + " - " + self.songdata.album,
                          font_name='bananaslip plus plus',
                          font_size=40,
                          start_x=self.window.width//2, start_y=self.window.height//2,
                          anchor_x='center', anchor_y='top',
                          color = CharmColors.PURPLE + (0xFF,))

        #back sound
        with pkg_resources.path(charmtests.data.audio, "sfx-back.wav") as p:
            self.back_sound = arcade.load_sound(p)

        # Play music
        with pkg_resources.path(charmtests.data.audio, "petscop.mp3") as p:
            song = arcade.load_sound(p)
            self.song = arcade.play_sound(song, self.volume, looping = True)

    def on_key_press(self, symbol: int, modifiers: int):
        match symbol:
            case arcade.key.BACKSPACE:
                self.window.show_view(self.back)
                arcade.play_sound(self.back_sound)
        return super().on_key_press(symbol, modifiers)

    def on_update(self, delta_time):
        super().on_update(delta_time)

        move_gum_wrapper(self.logo_width, self.small_logos_forward, self.small_logos_backward, delta_time)

    def on_draw(self):
        arcade.start_render()
        self.camera.use()

        # Charm BG
        self.small_logos_forward.draw()
        self.small_logos_backward.draw()

        self.title_label.draw()
        self.artistalbum_label.draw()

        super().on_draw()
