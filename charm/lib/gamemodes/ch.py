import re
from pathlib import Path
from charm.lib.generic.song import Chart, Note, Song

RE_HEADER = r"\[(.+)\]"
RE_DATA = r"(.+)\s*=\s*(.+)"


class HeroNote(Note):
    @property
    def icon(self) -> str:
        return super().icon


class HeroChart(Chart):
    def __init__(self, song: 'Song', difficulty: str, instrument: str, lanes: int, hash: str) -> None:
        super().__init__(song, "hero", difficulty, instrument, lanes, hash)


class HeroSong(Song):
    def __init__(self, name: str):
        super().__init__(name)

    @classmethod
    def parse(self, folder: Path) -> "HeroSong":
        pass