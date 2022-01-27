import importlib.resources as pkg_resources
import math

import arcade

import charmtests.data.audio
import charmtests.data.images
from charmtests.lib.anim import ease_linear
from charmtests.lib.charm import CharmColors
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

        # Play music
        with pkg_resources.path(charmtests.data.audio, "petscop.mp3") as p:
            song = arcade.load_sound(p)
            self.song = arcade.play_sound(song, self.volume, looping = True)

    def on_key_press(self, symbol: int, modifiers: int):
        match symbol:
            case arcade.key.BACKSPACE:
                self.window.show_view(self.back)
        return super().on_key_press(symbol, modifiers)

    def on_update(self, delta_time):
        super().on_update(delta_time)

        # Move background logos forwards and backwards, looping
        self.small_logos_forward.move((self.logo_width * delta_time / 4), 0)
        if self.small_logos_forward[0].left - self.small_logos_forward[0].original_left >= self.logo_width:
            self.small_logos_forward.move(-(self.small_logos_forward[0].left - self.small_logos_forward[0].original_left), 0)
        self.small_logos_backward.move(-(self.logo_width * delta_time / 4), 0)
        if self.small_logos_backward[0].original_left - self.small_logos_backward[0].left >= self.logo_width:
            self.small_logos_backward.move(self.small_logos_backward[0].original_left - self.small_logos_backward[0].left, 0)

    def on_draw(self):
        arcade.start_render()
        self.camera.use()

        # Charm BG
        self.small_logos_forward.draw()
        self.small_logos_backward.draw()

        self.title_label.draw()
        self.artistalbum_label.draw()

        super().on_draw()
