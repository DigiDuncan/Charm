import importlib.resources as pkg_resources
import math

import arcade

import charmtests.data.audio
import charmtests.data.images
from charmtests.lib.anim import ease_quartout
from charmtests.lib.charm import CharmColors, generate_gum_wrapper, move_gum_wrapper
from charmtests.lib.digiview import DigiView
from charmtests.lib.settings import Settings
from charmtests.lib.utils import clamp
from charmtests.objects.songmenu import SongMenu
from charmtests.objects.song import Song
from charmtests.views.song import SongView

class SongMenuView(DigiView):
    def __init__(self, *args, **kwargs):
        super().__init__(fade_in=0.5, bg_color=CharmColors.FADED_GREEN, *args, **kwargs)

        self.album_art_buffer = Settings.width // 20
        self.static_time = 0.25

    def setup(self):
        super().setup()

        self.hit_start = None

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

        self.menu = SongMenu(self.songs)
        self.menu.sort("title")
        self.menu.selected_id = 0
        self.selection_changed = 0

        self.album_art = arcade.Sprite(texture=self.menu.selected.album_art)
        self.album_art.right = self.size[0] - self.album_art_buffer
        self.album_art.original_bottom = self.album_art.bottom = self.size[1] // 2

        self.static = arcade.load_animated_gif(pkg_resources.path(charmtests.data.images, "static.gif"))
        self.static.right = self.size[0] - self.album_art_buffer
        self.static.original_bottom = self.album_art.bottom = self.size[1] // 2


    def on_show(self):
        return super().on_show()

    def on_update(self, delta_time):
        super().on_update(delta_time)

        move_gum_wrapper(self.logo_width, self.small_logos_forward, self.small_logos_backward, delta_time)

        self.album_art.bottom = self.album_art.original_bottom + (math.sin(self.local_time * 2) * 25)
        self.static.bottom = self.album_art.original_bottom + (math.sin(self.local_time * 2) * 25)
        self.menu.update(self.local_time)
        self.static.update_animation(delta_time)

    def on_key_press(self, symbol: int, modifiers: int):
        old_id = self.menu.selected_id
        match symbol:
            case arcade.key.UP:
                self.menu.selected_id -= 1
                arcade.play_sound(self.window.sounds["select"])
            case arcade.key.DOWN:
                self.menu.selected_id += 1
                arcade.play_sound(self.window.sounds["select"])
            case arcade.key.ENTER:
                arcade.play_sound(self.window.sounds["valid"])
                songview = SongView(self.menu.selected, back = self)
                songview.setup()
                self.window.show_view(songview)
            case arcade.key.BACKSPACE:
                arcade.play_sound(self.window.sounds["back"])
                self.back.setup()
                self.window.show_view(self.back)
        if old_id != self.menu.selected_id:
            self.selection_changed = self.local_time
            self.album_art.texture = self.menu.selected.album_art

        return super().on_key_press(symbol, modifiers)

    def on_draw(self):
        self.clear()
        self.camera.use()

        # Charm BG
        self.small_logos_forward.draw()
        self.small_logos_backward.draw()

        bottom = ease_quartout(self.size[1], 0, 0.5, 1.5, self.local_time)
        arcade.draw_lrtb_rectangle_filled(self.album_art.left - self.album_art_buffer, self.size[0], self.size[1], bottom, arcade.color.WHITE + (127,))

        self.menu.draw()
        if self.local_time < self.selection_changed + self.static_time:
            self.static.draw()
        else:
            self.album_art.draw()

        super().on_draw()
