from dataclasses import dataclass
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


class FNFNote(arcade.Sprite):
    def __init__(self, note: Note, height: 128, *args, **kwargs):
        self.note = note
        self.time = note.time
        self.lane = note.lane
        self.hit = note.hit
        self.hit_time = note.hit_time
        self.missed = note.missed
        try:
            icon = f"{self.note.type}-{wordmap[self.note.lane]}"
            self.icon = img_from_resource(fnfskin, f"{icon}.png")
            whratio = self.icon.width / self.icon.height
            self.icon = self.icon.resize((int(height * whratio), height), PIL.Image.LANCZOS)
        except Exception:
            self.icon = generate_missing_texture_image(height, height)

        tex = arcade.Texture(f"_fnf_note_{icon}", image=self.icon, hit_box_algorithm=None)
        super().__init__(texture=tex, *args, **kwargs)


class FNFChart(Chart):
    def __init__(self, difficulty: str, instrument: str, notespeed: float = 1) -> None:
        self.notespeed = notespeed
        super().__init__("fnf", difficulty, instrument, 4)


class FNFSong(Song):
    @classmethod
    def parse(cls, s: str):
        j: SongFileJson = json.loads(s)
        song = j["song"]

        name = song["song"]
        logger.debug(f"Parsing {name}...")
        bpm = song["bpm"]
        speed = song["speed"]
        returnsong = FNFSong(name, bpm)
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

            # Actually make two charts
            sectionNotes = section["sectionNotes"]
            for note in sectionNotes:
                posms, lane, lengthms = note  # hope this never breaks lol
                pos = posms / 1000
                length = lengthms / 1000

                note_in_focused_lane = lane < 4
                note_player = focused if note_in_focused_lane else unfocused
                lanemap = [0, 1, 2, 3, 0, 1, 2, 3]
                try:
                    chart_lane = lanemap[lane]
                except IndexError:
                    logger.warn(f"Lane {lane} out of range.")

                thisnote = Note(str(uuid4()), pos, chart_lane, length)
                returnsong.charts[note_player - 1].notes.append(thisnote)
                returnsong.charts[note_player - 1].note_by_uuid[thisnote.uuid] = thisnote

                # Fake sustains (change this.)
                seconds_per_thirtysecond = seconds_per_sixteenth / 2
                if thisnote.length != 0:
                    sustainbeats = round(thisnote.length / seconds_per_thirtysecond)
                    for i in range(sustainbeats):
                        j = i + 1
                        thisnote = Note(str(uuid4()), pos + (seconds_per_thirtysecond * (i + 1)), chart_lane, 0, "sustain")
                        returnsong.charts[note_player - 1].notes.append(thisnote)
                        returnsong.charts[note_player - 1].note_by_uuid[thisnote.uuid] = thisnote

            section_start += section_length

        for c in returnsong.charts:
            c.notes.sort()
            c.active_notes = c.notes.copy()
            c.events.sort()
            logger.debug(f"Parsed chart {c.instrument} with {len(c.notes)} notes.")

        returnsong.events = songevents
        returnsong.events.sort()

        return returnsong


class FNFHighway(Highway):
    def __init__(self, chart: FNFChart, pos: tuple[int, int], size: tuple[int, int] = None, gap=5, auto=False):
        viewport = 1 / chart.notespeed
        if size is None:
            size = int(Settings.width / (1280 / 400)), Settings.height

        super().__init__(chart, pos, size, gap, viewport)

        self.auto = auto
        for note in self.notes:
            sprite = FNFNote(note, self.note_size)
            sprite.alpha = 0
            self.sprite_list.append(sprite)

        self.strikeline = arcade.SpriteList()
        for i in [0, 1, 2, 3]:
            sprite = FNFNote(Note(i, 0, i, 0), self.note_size)
            sprite.top = self.strikeline_y
            sprite.left = self.lane_x(sprite.lane)
            sprite.alpha = 64
            self.strikeline.append(sprite)

        logger.debug(f"Generated highway for chart {chart.instrument}.")

    @property
    def px_per_s(self) -> float:
        return self.note_y(1) - self.note_y(0)

    def note_visible(self, n: FNFNote):
        if self.auto:
            return self.song_time < n.time <= self.song_time + self.viewport
        return self.song_time - (self.viewport / 2) < n.time <= self.song_time + self.viewport

    def note_expired(self, n: FNFNote):
        if self.auto:
            return self.song_time > n.time
        return self.song_time - self.viewport > n.time

    @property
    def visible_notes(self):
        return [n for n in self.sprite_list if self.note_visible(n)]

    @property
    def expired_notes(self):
        return [n for n in self.sprite_list if self.note_expired(n)]

    def update(self, song_time):
        super().update(song_time)
        for n in self.visible_notes:
            n.alpha = 255
            n.top = self.note_y(n.time)
            n.left = self.lane_x(n.lane)
            if n.note.hit:
                self.sprite_list.remove(n)
        for n in self.expired_notes:
            self.sprite_list.remove(n)

    def draw(self):
        # prev_camera = arcade.get_window().current_camera
        # self.camera.use()

        self.strikeline.draw()
        self.sprite_list.draw()

        # prev_camera.use()


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
        self.hp = 0.5
        self.max_hp = 1

        self.latest_judgement = ""
        self.latest_judgement_time = 0

        self.current_notes: list[FNFNote] = self.chart.notes.copy()
        self.current_events: list[DigitalKeyEvent] = []

        self.last_p1_note = None
        self.last_note_missed = False

    def process_keystate(self, key_states: KeyStates):
        last_state = self.key_state
        if self.last_p1_note in (0, 1, 2, 3) and key_states[self.last_p1_note] is False:
            self.last_p1_note = None
        # ignore spam during front/back porch
        if (self.chart_time < self.chart.notes[0].time - self.hit_window
           or self.chart_time > self.chart.notes[-1].time + self.hit_window):
            return
        if self.current_notes[0].time > self.chart_time + self.hit_window:
            return
        for n in range(len(key_states)):
            if key_states[n] is True and last_state[n] is False:
                e = DigitalKeyEvent(n, "down", self.chart_time)
                self.current_events.append(e)
            elif key_states[n] is False and last_state[n] is True:
                e = DigitalKeyEvent(n, "up", self.chart_time)
                self.current_events.append(e)
        self.key_state = key_states.copy()
        # self.calculate_score()

    def calculate_score(self):
        for note in [n for n in self.current_notes if n.type == "normal" and n.time <= self.chart_time + self.hit_window]:
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
        self.hp = clamp(self.min_hp, self.hp, self.max_hp)

    def score_note(self, note: FNFNote):
        j = self.get_note_judgement(note)
        self.score += j.score
        self.weighted_hit_notes += j.accuracy_weight
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
