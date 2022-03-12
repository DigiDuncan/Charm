from dataclasses import dataclass
from hashlib import sha1
import json
import logging
import math
from typing import Literal, Optional, TypedDict
from uuid import uuid4

import arcade
import PIL.Image

from charm.lib.charm import generate_missing_texture_image
from charm.lib.generic.engine import DigitalKeyEvent, Engine, Judgement, KeyStates
from charm.lib.generic.highway import Highway
from charm.lib.generic.song import BPMChangeEvent, Chart, Event, Milliseconds, Note, Seconds, Song
from charm.lib.settings import Settings
from charm.lib.utils import clamp, img_from_resource

import charm.data.images.skins.fnf as fnfskin

logger = logging.getLogger("charm")
hashes = {}

PlayerNum = Literal[1, 2]
JsonLaneNum = Literal[0, 1, 2, 3, 4, 5, 6, 7]

colormap = {
    0: arcade.color.MAGENTA + (0xFF,),
    1: arcade.color.CYAN + (0xFF,),
    2: arcade.color.GREEN + (0xFF,),
    3: arcade.color.RED + (0xFF,)
}

altcolormap = {
    0: arcade.color.DARK_MAGENTA + (0xFF,),
    1: arcade.color.DARK_CYAN + (0xFF,),
    2: arcade.color.DARK_GREEN + (0xFF,),
    3: arcade.color.DARK_RED + (0xFF,)
}

wordmap = {
    0: "left",
    1: "down",
    2: "up",
    3: "right"
}


class SongFileJson(TypedDict):
    song: "SongJson"


class SongJson(TypedDict):
    song: str
    bpm: float
    speed: float
    notes: list["NoteJson"]


class NoteJson(TypedDict):
    bpm: float
    mustHitSection: bool
    sectionNotes: list[tuple[Milliseconds, JsonLaneNum, Milliseconds]]
    lengthInSteps: int


@dataclass
class CameraFocusEvent(Event):
    focused_player: int

    @property
    def icon(self) -> str:
        return f"cam_p{self.focused_player}"


class FNFHardcode:
    def __init__(self, hash: str, mod_name: str, author: str, lanemap: list[tuple[int, int, str]] = None):
        self.hash = hash
        self.mod_name = mod_name
        self.author = author
        self.lanemap = lanemap if lanemap is not None else [(0, 0, "normal"), (0, 1, "normal"), (0, 2, "normal"), (0, 3, "normal"),
                                                            (1, 0, "normal"), (1, 1, "normal"), (1, 2, "normal"), (1, 3, "normal")]


hardcodes = [
    FNFHardcode("09959de9dca4800df18e74108c1d8a36940be6eb", "Vs. Tricky", "Banbuds",  # madness
    [(0, 0, "normal"), (0, 1, "normal"), (0, 2, "normal"), (0, 3, "normal"),
     (1, 0, "normal"), (1, 1, "normal"), (1, 2, "normal"), (1, 3, "normal"),
     (0, 0, "bomb"), (0, 1, "bomb"), (0, 2, "bomb"), (0, 3, "bomb"),
     (1, 0, "bomb"), (1, 1, "bomb"), (1, 2, "bomb"), (1, 3, "bomb")]),
    FNFHardcode("3a1f66a3d87637dfeaa2c8a44e6b4946b5013c94", "Vs. Tricky", "Banbuds",  # hellclown
    [(0, 0, "normal"), (0, 1, "normal"), (0, 2, "normal"), (0, 3, "normal"),
     (1, 0, "normal"), (1, 1, "normal"), (1, 2, "normal"), (1, 3, "normal"),
     (0, 0, "bomb"), (0, 1, "bomb"), (0, 2, "bomb"), (0, 3, "bomb"),
     (1, 0, "bomb"), (1, 1, "bomb"), (1, 2, "bomb"), (1, 3, "bomb")]),
    FNFHardcode("7113289f3f65068d67db58c11756271f5792ae28", "Vs. Tricky", "Banbuds",  # expurgation
    [(0, 0, "normal"), (0, 1, "normal"), (0, 2, "normal"), (0, 3, "normal"),
     (1, 0, "normal"), (1, 1, "normal"), (1, 2, "normal"), (1, 3, "normal"),
     (0, 0, "death"), (0, 1, "death"), (0, 2, "death"), (0, 3, "death"),
     (1, 0, "death"), (1, 1, "death"), (1, 2, "death"), (1, 3, "death")])
]


