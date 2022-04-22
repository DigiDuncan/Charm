import itertools
import re
from pathlib import Path
from charm.lib.errors import ChartParseError, NoChartsError
from charm.lib.generic.song import Chart, Note, Song

RE_HEADER = r"\[(.+)\]"
RE_DATA = r"(.+)\s*=\s*(.+)"

RE_B = r"(\d+)\s*=\s*B\s(\d+)"  # BPM Event
RE_TS = r"(\d+)\s*=\s*TS\s(\d+)\s?(\d+)?"  # Time Sig Event
RE_A = r"(\d+)\s*=\s*A\s(\d+)"  # Anchor Event (unused by games, editor only)
RE_E = r"(\d+)\s*=\s*E\s\"(.*)\""  # Text Event (basically anything, fun)
RE_SECTION = r"(\d+)\s*=\s*E\s\"section (.*)\""  # Section Event (subtype of E)
RE_LYRIC = r"(\d+)\s*=\s*E\s\"lyric (.*)\""  # Lyric Event (subtype of E)
RE_N = r"(\d+)\s*=\s*N\s(\d+)\s?(\d+)?"  # Note Event (or note flag event...)
RE_S = r"(\d+)\s*=\s*S\s(\d+)\s?(\d+)?"  # "Special Event" (really guys?)
RE_TRACK_E = r"(\d+)\s*=\s*E\s([^\s]+)"  # Track Event (text event but with no quotes)

DIFFICULTIES = ["Easy", "Medium", "Hard", "Expert"]
INSTRUMENTS = ["Single", "DoubleGuitar", "DoubleBass", "DoubleRhythm", "Drums", "Keyboard", "GHLGuitar", "GHLBass"]
SPECIAL_HEADERS = ["Song", "SyncTrack", "Events"]
DIFF_INST_PAIRS = [a + b for a, b in itertools.product(DIFFICULTIES, INSTRUMENTS)]
VALID_HEADERS = DIFF_INST_PAIRS + SPECIAL_HEADERS


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
        if not (folder / "notes.chart").exists():
            raise NoChartsError(folder.stem)
        with open(folder / "notes.chart") as f:
            chartfile = f.readlines()

        linenum = 0
        lastlinetype = None
        lastheader = None
        for line in chartfile:
            line = line.strip().strip("\uffef")  # god dang ffef
            linenum += 1

            # Parse headers
            if m := re.match(RE_HEADER, line):
                header = m.group(1)
                if header not in VALID_HEADERS:
                    raise ChartParseError(linenum, f"{header} is not a valid header.")
                if lastheader is None and header != "Song":
                    raise ChartParseError(linenum, "First header must be Song.")
                lastlinetype = "header"
                lastheader = header