from dataclasses import dataclass
from typing import Literal, TYPE_CHECKING
from charm.lib.generic.song import Chart, Note, Seconds
if TYPE_CHECKING:
    from charm.lib.generic.results import Results

KeyStates = list[bool]
Key = int

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
    time: float

    def __lt__(self, other):
        self.time < other.time


@dataclass
class DigitalKeyEvent(EngineEvent):
    key: int
    new_state: Literal["up", "down"]

    def __lt__(self, other):
        (self.time, self.key) < (other.time, other.key)


class Engine:
    def __init__(self, chart: Chart, mapping: list[Key], hit_window: Seconds, judgements: list[Judgement] = [], offset: Seconds = 0):
        self.chart = chart
        self.mapping = mapping
        self.hit_window = hit_window
        self.offset = offset
        self.judgements = judgements

        self.chart_time: Seconds = 0
        self.active_notes = self.chart.notes.copy()

        self.key_state = [False] * len(mapping)
        self.current_events: list[EngineEvent] = []

        # Scoring
        self.score: int = 0
        self.hits: int = 0
        self.misses: int = 0

        # Accuracy
        self.max_notes = len(self.chart.notes)
        self.weighted_hit_notes: int = 0

    @property
    def accuracy(self) -> float | None:
        if self.hits or self.misses:
            return self.weighted_hit_notes / (self.hits + self.misses)
        return 0

    @property
    def grade(self) -> str:
        accuracy = self.accuracy * 100
        if accuracy is not None:
            if accuracy >= 97.5:
                return "SS"
            elif accuracy >= 95:
                return "S"
            elif accuracy >= 90:
                return "A"
            elif accuracy >= 80:
                return "B"
            elif accuracy >= 70:
                return "C"
            elif accuracy >= 60:
                return "D"
            else:
                return "F"
        return "C"

    @property
    def fc_type(self) -> str:
        if self.accuracy is not None:
            if self.misses == 0:
                if self.grade in ["SS", "S", "A"]:
                    return f"{self.grade}FC"
                else:
                    return "FC"
            elif self.misses < 10:
                return f"SDCB (-{self.misses})"
        return "Clear"

    def update(self, song_time: Seconds):
        self.chart_time = song_time + self.offset

    def process_keystate(self, key_states: KeyStates):
        raise NotImplementedError

    def get_note_judgement(self, note: Note) -> Judgement:
        rt = abs(note.hit_time - note.time)
        # FIXME: Lag?
        for j in self.judgements:
            if rt <= j.seconds:
                return j
        return self.judgements[-1]

    def generate_results(self) -> "Results":
        raise NotImplementedError