class FNFNoteSprite(arcade.Sprite):
    def __init__(self, note: Note, height: 128, *args, **kwargs):
        self.note = note
        self.time = note.time
        self.type = note.type
        self.lane = note.lane
        self.hit = note.hit
        self.hit_time = note.hit_time
        self.missed = note.missed
        icon = f"{self.note.type}-{wordmap[self.note.lane]}"
        try:
            self.icon = img_from_resource(fnfskin, f"{icon}.png")
            whratio = self.icon.width / self.icon.height
            if self.icon.height != height:
                self.icon = self.icon.resize((int(height * whratio), height), PIL.Image.LANCZOS)
        except Exception:
            self.icon = generate_missing_texture_image(height, height)

        if self.type == "sustain":
            full_height = self.icon.height
            self.icon = self.icon.crop((0, 0, self.icon.width, 1))

        tex = arcade.Texture(f"_fnf_note_{icon}", image=self.icon, hit_box_algorithm=None)
        super().__init__(texture=tex, *args, **kwargs)

        if self.type == "sustain":
            self.height = full_height

    def __lt__(self, other):
        return (self.time, self.lane, self.type) < (other.time, other.lane, other.type)


class FNFChart(Chart):
    def __init__(self, difficulty: str, instrument: str, notespeed: float = 1) -> None:
        self.notespeed = notespeed
        super().__init__("fnf", difficulty, instrument, 4)


class FNFSong(Song):
    def __init__(self, name: str, bpm: float) -> None:
        self.key: str = None
        self.player2: str = None
        super().__init__(name, bpm)

    @classmethod
    def simple_parse(cls, k: str, s: str):
        j: SongFileJson = json.loads(s)
        hash = sha1(bytes(json.dumps(j), encoding='utf-8')).hexdigest()
        song = j["song"]
        title = song["song"].replace("-", " ").title()
        hardcode_search = (h for h in hardcodes if h.hash == hash)
        hardcode = next(hardcode_search, None)
        artist = "Unknown Artist" if not hardcode else hardcode.author
        album = "Unknown Album" if not hardcode else hardcode.mod_name

        hashes[k] = hash

        return {
            "title": title,
            "artist": artist,
            "album": album,
            "hash": hash,
            "key": k
        }

    @classmethod
    def parse(cls, k: str, s: str):
        j: SongFileJson = json.loads(s)
        hash = sha1(bytes(json.dumps(j), encoding='utf-8')).hexdigest()
        song = j["song"]

        name = song["song"].replace("-", " ").title()
        logger.debug(f"Parsing {name}...")
        bpm = song["bpm"]
        speed = song["speed"]
        player2 = song["player2"]
        returnsong = FNFSong(name, bpm)
        returnsong.key = k
        returnsong.player2 = player2
        returnsong.hash = hash
        returnsong.charts = [
            FNFChart("hard", "player1", speed),
            FNFChart("hard", "player2", speed)]

        sections = song["song"]

        last_bpm = bpm
        last_focus: Optional[PlayerNum] = None
        section_start = 0.0
        songevents: list[Event] = []
        sections = song["notes"]
        section_starts = []
        unknown_lanes = []

        hardcode_search = (h for h in hardcodes if h.hash == returnsong.hash)
        hardcode = next(hardcode_search, None)

        if hardcode:
            returnsong.metadata["artist"] = hardcode.author
            returnsong.metadata["album"] = hardcode.mod_name

        for section in sections:
            # There's a changeBPM event but like, it always has to be paired
            # with a bpm, so it's pointless anyway
            if "bpm" in section:
                new_bpm = section["bpm"]
                if new_bpm != last_bpm:
                    songevents.append(BPMChangeEvent(section_start, new_bpm))
                    last_bpm = new_bpm
            section_starts.append((section_start, bpm))

            # Since in theory you can have events in these sections
            # without there being notes there, I need to calculate where this
            # section occurs from scratch, and some engines have a startTime
            # thing here but I can't guarantee it so it's basically pointless
            seconds_per_beat = 60 / bpm
            seconds_per_measure = seconds_per_beat * 4
            seconds_per_sixteenth = seconds_per_measure / 16
            section_length = section["lengthInSteps"] * seconds_per_sixteenth

            # Create a camera focus event like they should have in the first place
            if section["mustHitSection"]:
                focused, unfocused = 1, 2
            else:
                focused, unfocused = 2, 1

            if focused != last_focus:
                songevents.append(CameraFocusEvent(section_start, focused))
                last_focus = focused

            if hardcode:
                lanemap = hardcode.lanemap
            else:
                lanemap = [(0, 0, "normal"), (0, 1, "normal"), (0, 2, "normal"), (0, 3, "normal"),
                           (1, 0, "normal"), (1, 1, "normal"), (1, 2, "normal"), (1, 3, "normal")]

            # Actually make two charts
            sectionNotes = section["sectionNotes"]
            for note in sectionNotes:
                extra = None
                if len(note) > 3:
                    extra = note[3:]
                    note = note[:3]
                posms, lane, lengthms = note  # hope this never breaks lol
                pos = posms / 1000
                length = lengthms / 1000

                try:
                    note_data = lanemap[lane]
                except IndexError:
                    unknown_lanes.append(lane)

                note_player = focused if note_data[0] == 0 else unfocused
                chart_lane = note_data[1]
                note_type = note_data[2]

                thisnote = Note(str(uuid4()), pos, chart_lane, length, type = note_type)
                thisnote.extra_data = extra
                returnsong.charts[note_player - 1].notes.append(thisnote)
                returnsong.charts[note_player - 1].note_by_uuid[thisnote.uuid] = thisnote

                # TODO: Fake sustains (change this.)
                seconds_per_thirtysecond = seconds_per_sixteenth / 2
                if thisnote.length != 0:
                    sustainbeats = round(thisnote.length / seconds_per_thirtysecond)
                    for i in range(sustainbeats):
                        j = i + 1
                        thatnote = Note(str(uuid4()), pos + (seconds_per_thirtysecond * (i + 1)), chart_lane, 0, "sustain", thisnote)
                        returnsong.charts[note_player - 1].notes.append(thatnote)
                        returnsong.charts[note_player - 1].note_by_uuid[thatnote.uuid] = thatnote

            section_start += section_length

        for c in returnsong.charts:
            c.notes.sort()
            c.active_notes = c.notes.copy()
            c.events.sort()
            logger.debug(f"Parsed chart {c.instrument} with {len(c.notes)} notes.")

        returnsong.events = songevents
        returnsong.events.sort()

        unknown_lanes = sorted(set(unknown_lanes))
        if unknown_lanes:
            logger.warn(f"Unknown lanes {unknown_lanes}")

        return returnsong


