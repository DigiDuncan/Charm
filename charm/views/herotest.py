import logging
import random

import arcade

from charm.lib.charm import CharmColors, generate_gum_wrapper, move_gum_wrapper
from charm.lib.digiview import DigiView
from charm.lib.gamemodes.hero import HeroHighway, HeroSong, SectionEvent
from charm.lib.paths import songspath

logger = logging.getLogger("charm")


class HeroTestView(DigiView):
    def __init__(self, *args, **kwargs):
        super().__init__(fade_in=1, bg_color=CharmColors.FADED_GREEN, *args, **kwargs)
        self.song = None
        self.highway = None
        self.volume = 0.25

    def setup(self):
        super().setup()

        self._song = arcade.load_sound(songspath / "ch" / "run_around_the_character_code" / "song.mp3")
        self.hero_song = HeroSong.parse(songspath / "ch" / "run_around_the_character_code")
        self.chart = self.hero_song.get_chart("Expert", "Single")
        self.highway = HeroHighway(self.chart, (0, 0))
        self.highway.x += self.window.width // 2 - self.highway.w // 2

        self.section_text = arcade.Text("", self.window.width - 5, 5, arcade.color.BLACK, 16, align = "right", anchor_x = "right", font_name = "bananaslip plus plus", width=self.window.width)

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
            case arcade.key.F:
                self.highway.show_flags = not self.highway.show_flags

        return super().on_key_press(symbol, modifiers)

    def on_update(self, delta_time):
        super().on_update(delta_time)

        self.highway.update(self.song.time)

        # Section name
        # This should in theory be kinda fast because it's using Indexes?
        current_section: SectionEvent = self.hero_song.indexes_by_time["section"].lteq(self.song.time)
        if current_section and self.section_text.text != current_section.name:
            logger.debug(f"Section name is now {current_section.name} ({self.song.time})")
            self.section_text.text = current_section.name

        move_gum_wrapper(self.logo_width, self.small_logos_forward, self.small_logos_backward, delta_time)

    def on_draw(self):
        self.clear()
        self.camera.use()

        # Charm BG
        self.small_logos_forward.draw()
        self.small_logos_backward.draw()

        arcade.draw_lrtb_rectangle_filled(self.highway.x, self.highway.x + self.highway.w,
                                          self.highway.y + self.highway.h, self.highway.y,
                                          (0, 0, 0, 128))
        self.highway.draw()
        self.section_text.draw()

        super().on_draw()
