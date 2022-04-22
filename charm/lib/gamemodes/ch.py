from dataclasses import dataclass
from importlib.metadata import metadata
import itertools
from math import log
import re
from pathlib import Path
from charm.lib.errors import ChartParseError, NoChartsError
from charm.lib.generic.song import BPMChangeEvent, Chart, Event, Metadata, Note, Seconds, Song

RE_HEADER = r"\[(.+)\]"
RE_DATA = r"(.+)\s*=\s*\"?(.+)\"?"

RE_B = r"(\d+)\s*=\s*B\s(\d+)"  # BPM Event
RE_TS = r"(\d+)\s*=\s*TS\s(\d+)\s?(\d+)?"  # Time Sig Event
RE_A = r"(\d+)\s*=\s*A\s(\d+)"  # Anchor Event (unused by games, editor only)
RE_E = r"(\d+)\s*=\s*E\s\"(.*)\""  # Text Event (basically anything, fun)
RE_SECTION = r"(\d+)\s*=\s*E\s\"section (.*)\""  # Section Event (subtype of E)
RE_LYRIC = r"(\d+)\s*=\s*E\s\"lyric (.*)\""  # Lyric Event (subtype of E)
RE_N = r"(\d+)\s*=\s*N\s(\d+)\s?(\d+)?"  # Note Event (or note flag event...)
RE_S = r"(\d+)\s*=\s*S\s(\d+)\s?(\d+)?"  # "Special Event" (really guys?)
RE_STARPOWER = r"(\d+)\s*=\s*S\s2\s?(\d+)?"  # Starpower Event (subtype of S)
RE_TRACK_E = r"(\d+)\s*=\s*E\s([^\s]+)"  # Track Event (text event but with no quotes)

DIFFICULTIES = ["Easy", "Medium", "Hard", "Expert"]
INSTRUMENTS = ["Single", "DoubleGuitar", "DoubleBass", "DoubleRhythm", "Drums", "Keyboard", "GHLGuitar", "GHLBass"]
SPECIAL_HEADERS = ["Song", "SyncTrack", "Events"]
DIFF_INST_PAIRS = [a + b for a, b in itertools.product(DIFFICULTIES, INSTRUMENTS)]
DIFF_INST_MAP: dict[str, tuple[str, str]] = {(a + b): (a, b) for a, b in itertools.product(DIFFICULTIES, INSTRUMENTS)}
VALID_HEADERS = DIFF_INST_PAIRS + SPECIAL_HEADERS

Ticks = int

@dataclass
class TSEvent(Event):
    new_numerator: int
    new_denominator: int = 4

@dataclass
class TextEvent(Event):
    text: str

@dataclass
class SectionEvent(Event):
    name: str

@dataclass
class LyricEvent(Event):
    text: str

@dataclass
class StarpowerEvent(Event):
    pass

@dataclass
class RawBPMEvent:
    ticks: Ticks
    mbpm: int

# ---

def tick_to_seconds(current_tick: Ticks, last_bpm_tick: Ticks, last_mbpm: int, resolution: int = 192) -> Seconds:
    tick_delta = current_tick - last_bpm_tick
    bps = last_mbpm / 1000 / 60
    seconds = tick_delta / (resolution * bps)
    return seconds

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
        
        resolution: Ticks = 192
        offset: Seconds = 0
        metadata = Metadata("Unknown Title")
        charts: list[HeroChart] = []
        events: list[Event] = []

        line_num = 0
        last_line_type = None
        last_header = None
        last_bpm_event = None

        for line in chartfile:
            line = line.strip().strip("\uffef")  # god dang ffef
            line_num += 1

            # Screw curly braces
            if line == "{" or line == "}":
                continue
            # Parse headers
            if m := re.match(RE_HEADER, line):
                header = m.group(1)
                if header not in VALID_HEADERS:
                    raise ChartParseError(line_num, f"{header} is not a valid header.")
                if last_header is None and header != "Song":
                    raise ChartParseError(line_num, "First header must be Song.")
                last_line_type = "header"
                last_header = header
            # Parse metadata
            elif last_header == "Song":
                if m:= re.match(RE_DATA, line):
                    match m.group(1):
                        case "Resolution":
                            resolution = Ticks(m.group(2))
                        case "Name":
                            metadata.title = m.group(2)
                        case "Artist":
                            metadata.artist = m.group(2)
                        case "Album":
                            metadata.album = m.group(2)
                        case "Year":
                            metadata.year = int(m.group(2).removeprefix(", "))
                        case "Charter":
                            metadata.charter = m.group(2)
                        case "Offset":
                            offset = Seconds(m.group(2))
                        # Skipping "Player2"
                        case "Difficulty":
                            metadata.difficulty = int(m.group(2))
                        case "PreviewStart":
                            metadata.preview_start = Seconds(m.group(2))
                        case "PreviewEnd":
                            metadata.preview_end = Seconds(m.group(2))
                        case "Genre":
                            metadata.genre = m.group(2)
                        # Skipping "MediaType"
                        # Skipping "Audio streams"
                        case _:
                            # Maybe don't raise an error and just skip?
                            raise ChartParseError(line_num, f"{m.group(1)} is not a valid metadata key.")
                else:
                    raise ChartParseError(line_num, f"Non-metadata found in metadata section: {line!r}")
            elif last_header == "SyncTrack":
                if m := re.match(RE_A, line):
                    # ignore anchor events
                    continue
                # BPM Events
                elif m := re.match(RE_B, line):
                    tick, mbpm = [int(i) for i in m.groups()]
                    if last_bpm_event is None and tick != "0":
                        raise ChartParseError("Chart has no BPM event at tick 0.")
                    elif last_bpm_event is None:
                        events.append(BPMChangeEvent(0, mbpm / 1000))
                        last_bpm_event = RawBPMEvent(0, mbpm)
                    else:
                        tick_delta = tick - last_bpm_event.ticks
                        bps = last_bpm_event.mbpm / 1000 / 60
                        seconds = tick_delta / (resolution * bps)
                        events.append(BPMChangeEvent(seconds, mbpm / 1000))
                        last_bpm_event = RawBPMEvent(tick, mbpm)
                # Time Sig events
                elif m := re.match(RE_TS):
                    tick, num, denom = [int(i) for i in m.groups()]
                    denom = 4 if denom is None else denom ** 2
                    seconds = tick_to_seconds(tick, last_bpm_event.ticks, last_bpm_event.mbpm, resolution)
                    events.append(TSEvent(seconds, num, denom))
                else:
                    raise ChartParseError(line_num, f"Non-sync event in SyncTrack: {line!r}")
            # Events sections
            elif last_header == "Events":
                # Section events
                if m := re.match(RE_SECTION, line):
                    tick, name = m.groups()
                    seconds = tick_to_seconds(tick, last_bpm_event.ticks, last_bpm_event.mbpm, resolution)
                    events.append(SectionEvent(seconds, name))
                # Lyric events
                elif m := re.match(RE_LYRIC, line):
                    tick, text = m.groups()
                    seconds = tick_to_seconds(tick, last_bpm_event.ticks, last_bpm_event.mbpm, resolution)
                    events.append(LyricEvent(seconds, text))
                # Misc. events
                elif m := re.match(RE_E, line):
                    tick, text = m.groups()
                    seconds = tick_to_seconds(tick, last_bpm_event.ticks, last_bpm_event.mbpm, resolution)
                    events.append(TextEvent(seconds, text))
                else:
                    raise ChartParseError(line_num, f"Non-event in Events: {line!r}")
            