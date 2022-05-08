from collections import defaultdict
from typing import cast, TypedDict
from dataclasses import dataclass
from pathlib import Path
import itertools
import logging
import re

from nindex import Index

from charm.lib.errors import ChartParseError, NoChartsError
from charm.lib.generic.song import Chart, Event, Metadata, Note, Seconds, Song

logger = logging.getLogger("charm")

RE_HEADER = r"\[(.+)\]"
RE_DATA = r"([^\s]+)\s*=\s*\"?([^\"]+)\"?"

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

class IndexDict(TypedDict):
    bpm: Index
    time_sig: Index
    section: Index

@dataclass
class TickEvent(Event):
    tick: int

    def __lt__(self, other: "TickEvent") -> bool:
        return self.tick < other.tick

@dataclass
class TSEvent(TickEvent):
    numerator: int
    denominator: int = 4

@dataclass
class TextEvent(TickEvent):
    text: str

@dataclass
class SectionEvent(TickEvent):
    name: str

@dataclass
class LyricEvent(TickEvent):
    text: str

@dataclass
class StarpowerEvent(TickEvent):
    tick_length: Ticks
    length: Seconds

@dataclass
class BPMChangeTickEvent(TickEvent):
    new_bpm: float

@dataclass
class RawBPMEvent:
    ticks: Ticks
    mbpm: int

# ---

def tick_to_seconds(current_tick: Ticks, sync_track: list[RawBPMEvent], resolution: int = 192, offset = 0) -> Seconds:
    """Takes a tick (and an associated sync_track,) and returns its position in seconds as a float."""
    current_tick = int(current_tick)  # you should really just be passing ints in here anyway but eh
    if current_tick == 0:
        return 0
    bpm_events = [b for b in sync_track if b.ticks <= current_tick]
    bpm_events.sort(key=lambda x: x.ticks)
    last_bpm_event = bpm_events[-1]
    tick_delta = current_tick - last_bpm_event.ticks
    bps = last_bpm_event.mbpm / 1000 / 60
    seconds = tick_delta / (resolution * bps)
    return seconds + offset

@dataclass
class HeroNote(Note):
    tick: int = None
    tick_length: Ticks = None

    @property
    def icon(self) -> str:
        return super().icon

    def __str__(self) -> str:
        return f"<HeroNote T:{self.tick}{'+' + self.tick_length if self.tick_length else ''} ({round(self.time, 3)}) lane={self.lane} type={self.type} length={round(self.length)}>"

    def __repr__(self) -> str:
        return self.__str__()

class HeroChord:
    """A data object to hold notes and have useful functions for manipulating and reading them."""
    def __init__(self, notes: list[HeroNote] = None) -> None:
        self.notes = notes if notes else []

    @property
    def frets(self) -> tuple[int]:
        return tuple(set(n.lane for n in self.notes))

    @property
    def tick(self) -> Ticks:
        return self.notes[0].tick

    @property
    def tick_length(self) -> Ticks:
        return max([n.tick_length for n in self.notes])

    @property
    def tick_end(self) -> Ticks:
        return self.tick + self.tick_length

    @property
    def type(self) -> str:
        return self.notes[0].type

    @type.setter
    def type(self, v):
        for n in self.notes:
            n.type = v

