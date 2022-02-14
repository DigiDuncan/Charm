from dataclasses import dataclass
from functools import total_ordering
from typing import Optional

Seconds = float
Milliseconds = float


@dataclass
@total_ordering
class Note:
    """Represents a note on a chart.

    - `time`: float`: (in seconds, 0 is the beginning of the song)
    - `lane: int`: The key the user will have to hit to trigger this note
    (which usually corrosponds with it's X position on the highway)
    - `length: float`: the length of the note in seconds, 0 by default.
    - `type: str`: the note's type, 'normal' be default."""
    uuid: str
    time: Seconds
    lane: int
    length: Seconds = 0
    type: str = "normal"

    hit: bool = False
    missed: bool = False
    hit_time: Optional[Seconds] = None

    def __lt__(self, other) -> bool:
        if isinstance(other, Note):
            return (self.time, self.lane) < (other.time, other.lane)
        elif isinstance(other, Event):
            if self.time == other.time:
                return False
            return self.time < other.time


@dataclass
class Event:
    """A very basic event that happens at a time."""
    time: Seconds

    def __lt__(self, other) -> bool:
        return self.time < other.time


@dataclass
class BPMChangeEvent(Event):
    new_bpm: int
    icon = "bpm"


class Chart:
    def __init__(self, gamemode: str, difficulty: str, instrument: str, lanes: int) -> None:
        self.gamemode = gamemode
        self.difficulty = difficulty
        self.instrument = instrument
        self.lanes = lanes
        self.notes: list[Note] = []
        self.events: list[Event] = []

        self.note_by_uuid: dict[str, Note] = {}


class Song:
    def __init__(self, name: str, bpm: float) -> None:
        self.name = name
        self.metadata = {
            "title": name,
            "artist": "Unknown Artist",
            "album": "Unknown Album"
        }
        self.bpm = bpm
        self.charts: list[Chart] = []
        self.events: list[Event] = []

    @classmethod
    def parse(cls, s: str):
        raise NotImplementedError