class FNFHighway(Highway):
    def __init__(self, chart: FNFChart, pos: tuple[int, int], size: tuple[int, int] = None, gap=5, auto=False):
        viewport = 1 / (chart.notespeed * 0.75)
        if size is None:
            size = int(Settings.width / (1280 / 400)), Settings.height

        super().__init__(chart, pos, size, gap, viewport)

        self.auto = auto

        sprites = []
        for note in self.notes:
            sprite = FNFNoteSprite(note, self.note_size)
            sprite.top = self.note_y(note.time)
            sprite.left = self.lane_x(sprite.lane)
            sprites.append(sprite)
        sprites = [s for s in sprites if s.type == "sustain"] + [s for s in sprites if s.type != "sustain"][::-1]
        for s in sprites:
            self.sprite_list.append(s)

        self.strikeline = arcade.SpriteList()
        for i in [0, 1, 2, 3]:
            sprite = FNFNoteSprite(Note(i, 0, i, 0), self.note_size)
            sprite.top = self.strikeline_y
            sprite.left = self.lane_x(sprite.lane)
            sprite.alpha = 64
            self.strikeline.append(sprite)

        logger.debug(f"Generated highway for chart {chart.instrument}.")

    def note_visible(self, n: FNFNoteSprite):
        if self.auto:
            return self.song_time < n.time <= self.song_time + self.viewport
        return self.song_time - (self.viewport / 2) < n.time <= self.song_time + self.viewport

    def note_expired(self, n: FNFNoteSprite):
        if self.auto:
            return self.song_time > n.time
        return self.song_time - self.viewport > n.time

    @property
    def visible_notes(self) -> list[FNFNoteSprite]:
        return [n for n in self.sprite_list if self.note_visible(n)]

    @property
    def expired_notes(self) -> list[FNFNoteSprite]:
        return [n for n in self.sprite_list if self.note_expired(n)]

    def update(self, song_time):
        super().update(song_time)
        for n in self.visible_notes:
            if n.note.hit and n.note.type != "sustain":
                n.alpha = 0
            if n.note.hit and n.note.type == "sustain" and song_time >= n.time:
                n.alpha = 0
        for n in self.expired_notes:
            n.alpha = 0

    def draw(self):
        self.strikeline.draw()
        scroll = (self.px_per_s * self.song_time)
        arcade.set_viewport(
            0,
            Settings.width,
            0 - scroll,
            Settings.height - scroll
        )
        self.sprite_list.draw()
        arcade.get_window().current_camera.use()