class HeroChart(Chart):
    def __init__(self, song: 'Song', difficulty: str, instrument: str, lanes: int, hash: str) -> None:
        super().__init__(song, "hero", difficulty, instrument, lanes, hash)
        self.chords: list[HeroChord] = None
        self.song = cast(HeroSong, self.song)

    def finalize(self):
        """Do some last-pass parsing steps."""
        self.create_chords()
        self.calculate_note_flags()
        self.calculate_hopos()
        self.events.sort()

    def create_chords(self):
        """Turn lists of notes (in `self.notes`) into `HeroChord`s (in `self.chords`)
        A chord is defined as all notes occuring at the same tick."""
        c = defaultdict(list)
        for note in self.notes:
            c[note.tick].append(note)
        chord_lists = list(c.values())
        chords = []
        for cl in chord_lists:
            chords.append(HeroChord(cl))
        self.chords = chords

    def calculate_note_flags(self):
        """Turn notes that aren't really notes but flags into properties on the notes."""
        for c in self.chords:
            forced = False
            tap = False
            for n in c.notes:
                if n.lane == 5:  # HOPO force
                    forced = True
                elif n.lane == 6:  # Tap
                    tap = True
            for n in c.notes:
                # Tap overrides HOPO, intentionally.
                if tap:
                    n.type = "tap"
                elif forced:
                    n.type = "forced"
            c = HeroChord([n for n in c.notes if n.lane not in [5, 6]])

    def calculate_hopos(self):
        # This is basically ripped from Charm-Legacy.
        # https://github.com/DigiDuncan/Charm-Legacy/blob/3187a8f2fa8c8876c2706b731bff6913dc0bad60/charm/song.py#L179
        for last_chord, current_chord in zip(self.chords[:-1], self.chords[1:]):  # python zip pattern, wee
            timesig = self.song.indexes_by_tick["time_sig"].lteq(last_chord.tick)
            if timesig is None:
                timesig = TSEvent(0, 0, 4, 4)

            ticks_per_quarternote = self.song.resolution
            ticks_per_wholenote = ticks_per_quarternote * 4
            beats_per_wholenote = timesig.denominator
            ticks_per_beat = ticks_per_wholenote / beats_per_wholenote

            chord_distance = current_chord.tick - last_chord.tick

            hopo_cutoff = ticks_per_beat / (192 / 66)  # Why? Where does this number come from?
                                                       # It's like 1/81 more than 1/3? Why?

            if current_chord.frets == last_chord.frets:
                # You can't have two HOPO chords of the same fretting.
                if current_chord.type == "forced":
                    current_chord.type = "normal"
            elif chord_distance <= hopo_cutoff:
                if current_chord.type == "forced":
                    current_chord.type = "normal"
                elif current_chord.type == "normal":
                    current_chord.type = "hopo"
            else:
                if current_chord.type == "forced":
                    current_chord.type = "hopo"

