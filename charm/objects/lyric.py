from os import PathLike
import re

import pysubs2
from pysubs2 import SSAEvent, SSAFile, SSAStyle

from charm.lib.generic.song import Seconds

re_karaoke = re.compile(r"{\\(kf?)(\d+)}([^{}]+)")


class LyricAnimator:
    def __init__(self, sub_file: PathLike):
        self.subtitles = pysubs2.load(str(sub_file))
        self.active_events = self.subtitles.events.copy()
        self.current_events: list[SSAEvent] = []
        self.song_time = 0

    def song_time_ms(self) -> int:
        return int(self.song_time * 1000)

    def get_style_from_event(self, event: SSAEvent):
        return self.subtitles.styles[event.style]

    def update(self, song_time: Seconds):
        self.song_time = song_time
        for event in self.current_events:
            if event.end < self.song_time_ms:
                self.current_events.remove(event)
        for event in self.subtitles.active_events:
            if event.start <= self.song_time_ms:
                self.current_events.append(event)
                self.active_events.remove(event)

    def draw(self):
        pass
