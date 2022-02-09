from typing import Iterable
from charm.lib.song import Chart, Note, Seconds


class Engine:
    def __init__(self, chart: Chart, hit_window: Seconds) -> None:
        self.chart = chart
        self.hit_window = hit_window
        self.score = 0

    def update(self, song_time):
        pass

    def get_hittable_notes(self, current_time: Seconds) -> Iterable[Note]:
        n = 0
        while n < len(self.active_notes):
            note = self.active_notes[n]
            is_expired = note.position < current_time - (self.hit_window / 2)
            is_waiting = note.position > current_time + (self.hit_window / 2)
            if is_expired:
                del self.active_notes[n]
                n -= 1
            elif is_waiting:
                break
            else:
                yield note
            n += 1
