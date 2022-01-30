import importlib.resources as pkg_resources
import math

import arcade

import charmtests.data.audio
import charmtests.data.images
from charmtests.lib.anim import ease_linear
from charmtests.lib.charm import CharmColors, generate_gum_wrapper, move_gum_wrapper
from charmtests.lib.digiview import DigiView
from charmtests.lib.utils import clamp, img_from_resource
from charmtests.objects.menu import Menu, MenuItem
from charmtests.objects.song import Song
from charmtests.views.song import SongView

class MainMenuView(DigiView):
    def __init__(self, *args, **kwargs):
        super().__init__(fade_in=0.5, bg_color=CharmColors.FADED_GREEN, show_fps=True, *args, **kwargs)
        self.main_sprites = None
        self.song = None
        self.volume = 0.5
        self.sounds: dict[str, arcade.Sound] = {}
        self.album_art_buffer = 25
        self.static_time = 0.25

    def setup(self):
        super().setup()

        self.hit_start = None
        self.main_sprites = arcade.SpriteList()

        # Generate "gum wrapper" background
        self.logo_width, self.small_logos_forward, self.small_logos_backward = generate_gum_wrapper(self.size)

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
        self.selection_changed = 0

        self.album_art = arcade.Sprite(texture=self.menu.selected.album_art)
        self.album_art.right = self.size[0] - self.album_art_buffer
        self.album_art.original_bottom = self.album_art.bottom = self.size[1] // 2

        self.static = arcade.load_animated_gif(pkg_resources.path(charmtests.data.images, "static.gif"))
        self.static.right = self.size[0] - self.album_art_buffer
        self.static.original_bottom = self.album_art.bottom = self.size[1] // 2

        # Menu sounds
        for soundname in ["back", "select", "valid"]:
            with pkg_resources.path(charmtests.data.audio, f"sfx-{soundname}.wav") as p:
                self.sounds[soundname] = arcade.load_sound(p)

    def on_show(self):
        # Play music
        with pkg_resources.path(charmtests.data.audio, "petscop.mp3") as p:
            song = arcade.load_sound(p)
            self.song = arcade.play_sound(song, self.volume, looping = True)
        return super().on_show()

    def on_update(self, delta_time):
        super().on_update(delta_time)

        move_gum_wrapper(self.logo_width, self.small_logos_forward, self.small_logos_backward, delta_time)

        self.album_art.bottom = self.album_art.original_bottom + (math.sin(self.local_time * 2) * 25)
        self.static.bottom = self.album_art.original_bottom + (math.sin(self.local_time * 2) * 25)
        self.menu.update(self.local_time)
        self.static.on_update(delta_time)

    def on_key_press(self, symbol: int, modifiers: int):
        old_id = self.menu.selected_id
        match symbol:
            case arcade.key.UP:
                self.menu.selected_id -= 1
                arcade.play_sound(self.sounds["select"])
            case arcade.key.DOWN:
                self.menu.selected_id += 1
                arcade.play_sound(self.sounds["select"])
            case arcade.key.ENTER:
                arcade.play_sound(self.sounds["valid"])
                songview = SongView(self.menu.selected, back = self)
                songview.setup()
                arcade.stop_sound(self.song)
                self.window.show_view(songview)
            case arcade.key.BACKSPACE:
                arcade.play_sound(self.sounds["back"])
                self.back.setup()
                arcade.stop_sound(self.song)
                self.window.show_view(self.back)
            case arcade.key.KEY_7:
                self.window.debug = not self.window.debug
                if self.window.debug:
                    self.camera.scale = 2
                else:
                    self.camera.scale = 1
        self.menu.selected_id = clamp(0, self.menu.selected_id, len(self.menu.items) - 1)
        if old_id != self.menu.selected_id:
            self.selection_changed = self.local_time
            self.album_art.texture = self.menu.selected.album_art

    def on_draw(self):
        arcade.start_render()
        self.camera.use()

        # Charm BG
        self.small_logos_forward.draw()
        self.small_logos_backward.draw()

        arcade.draw_lrtb_rectangle_filled(self.album_art.left - self.album_art_buffer, self.size[0], self.size[1], 0, arcade.color.WHITE + (63,))

        self.menu.draw()
        if self.local_time < self.selection_changed + self.static_time:
            self.static.draw()
        else:
            self.album_art.draw()

        super().on_draw()
