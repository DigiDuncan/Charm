from collections import defaultdict
from functools import cache
from typing import cast, TypedDict
from dataclasses import dataclass
from pathlib import Path
import itertools
import logging
import re
import PIL.Image
import arcade

from nindex import Index
from charm.lib.charm import load_missing_texture

from charm.lib.errors import ChartParseError, ChartPostReadParseError, NoChartsError
from charm.lib.generic.highway import Highway
from charm.lib.generic.song import Chart, Event, Metadata, Note, Seconds, Song
from charm.lib.settings import Settings
from charm.lib.spritebucket import SpriteBucketCollection
from charm.lib.utils import img_from_resource

import charm.data.images.skins.hero as heroskin

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
# Produce every unique pair of difficulties and instruments (e.g.: EasySingle) and map them to tuples (e.g.: (Easy, Single))
DIFF_INST_MAP: dict[str, tuple[str, str]] = {(a + b): (a, b) for a, b in itertools.product(DIFFICULTIES, INSTRUMENTS)}
VALID_HEADERS = list(DIFF_INST_MAP.keys()) + SPECIAL_HEADERS

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

    @property
    def time_sig(self) -> tuple[int, int]:
        return (self.numerator, self.denominator)

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
class SoloEvent(TickEvent):
    tick_length: Ticks
    length: Seconds

@dataclass
class BPMChangeTickEvent(TickEvent):
    new_bpm: float

@dataclass
class RawBPMEvent:
    """Only used for parsing, and shouldn't be in a Song post-parse."""
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

    def finalize(self):
        """Do some last-pass parsing steps."""
        self.create_chords()
        self.calculate_note_flags()
        self.calculate_hopos()
        self.parse_text_events()

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

    def parse_text_events(self):
        self.events = cast(list[TickEvent], self.events)
        parsed: list[TextEvent] = []
        new_events: list[SoloEvent] = []
        current_solo = None
        for e in [e for e in self.events if isinstance(e, TextEvent)]:
            if e.text == "solo":
                current_solo = e
                parsed.append(e)
            elif e.text == "soloend":
                if current_solo is None:
                    raise ChartPostReadParseError("`solo_end` without `solo` event!")
                else:
                    tick_length = e.tick - current_solo.tick
                    length = e.time - current_solo.time
                    new_events.append(SoloEvent(current_solo.time, current_solo.tick, tick_length, length))
                    current_solo = None
                parsed.append(e)
        for e in parsed:
            self.events.remove(e)
        for e in new_events:
            self.events.append(e)
        self.events.sort()


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
        with open(folder / "notes.chart", encoding = "utf-8") as f:
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
                    # ignore anchor events [only used for charting]
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
                    logger.debug(f"Added section {line}")
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
                elif m := re.match(RE_N, line):
                    tick, lane, length = m.groups()
                    tick = int(tick)
                    length = int(length)
                    seconds = tick_to_seconds(tick, sync_track, resolution, offset)
                    end = tick_to_seconds(tick + length, sync_track, resolution, offset)
                    sec_length = round(end - seconds, 5)  # accurate to 1/100ms
                    chart.notes.append(HeroNote(chart, seconds, int(lane), sec_length, tick = tick, tick_length = length))  # TODO: Note flags.
                # Special events
                elif m := re.match(RE_S, line):
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
        for event in events:
            song.events.append(event)
        song.events.sort()
        song.index()
        for chart in charts.values():
            chart.song = song
            chart.finalize()
            song.charts.append(chart)
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

@cache
def load_note_texture(note_type, note_lane, height):
    image_name = f"{note_type}-{note_lane + 1}"
    open_height = int(height / (128 / 48))
    try:
        image = img_from_resource(heroskin, image_name + ".png")
        if image.height != height and note_lane != 7:
            width = int((height / image.height) * image.width)
            image = image.resize((width, height), PIL.Image.LANCZOS)
        elif image.height != open_height:
            width = int((open_height / image.height) * image.width)
            image = image.resize((width, open_height), PIL.Image.LANCZOS)
    except Exception as e:
        logger.error(f"Unable to load texture: {image_name} | {e}")
        return load_missing_texture(height, height)
    return arcade.Texture(f"_heronote_{image_name}", image=image, hit_box_algorithm=None)

