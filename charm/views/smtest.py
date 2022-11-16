import logging

import arcade

from charm.lib.charm import CharmColors, generate_gum_wrapper, move_gum_wrapper
from charm.lib.digiview import DigiView
from charm.lib.gamemodes.four_key import FourKeySong, FourKeyHighway
from charm.lib.paths import songspath

logger = logging.getLogger("charm")


class SMTestView(DigiView):
    def __init__(self, *args, **kwargs):
        super().__init__(fade_in=1, bg_color=CharmColors.FADED_GREEN, *args, **kwargs)
        self.song = None
        self.highway = None
        self.volume = 0.25

    def setup(self):
        super().setup()

        self._song = arcade.load_sound(songspath / "sm" / "discord" / "discord.mp3")
        self.sm_song = FourKeySong.parse(songspath / "sm" / "discord")
        self.chart = self.sm_song.get_chart("Challenge")
        self.highway = FourKeyHighway(self.chart, (0, 0), auto=True)
        self.highway.x += self.window.width // 2 - self.highway.w // 2

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
            case arcade.key.SPACE:
                self.song.pause() if self.song.playing else self.song.play()
            case arcade.key.KEY_0:
                self.song.seek(0)
            case arcade.key.MINUS:
                self.song.seek(self.song.time - 5)
            case arcade.key.EQUAL:
                self.song.seek(self.song.time + 5)

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