class FNFEngine(Engine):
    def __init__(self, chart: Chart, offset: Seconds = -0.075):  # FNF defaults to a 75ms input offset.
        hit_window = 0.166
        mapping = [arcade.key.D, arcade.key.F, arcade.key.J, arcade.key.K]
        judgements = [
            #        ("name",  ms,       score, acc,  hp = 0)
            Judgement("sick",  45,       350,   1,    0.04),
            Judgement("good",  90,       200,   0.75),
            Judgement("bad",   135,      100,   0.5,  -0.03),
            Judgement("awful", 166,      50,    -1,   -0.06),  # I'm not calling this "s***", it's not funny.
            Judgement("miss",  math.inf, 0,     -1,   -0.1)
        ]
        super().__init__(chart, mapping, hit_window, judgements, offset)

        self.min_hp = 0
        self.hp = 1
        self.max_hp = 2
        self.bomb_hp = 0.5
        self.heal_hp = 0.5

        self.has_died = False

        self.latest_judgement = ""
        self.latest_judgement_time = 0

        self.current_notes: list[FNFNoteSprite] = self.chart.notes.copy()
        self.current_events: list[DigitalKeyEvent] = []

        self.last_p1_note = None
        self.last_note_missed = False

    def process_keystate(self, key_states: KeyStates):
        last_state = self.key_state
        if self.last_p1_note in (0, 1, 2, 3) and key_states[self.last_p1_note] is False:
            self.last_p1_note = None  # should set BF to idle?
        # ignore spam during front/back porch
        if (self.chart_time < self.chart.notes[0].time - self.hit_window
           or self.chart_time > self.chart.notes[-1].time + self.hit_window):
            return
        for n in range(len(key_states)):
            if key_states[n] is True and last_state[n] is False:
                e = DigitalKeyEvent(self.chart_time, n, "down")
                self.current_events.append(e)
            elif key_states[n] is False and last_state[n] is True:
                e = DigitalKeyEvent(self.chart_time, n, "up")
                self.current_events.append(e)
        self.key_state = key_states.copy()

    def calculate_score(self):
        for note in [n for n in self.current_notes if n.type != "sustain" and n.time <= self.chart_time + self.hit_window]:
            if self.chart_time > note.time + self.hit_window:
                note.missed = True
                note.hit_time = math.inf  # how smart is this? :thinking:
                self.score_note(note)
                self.current_notes.remove(note)
            else:
                for event in [e for e in self.current_events if e.new_state == "down"]:
                    if event.key == note.lane and abs(event.time - note.time) <= self.hit_window:
                        note.hit = True
                        note.hit_time = event.time
                        self.score_note(note)
                        self.current_notes.remove(note)
                        self.current_events.remove(event)
                        break
        # aaaaaa do not do this loop
        for note in [n for n in self.current_notes if n.type == "sustain" and n.time <= self.chart_time + self.hit_window]:
            if self.chart_time > note.time + self.hit_window:
                note.missed = True
                note.hit_time = math.inf
                self.score_note(note)
                self.current_notes.remove(note)
            else:
                if self.key_state[note.lane] is True:
                    note.hit = True
                    note.hit_time = note.time
                    self.score_note(note)
                    self.current_notes.remove(note)
        self.hp = clamp(self.min_hp, self.hp, self.max_hp)
        if self.hp == self.min_hp:
            self.has_died = True

    def score_note(self, note: FNFNoteSprite):
        if note.type == "sustain":
            if note.hit:
                self.hp += 0.01
            elif note.missed:
                self.hp -= 0.025
            return
        if note.type == "death":
            if note.hit:
                self.hp = self.min_hp
            return
        if note.type == "bomb":
            if note.hit:
                self.hp -= self.bomb_hp
            return
        j = self.get_note_judgement(note)
        self.score += j.score
        self.weighted_hit_notes += j.accuracy_weight
        if note.type == "heal":
            self.hp += self.heal_hp
        else:
            self.hp += j.hp_change
        self.latest_judgement = j.name
        self.latest_judgement_time = self.chart_time
        if note.hit:
            self.hits += 1
            self.last_p1_note = note.lane
            self.last_note_missed = False
        elif note.missed:
            self.misses += 1
            self.last_note_missed = True
