
from __future__ import annotations
from typing import TYPE_CHECKING

import arcade

from charm.objects.lyric_animator import LyricAnimator, LyricEvent
if TYPE_CHECKING:
    from charm.lib.digiview import DigiWindow
from collections.abc import Sequence

from arcade import get_window

from charm.lib.types import Seconds
from charm.lib.displayables import Timer

from charm.core.generic import Display
from .chart import FiveFretChart, SectionEvent
from .engine import FiveFretEngine
from .highway import FiveFretHighway


class FiveFretDisplay(Display[FiveFretChart, FiveFretEngine]):
    def __init__(self, engine: FiveFretEngine, charts: Sequence[FiveFretChart]):
        super().__init__(engine, charts)
        self._win: DigiWindow = get_window()  # type: ignore | aaa shut up Arcade
        self.chart = charts[0]

        self.highway: FiveFretHighway = FiveFretHighway(self.chart, engine, (0, 0), (self._win.width // 4, self._win.height))
        self.highway.x = self._win.center_x - self.highway.w // 2

        # Timer
        self.timer = Timer(250, 60)
        self.timer.center_x = self._win.width - 135
        self.timer.center_y = 60

        # Lyric animator
        if lyrics := self.chart.events_by_type(LyricEvent):
            self.lyric_animator: LyricAnimator = LyricAnimator(self._win.width / 2, self._win.height * 0.9, lyrics)
            self.lyric_animator.prerender()
        else:
            self.lyric_animator: LyricAnimator = None

        self.sections = self.chart.events_by_type(SectionEvent)
        self.current_section = self.sections[0] if self.sections else "No Section"

    def update(self, song_time: Seconds) -> None:
        self._song_time = song_time

        self.highway.update(song_time)

        self.timer.current_time = song_time
        self.timer.update(self._win.delta_time)

        if self.lyric_animator:
            self.lyric_animator.update(song_time)

        if self.sections:
            sec = self.current_section = self.chart.indices.section_time.lteq(song_time)
            self.current_section = sec.name if sec else "No Section"

    def draw(self) -> None:
        self.highway.draw()

        # self.hp_bar.draw()
        self.timer.draw()

        arcade.draw_text(self.current_section, self.timer.x + self.timer.width, self.timer.y + self.timer.height + 5, arcade.color.BLACK, 24, align = "right", font_name = "bananaslip plus", anchor_x = "right", anchor_y = "bottom")

        if self.lyric_animator:
            self.lyric_animator.draw()