class HeroSong(Song):
    def __init__(self, name: str):
        super().__init__(name)
        self.indexes_by_tick: IndexDict = {}
        self.indexes_by_time: IndexDict = {}
        self.resolution: int = 192

    @classmethod
    def parse(cls, folder: Path) -> "HeroSong":
        if not (folder / "notes.chart").exists():
            raise NoChartsError(folder.stem)
        with open(folder / "notes.chart") as f:
            chartfile = f.readlines()
        
        resolution: Ticks = 192
        offset: Seconds = 0
        metadata = Metadata("Unknown Title")
        charts: dict[str, HeroChart] = {}
        events: list[Event] = []

        line_num = 0
        last_line_type = None  # unused
        last_header = None
        sync_track: list[RawBPMEvent] = []

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
                if m := re.match(RE_DATA, line):
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
                            metadata.year = int(m.group(2).removeprefix(",").strip())
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
                            logger.debug(f"Unrecognized .chart metadata {line!r}")
                else:
                    raise ChartParseError(line_num, f"Non-metadata found in metadata section: {line!r}")
            elif last_header == "SyncTrack":
                if m := re.match(RE_A, line):
                    # ignore anchor events
                    continue
                # BPM Events
                elif m := re.match(RE_B, line):
                    tick, mbpm = [int(i) for i in m.groups()]
                    tick = int(tick)
                    if not sync_track and tick != 0:
                        raise ChartParseError(line_num, "Chart has no BPM event at tick 0.")
                    elif not sync_track:
                        events.append(BPMChangeTickEvent(0, tick, mbpm / 1000))
                        sync_track.append(RawBPMEvent(0, mbpm))
                    else:
                        seconds = tick_to_seconds(tick, sync_track, resolution, offset)
                        events.append(BPMChangeTickEvent(seconds, tick, mbpm / 1000))
                        sync_track.append(RawBPMEvent(tick, mbpm))
                # Time Sig events
                elif m := re.match(RE_TS, line):
                    tick, num, denom = m.groups()
                    tick = int(tick)
                    denom = 4 if denom is None else denom ** 2
                    seconds = tick_to_seconds(tick, sync_track, resolution, offset)
                    events.append(TSEvent(seconds, tick, int(num), int(denom)))
                else:
                    raise ChartParseError(line_num, f"Non-sync event in SyncTrack: {line!r}")
            # Events sections
            elif last_header == "Events":
                # Section events
                if m := re.match(RE_SECTION, line):
                    tick, name = m.groups()
                    tick = int(tick)
                    seconds = tick_to_seconds(tick, sync_track, resolution, offset)
                    events.append(SectionEvent(seconds, tick, name))
                # Lyric events
                elif m := re.match(RE_LYRIC, line):
                    tick, text = m.groups()
                    tick = int(tick)
                    seconds = tick_to_seconds(tick, sync_track, resolution, offset)
                    events.append(LyricEvent(seconds, tick, text))
                # Misc. events
                elif m := re.match(RE_E, line):
                    tick, text = m.groups()
                    tick = int(tick)
                    seconds = tick_to_seconds(tick, sync_track, resolution, offset)
                    events.append(TextEvent(seconds, tick, text))
                else:
                    raise ChartParseError(line_num, f"Non-event in Events: {line!r}")
            else:
                # We are in a chart section
                diff, inst = DIFF_INST_MAP[last_header]
                if last_header not in charts:
                    charts[last_header] = HeroChart(None, diff, inst, 5, None)
                chart = charts[last_header]
                # Track events
                if m := re.match(RE_TRACK_E, line):
                    tick, text = m.groups()
                    tick = int(tick)
                    seconds = tick_to_seconds(tick, sync_track, resolution, offset)
                    chart.events.append(TextEvent(seconds, tick, text))
                # Note events
                elif m:= re.match(RE_N, line):
                    tick, lane, length = m.groups()
                    tick = int(tick)
                    length = int(length)
                    seconds = tick_to_seconds(tick, sync_track, resolution, offset)
                    end = tick_to_seconds(tick + length, sync_track, resolution, offset)
                    sec_length = round(end - seconds, 5)  # accurate to 1/100ms
                    chart.notes.append(HeroNote(chart, seconds, int(lane), sec_length, tick = tick, tick_length = length))  # TODO: Note flags.
                # Special events
                elif m:= re.match(RE_S, line):
                    tick, s_type, length = m.groups()
                    tick = int(tick)
                    length = int(length)
                    seconds = tick_to_seconds(tick, sync_track, resolution, offset)
                    end = tick_to_seconds(tick + length, sync_track, resolution, offset)
                    sec_length = round(end - seconds, 5)  # accurate to 1/100ms
                    if s_type == "2":
                        chart.events.append(StarpowerEvent(seconds, tick, length, sec_length))
                    # Ignoring non-SP events for now...
                else:
                    raise ChartParseError(line_num, f"Non-chart event in {last_header}: {line!r}")

        # Finalize
        song = HeroSong(metadata.key)
        song.index()
        for chart in charts.values():
            chart.song = song
            chart.finalize()
            song.charts.append(chart)
        for event in events:
            song.events.append(event)
        song.events.sort()
        song.resolution = resolution
        song.metadata = metadata
        return song

    def index(self):
        """Save indexes of important look-up events."""
        self.indexes_by_tick["bpm"] = Index(self.events_by_type(BPMChangeTickEvent), "tick")
        self.indexes_by_tick["time_sig"] = Index(self.events_by_type(TSEvent), "tick")
        self.indexes_by_tick["section"] = Index(self.events_by_type(SectionEvent), "tick")

        self.indexes_by_time["bpm"] = Index(self.events_by_type(BPMChangeTickEvent), "time")
        self.indexes_by_time["time_sig"] = Index(self.events_by_type(TSEvent), "time")
        self.indexes_by_time["section"] = Index(self.events_by_type(SectionEvent), "time")