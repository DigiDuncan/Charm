from __future__ import annotations

from dataclasses import dataclass
from functools import total_ordering
from pathlib import Path
from typing import Optional

Seconds = float
Milliseconds = float


@dataclass
@total_ordering
class Note:
    """Represents a note on a chart.

    - `chart: Chart`: the chart this Note belongs to
    - `time: float`: (in seconds, 0 is the beginning of the song)
    - `lane: int`: The key the user will have to hit to trigger this note
    (which usually corrosponds with it's X position on the highway)
    - `length: float`: the length of the note in seconds, 0 by default
    - `type: str`: the note's type, 'normal' be default

    - `hit: bool`: has this note been hit?
    - `missed: bool`: has this note been missed?
    - `hit_time: float`: when was this note hit?

    - `extra_data: tuple`: ¯\_(ツ)_/¯"""  # noqa
    chart: Chart
    time: Seconds
    lane: int
    length: Seconds = 0
    type: str = "normal"

    hit: bool = False
    missed: bool = False
    hit_time: Optional[Seconds] = None

    extra_data: tuple = None

    @property
    def icon(self) -> str:
        return NotImplemented

    @property
    def is_sustain(self) -> bool:
        return self.length > 0

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


class Chart:
    def __init__(self, song: 'Song', gamemode: str, difficulty: str, instrument: str, lanes: int, hash: str) -> None:
        self.song: Song = song
        self.gamemode = gamemode
        self.difficulty = difficulty
        self.instrument = instrument
        self.lanes = lanes
        self.hash = hash

        self.notes: list[Note] = []
        self.events: list[Event] = []
        self.bpm: float = None


class Song:
    def __init__(self, name: str):
        self.name = name
        self.path: Path = None
        self.metadata = {
            "title": name,
            "artist": "Unknown Artist",
            "album": "Unknown Album"
        }
        self.charts: list[Chart] = []
        self.events: list[Event] = []

    @classmethod
    def parse(cls, folder: str):
        raise NotImplementedError