class HeroNoteSprite(arcade.Sprite):
    def __init__(self, note: HeroNote, highway: "HeroHighway", height = 128, *args, **kwargs):
        self.note: HeroNote = note
        self.highway: HeroHighway = highway
        tex = load_note_texture(note.type, note.lane, height)
        super().__init__(texture=tex, *args, **kwargs)

    def __lt__(self, other: "HeroNoteSprite"):
        return self.note.time < other.note.time

    def update_animation(self, delta_time: float):
        if self.highway.auto:
            if self.highway.song_time >= self.note.time:
                self.note.hit = True
        elif self.note.hit:
            self.alpha = 0

class HeroHighway(Highway):
    def __init__(self, chart: HeroChart, pos: tuple[int, int], size: tuple[int, int] = None, gap: int = 5, auto = False, show_flags = False):
        if size is None:
            size = int(Settings.width / (1280 / 400)), Settings.height

        super().__init__(chart, pos, size, gap, downscroll = True)

        self.viewport = 0.75  # TODO: Set dynamically.

        self.auto = auto

        self._show_flags = show_flags

        self.color = (0, 0, 0, 128)

        self.sprite_buckets = SpriteBucketCollection()
        for note in self.notes:
            sprite = HeroNoteSprite(note, self, self.note_size)
            sprite.top = self.note_y(note.time)
            sprite.left = self.lane_x(note.lane)
            if note.lane in [5, 6]:  # flags
                sprite.left = self.lane_x(5)
                if self._show_flags is False:
                    sprite.alpha = 0
            elif note.lane == 7:  # open
                sprite.center_x = self.w / 2
            note.sprite = sprite
            self.sprite_buckets.append(sprite, note.time, note.length)

        self.strikeline = arcade.SpriteList()
        # TODO: Is this dumb?
        for i in range(5):
            sprite = HeroNoteSprite(HeroNote(self.chart, 0, i, 0, "strikeline"), self, self.note_size)
            sprite.top = self.strikeline_y
            sprite.left = self.lane_x(sprite.note.lane)
            sprite.alpha = 128
            self.strikeline.append(sprite)

        logger.debug(f"Generated highway for chart {chart.instrument}.")

        # TODO: Replace with better pixel_offset calculation
        self.last_update_time = 0
        self._pixel_offset = 0

    def update(self, song_time: float):
        super().update(song_time)
        self.sprite_buckets.update_animation(song_time)
        # TODO: Replace with better pixel_offset calculation
        delta_draw_time = self.song_time - self.last_update_time
        self._pixel_offset += (self.px_per_s * delta_draw_time)
        self.last_update_time = self.song_time

    @property
    def pos(self) -> tuple[int, int]:
        return self._pos

    @pos.setter
    def pos(self, p: tuple[int, int]):
        old_pos = self._pos
        diff_x = p[0] - old_pos[0]
        diff_y = p[1] - old_pos[1]
        self._pos = p
        for bucket in self.sprite_buckets.buckets:
            bucket.move(diff_x, diff_y)
        self.sprite_buckets.overbucket.move(diff_x, diff_y)
        self.strikeline.move(diff_x, diff_y)

    @property
    def pixel_offset(self):
        # TODO: Replace with better pixel_offset calculation
        return self._pixel_offset

    def draw(self):
        _cam = arcade.get_window().current_camera
        self.camera.use()
        arcade.draw_lrtb_rectangle_filled(self.x, self.x + self.w,
                                          self.y + self.h, self.y,
                                          self.color)
        self.strikeline.draw()
        vp = arcade.get_viewport()
        height = vp[3] - vp[2]
        arcade.set_viewport(
            0,
            Settings.width,
            self.pixel_offset,
            self.pixel_offset + height
        )
        self.sprite_buckets.draw(self.song_time)
        _cam.use()

    def lane_x(self, lane_num):
        if lane_num == 7:  # tap note override
            return self.x
        return (self.note_size + self.gap) * lane_num + self.x

    @property
    def show_flags(self) -> bool:
        return self._show_flags

    @show_flags.setter
    def show_flags(self, v: bool):
        self._show_flags = v
        if self._show_flags:
            for sprite in self.sprite_buckets.sprites:
                if sprite.note.lane in [5, 6]:
                    sprite.alpha = 255
        else:
            for sprite in self.sprite_buckets.sprites:
                if sprite.note.lane in [5, 6]:
                    sprite.alpha = 0