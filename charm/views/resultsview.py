import importlib.resources as pkg_resources
import logging

import arcade

from charm.lib.charm import CharmColors, generate_gum_wrapper, move_gum_wrapper
from charm.lib.digiview import DigiView
from charm.lib.generic.results import Results

import charm.data.audio
import charm.data.images.skins

logger = logging.getLogger("charm")


class ResultsView(DigiView):
    def __init__(self, results: Results, *args, **kwargs):
        super().__init__(fade_in=1, bg_color=CharmColors.FADED_GREEN, *args, **kwargs)
        self.song = None
        self.volume = 1
        self.results = results

    def setup(self):
        super().setup()

        with pkg_resources.path(charm.data.audio, "music-results.mp3") as p:
            self._song = arcade.load_sound(p)

        with pkg_resources.path(charm.data.images.skins.base, f"grade-{self.results.grade}.png") as p:
            self.grade_sprite = arcade.Sprite(p)
        self.grade_sprite.bottom = 10
        self.grade_sprite.left = 10

        self.score_text = arcade.Text(f"{self.results.score}",
            self.window.width - 5, self.window.height,
            arcade.color.BLACK, 72, self.window.width,
            "right", "bananaslip plus plus",
            anchor_x = "right", anchor_y = "top", multiline = True)
        self.data_text = arcade.Text(f"{self.results.fc_type}\nAccuracy: {self.results.accuracy * 100:.2f}%",
            self.window.width - 5, self.score_text.bottom,
            arcade.color.BLACK, 24, self.window.width,
            "right", "bananaslip plus plus",
            anchor_x = "right", anchor_y = "top", multiline = True)

        # Generate "gum wrapper" background
        self.logo_width, self.small_logos_forward, self.small_logos_backward = generate_gum_wrapper(self.size)
        self.success = True

    def on_show_view(self):
        self.window.theme_song.volume = 0
        self.song = arcade.play_sound(self._song, self.volume, looping=False)

    def on_key_press(self, symbol: int, modifiers: int):
        match symbol:
            case arcade.key.BACKSPACE:
                self.song.volume = 0
                self.back.setup()
                self.window.show_view(self.back)
                arcade.play_sound(self.window.sounds["back"])

        return super().on_key_press(symbol, modifiers)

    def on_update(self, delta_time):
        super().on_update(delta_time)

        move_gum_wrapper(self.logo_width, self.small_logos_forward, self.small_logos_backward, delta_time)

    def on_draw(self):
        self.clear()
        self.camera.use()

        # Charm BG
        self.small_logos_forward.draw()
        self.small_logos_backward.draw()

        self.grade_sprite.draw()
        self.score_text.draw()
        self.data_text.draw()

        super().on_draw()
