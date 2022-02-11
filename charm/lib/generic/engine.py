from dataclasses import dataclass
from typing import Literal
from charm.lib.generic.song import Chart, Note, Seconds

KeyStates = list[bool]


@dataclass
class Judgement:
    name: str
    ms: int  # maximum
    score: int
    accuracy_weight: float
    hp_change: float = 0

    @property
    def seconds(self):
        return self.ms / 1000

    def __lt__(self, other):
        return self.ms < other.ms


@dataclass
class EngineEvent:
    pass


@dataclass
class DigitalKeyEvent(EngineEvent):
    key: int
    new_state: Literal["up", "down"]
    time: float

    def __lt__(self, other):
        (self.time, self.key) < (self.time, self.key)


class Engine:
    def __init__(self, chart: Chart, mapping: list[int], hit_window: Seconds, judgements: list[Judgement] = [], offset: Seconds = 0) -> None:
        self.chart = chart
        self.mapping = mapping
        self.hit_window = hit_window
        self.offset = offset
        self.judgements = judgements

        self.chart_time = 0
        self.active_notes = self.chart.notes.copy()

        self.key_state = [False] * len(mapping)
        self.current_events: list[EngineEvent] = []

        # Scoring
        self.score = 0

        # Accuracy
        self.max_notes = len(self.chart.notes)
        self.weighted_hit_notes = 0

    def update(self, song_time: Seconds):
        self.chart_time = song_time + self.offset

    def process_keystate(self, key_states: KeyStates):
        raise NotImplementedError

    def get_note_judgement(self, note: Note):
        rt = abs(note.hit_time - note.position)
        for j in self.judgements:
            if rt <= j.seconds:
                return j
        return self.judgements[-1]

    # def get_hittable_notes(self, current_time: Seconds) -> Iterable[Note]:
    #     n = 0
    #     while n < len(self.active_notes):
    #         note = self.active_notes[n]
    #         is_expired = note.position < current_time - (self.hit_window / 2)
    #         is_waiting = note.position > current_time + (self.hit_window / 2)
    #         if is_expired:
    #             del self.active_notes[n]
    #             n -= 1
    #         elif is_waiting:
    #             break
    #         else:
    #             yield note
    #         n += 1
