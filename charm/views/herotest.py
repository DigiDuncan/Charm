import importlib.resources as pkg_resources

import arcade

from charm.lib.charm import CharmColors, generate_gum_wrapper, move_gum_wrapper
from charm.lib.digiview import DigiView
from charm.lib.gamemodes.hero import HeroChart, HeroHighway, HeroSong
from charm.lib.paths import songspath
from charm.lib.settings import Settings

import charm.data.audio


class HeroTestView(DigiView):
    def __init__(self, *args, **kwargs):
        super().__init__(fade_in=1, bg_color=CharmColors.FADED_GREEN, *args, **kwargs)
        self.song = None
        self.highway = None
        self.volume = 1

    def setup(self):
        super().setup()

        self._song = arcade.load_sound(songspath / "ch" / "run_around_the_character_code" / "song.mp3")
        self.song = HeroSong.parse(songspath / "ch" / "run_around_the_character_code")
        self.chart = self.song.get_chart("Expert", "Single")
        self.highway = HeroHighway(self.chart, (0, 0), show_flags=True)

        # Generate "gum wrapper" background
        self.logo_width, self.small_logos_forward, self.small_logos_backward = generate_gum_wrapper(self.size)

    def on_show_view(self):
        self.window.theme_song.volume = 0
        self.song = arcade.play_sound(self._song, self.volume, looping=False)

    def on_key_press(self, symbol: int, modifiers: int):
        match symbol:
            case arcade.key.BACKSPACE:
                self.song.delete()
                self.back.setup()
                self.window.show_view(self.back)
                arcade.play_sound(self.window.sounds["back"])

        return super().on_key_press(symbol, modifiers)

    def on_update(self, delta_time):
        super().on_update(delta_time)

        self.highway.update(self.song.time)

        move_gum_wrapper(self.logo_width, self.small_logos_forward, self.small_logos_backward, delta_time)

    def on_draw(self):
        self.clear()
        self.camera.use()

        # Charm BG
        self.small_logos_forward.draw()
        self.small_logos_backward.draw()

        self.highway.draw()

        super().on_draw()
