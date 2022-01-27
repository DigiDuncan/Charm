import importlib.resources as pkg_resources
import math

import arcade

import charmtests.data.audio
import charmtests.data.images
from charmtests.lib.anim import ease_linear
from charmtests.lib.charm import CharmColors
from charmtests.lib.digiview import DigiView
from charmtests.lib.utils import clamp, img_from_resource
from charmtests.objects.menu import Menu, MenuItem
from charmtests.objects.song import Song
from charmtests.views.song import SongView

FADE_DELAY = 0.5

class MainMenuView(DigiView):
    def __init__(self):
        super().__init__(fade_in=1, bg_color=CharmColors.FADED_GREEN, show_fps=True)
        self.main_sprites = None
        self.camera = arcade.Camera(1280, 720, self.window)
        self.song = None
        self.volume = 0.5
        self.sounds: dict[str, arcade.Sound] = {}

    def setup(self):
        super().setup()

        self.hit_start = None
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

        self.songs = [
            Song("It's A Song!", "DigiDuncan", "The Digi EP"),
            Song("Never Gonna Give You Up", "Rick Astley", "Rickrollin'"),
            Song("Caramelldansen", "Caramell", "Supergott"),
            Song("Run Around The Character Code!", "Camellia feat. nanhira", "3LEEP!"),
            Song("The Funny Dream Music", "Dream", "Cheating"),
            Song("Robot Rock", "Daft Punk", "I Forget, Sorry"),
            Song("Just Screaming", "AAAAAAAAAA", "AAAAAAAA"),
            Song("Twinkle, Twinkle, Patrick Star", "Patrick Star", "The Star Hits"),
            Song("Less Talk More Rokk", "Freezepop", "Rock Band 2"),
            Song("Thinking Of Songs Is Hard", "God Dang It", ":omegaAAA:"),
            Song("ERROR", "Garry", "My Mod")
        ]

        self.menu = Menu(self.songs)
        self.menu.sort("title")
        self.menu.selected_id = 0

        # Play music
        with pkg_resources.path(charmtests.data.audio, "petscop.mp3") as p:
            song = arcade.load_sound(p)
            self.song = arcade.play_sound(song, self.volume, looping = True)

        print("Loaded menu...")

    def on_update(self, delta_time):
        super().on_update(delta_time)

        # Move background logos forwards and backwards, looping
        self.small_logos_forward.move((self.logo_width * delta_time / 4), 0)
        if self.small_logos_forward[0].left - self.small_logos_forward[0].original_left >= self.logo_width:
            self.small_logos_forward.move(-(self.small_logos_forward[0].left - self.small_logos_forward[0].original_left), 0)
        self.small_logos_backward.move(-(self.logo_width * delta_time / 4), 0)
        if self.small_logos_backward[0].original_left - self.small_logos_backward[0].left >= self.logo_width:
            self.small_logos_backward.move(self.small_logos_backward[0].original_left - self.small_logos_backward[0].left, 0)

        self.test_label.rotation = math.sin(self.local_time * 4) * 6.25
        self.menu.update(self.local_time)

    def on_key_press(self, symbol: int, modifiers: int):
        match symbol:
            case arcade.key.UP:
                self.menu.selected_id -= 1
            case arcade.key.DOWN:
                self.menu.selected_id += 1
            case arcade.key.ENTER:
                songview = SongView(self.menu.items[self.menu.selected_id], back = self)
                songview.setup()
                self.window.show_view(songview)
        self.menu.selected_id = clamp(0, self.menu.selected_id, len(self.menu.items) - 1)
        self.menu.update_please = True

    def on_draw(self):
        arcade.start_render()
        self.camera.use()

        # Charm BG
        self.small_logos_forward.draw()
        self.small_logos_backward.draw()

        self.test_label.draw()
        self.menu.draw()

        self.window.fps_draw()
