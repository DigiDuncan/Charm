import logging

import arcade
from arcade import Text, color as colors
from pyglet.graphics import Batch

from charm.core.charm import GumWrapper
from charm.core.digiview import DigiView, disable_when_focus_lost, shows_errors
from charm.lib.gamemodes.hero import HeroEngine, HeroHighway, HeroSong, SectionEvent
from charm.core.keymap import keymap
from charm.lib.oggsound import OGGSound
from charm.core.paths import songspath
from charm.game.displayables.lyric_animator import LyricAnimator

logger = logging.getLogger("charm")


class HeroTestView(DigiView):
    def __init__(self, back: DigiView):
        super().__init__(fade_in=1, back=back)
        self.song = None
        self.highway = None
        self._song: OGGSound

    @shows_errors
    def setup(self) -> None:
        super().presetup()
        # name = "mcmental"
        name = "run_around_the_character_code"

        self._song = OGGSound(songspath / "ch" / name / "song.ogg")
        self.hero_song = HeroSong.parse(songspath / "ch" / name)
        self.chart = self.hero_song.get_chart("Expert", "Single")
        self.engine = HeroEngine(self.chart)
        self.highway = HeroHighway(self.chart, (0, 0))
        self.highway.x += self.window.center_x - self.highway.w // 2

        self.text_batch = Batch()

        metadata_string = f"{self.hero_song.metadata.title}\n{self.hero_song.metadata.artist}\n{self.hero_song.metadata.album}"
        self.metadata_text = Text(metadata_string, 5, 5, colors.BLACK, 16, align = "left", anchor_x = "left", anchor_y = "bottom", multiline = True, font_name = "bananaslip plus", width=self.window.width, batch = self.text_batch)
        self.section_text = Text("", self.window.width - 5, 5, colors.BLACK, 16, anchor_x = "right", font_name = "bananaslip plus", width=self.window.width, batch = self.text_batch)
        self.time_text = Text("0:00", self.window.width - 5, 35, colors.BLACK, 16, anchor_x = "right", font_name = "bananaslip plus", width=self.window.width, batch = self.text_batch)
        self.score_text = Text("0", self.window.width - 5, 65, colors.BLACK, 24, anchor_x = "right", font_name = "bananaslip plus", width=self.window.width, batch = self.text_batch)
        self.multiplier_text = Text("x1", self.window.width - 5, 95, colors.BLACK, 16, anchor_x = "right", font_name = "bananaslip plus", width=self.window.width, batch = self.text_batch)

        self.lyric_animator = None
        if self.hero_song.lyrics:
            self.lyric_animator = LyricAnimator(self.window.center_x, self.window.height - 100, self.hero_song.lyrics)
            self.lyric_animator.prerender()

        self.gum_wrapper = GumWrapper()
        super().postsetup()

    def on_show_view(self) -> None:
        self.window.theme_song.volume = 0
        self.song = arcade.play_sound(self._song, 0.25, loop=False)

    @shows_errors
    def on_button_press(self, keymap: KeyMap) -> None:
        if keymap.back.pressed:
            self.go_back()
        elif keymap.pause.pressed:
            self.song.pause() if self.song.playing else self.song.play()
        elif self.window.debug.enabled and keymap.seek_zero.pressed:
            self.song.seek(0)
        elif self.window.debug.enabled and keymap.seek_backward.pressed:
            self.song.seek(self.song.time - 5)
        elif self.window.debug.enabled and keymap.seek_forward.pressed:
            self.song.seek(self.song.time + 5)
        elif self.window.debug.enabled and keymap.debug_toggle_flags.pressed:
            self.highway.show_flags = not self.highway.show_flags

        self.engine.on_button_press(keymap)
        if keymap.back.pressed or keymap.pause.pressed:
            self.song.pause() if self.song.playing else self.song.play()
        if self.window.debug.enabled:
            if keymap.seek_zero.pressed:
                self.song.seek(0)
            if keymap.seek_backward.pressed:
                self.song.seek(0)
            if keymap.seek_forward.pressed:
                self.song.seek(self.song.time + 5)
            if keymap.debug_toggle_flags.pressed:
                self.highway.show_flags = not self.highway.show_flags

    @shows_errors
    def on_button_release(self, keymap: KeyMap) -> None:
        self.engine.on_button_release(keymap)

    def go_back(self) -> None:
        self.song.delete()
        super().go_back()

    @shows_errors
    def on_update(self, delta_time) -> None:
        super().on_update(delta_time)

        self.highway.update(self.song.time)

        self.engine.update(self.song.time)
        self.engine.calculate_score()

        # Section name
        # This should in theory be kinda fast because it's using Indexes?
        current_section: SectionEvent = self.hero_song.indexes_by_time["section"].lteq(self.song.time)
        if current_section and self.section_text.text != current_section.name:
            logger.debug(f"Section name is now {current_section.name} ({self.song.time})")
            self.section_text.text = current_section.name

        time_string = f"{self.song.time // 60:.0f}:{int(self.song.time % 60):02}"
        if self.time_text.text != time_string:
            self.time_text.text = time_string

        if self.score_text._label.text != f"{self.engine.score}":
            self.score_text._label.text = f"{self.engine.score}"

        if self.multiplier_text._label.text != f"x{self.engine.multiplier} [{self.engine.combo}]":
            self.multiplier_text._label.text = f"x{self.engine.multiplier} [{self.engine.combo}]"

        if self.lyric_animator:
            self.lyric_animator.update(self.song.time)

        self.gum_wrapper.update(delta_time)

    @shows_errors
    def on_draw(self) -> None:
        super().predraw()
        # Charm BG
        self.gum_wrapper.draw()

        self.highway.draw()
        self.text_batch.draw()

        if self.lyric_animator:
            with self.window.default_camera.activate():
                self.lyric_animator.draw()
        super().postdraw()
