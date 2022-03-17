import json
import logging
import math
from dataclasses import dataclass
from hashlib import sha1
from pathlib import Path
from typing import Optional, TypedDict

import arcade
import PIL, PIL.ImageFilter  # noqa

import charm.data.images.skins.fnf as fnfskin
from charm.lib.anim import bounce
from charm.lib.charm import generate_missing_texture_image
from charm.lib.errors import NoChartsError, UnknownLanesError
from charm.lib.generic.engine import DigitalKeyEvent, Engine, Judgement, KeyStates
from charm.lib.generic.highway import Highway
from charm.lib.generic.song import BPMChangeEvent, Chart, Event, Milliseconds, Note, Seconds, Song
from charm.lib.paths import modsfolder, songspath
from charm.lib.settings import Settings
from charm.lib.utils import clamp, img_from_resource

logger = logging.getLogger("charm")


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
    sectionNotes: list[tuple[Milliseconds, int, Milliseconds]]
    lengthInSteps: int


class NoteType(str):
    NORMAL = "normal"
    BOMB = "bomb"
    DEATH = "death"
    HEAL = "heal"
    CAUTION = "caution"


@dataclass
class CameraFocusEvent(Event):
    focused_player: int


class FNFNote(Note):
    @property
    def image_name(self) -> str:
        return f"{self.type}-{self.lane + 1}"

    def __lt__(self, other):
        return (self.time, self.lane, self.type) < (other.time, other.lane, other.type)


class FNFJudgement(Judgement):
    @property
    def image_name(self) -> str:
        return f"judge-{self.name}"


class FNFChart(Chart):
    def __init__(self, song: 'FNFSong', difficulty: str, player: int, speed: float, hash: str):
        super().__init__(song, "fnf", difficulty, f"player{player}", 4, hash)
        self.player1 = "bf"
        self.player2 = "dad"
        self.spectator = "gf"
        self.stage = "stage"
        self.notespeed = speed
        self.hash = hash

        self.notes: list[FNFNote] = []


class FNFMod:
    def __init__(self, folder_name: str) -> None:
        self.folder_name = folder_name
        self.path = modsfolder / self.folder_name
        self.name: str = None
        self.songs = list[FNFSong]


class FNFSong(Song):
    def __init__(self, song_code: str, mod: FNFMod = None) -> None:
        super().__init__(song_code)
        self.mod: FNFMod = mod

    @classmethod
    def parse(cls, folder: str, mod: FNFMod = None):
        song = FNFSong(folder)
        song.path = songspath / "fnf" / folder
        if mod:
            song.mod = mod
            song.path = mod.path / folder

        charts = song.path.glob("*.json")
        parsed_charts = [cls.parse_chart(chart, song) for chart in charts]
        for charts in parsed_charts:
            for chart in charts:
                song.charts.append(chart)

        if not song.charts:
            raise NoChartsError(folder)

        # Global attributes that are stored per-chart, for some reason.
        chart: FNFChart = song.charts[0]
        song.bpm = chart.bpm
        song.metadata["title"] = chart.name

        return song

    @classmethod
    def parse_chart(cls, file_path: Path, song: 'FNFSong') -> list[FNFChart]:
        with open(file_path) as p:
            j: SongFileJson = json.load(p)
        hash = sha1(bytes(json.dumps(j), encoding='utf-8')).hexdigest()
        difficulty = file_path.stem.rsplit("-", 1)[1] if "-" in file_path.stem else "normal"
        songdata = j["song"]

        name = songdata["song"].replace("-", " ").title()
        logger.debug(f"Parsing {name}...")
        bpm = songdata["bpm"]
        speed = songdata["speed"]
        charts = [
            FNFChart(song, difficulty, 1, speed, hash),
            FNFChart(song, difficulty, 2, speed, hash)]

        for chart in charts:
            chart.name = songdata["song"]
            chart.bpm = bpm
            chart.player1 = songdata.get("player1", "bf")
            chart.player2 = songdata.get("player2", "dad")
            chart.spectator = songdata.get("player3", "gf")
            chart.stage = songdata.get("stage", "stage")

        sections = songdata["song"]

        last_bpm = bpm
        last_focus: Optional[int] = None
        section_start = 0.0
        events: list[Event] = []
        sections = songdata["notes"]
        section_starts = []
        unknown_lanes = []

        # hardcode_search = (h for h in hardcodes if h.hash == returnsong.hash)
        # hardcode = next(hardcode_search, None)

        # if hardcode:
        #     returnsong.metadata["artist"] = hardcode.author
        #     returnsong.metadata["album"] = hardcode.mod_name

        for section in sections:
            # There's a changeBPM event but like, it always has to be paired
            # with a bpm, so it's pointless anyway
            if "bpm" in section:
                new_bpm = section["bpm"]
                if new_bpm != last_bpm:
                    events.append(BPMChangeEvent(section_start, new_bpm))
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
                focused, unfocused = 0, 1
            else:
                focused, unfocused = 1, 0

            if focused != last_focus:
                events.append(CameraFocusEvent(section_start, focused))
                last_focus = focused

            # Lanemap: (player, lane, type)
            # TODO: overrides for this
            lanemap: list[tuple[int, int, NoteType]] = [(0, 0, NoteType.NORMAL), (0, 1, NoteType.NORMAL), (0, 2, NoteType.NORMAL), (0, 3, NoteType.NORMAL),
                                                        (1, 0, NoteType.NORMAL), (1, 1, NoteType.NORMAL), (1, 2, NoteType.NORMAL), (1, 3, NoteType.NORMAL)]

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
                    continue

                note_player = focused if note_data[0] == 0 else unfocused
                chart_lane = note_data[1]
                note_type = note_data[2]

                thisnote = FNFNote(charts[note_player], pos, chart_lane, length, type = note_type)
                thisnote.extra_data = extra
                charts[note_player].notes.append(thisnote)

                # TODO: Fake sustains (change this?)
                if thisnote.length != 0:
                    sustainbeats = round(thisnote.length / seconds_per_sixteenth)
                    for i in range(sustainbeats):
                        j = i + 1
                        thatnote = FNFNote(charts[note_player], pos + (seconds_per_sixteenth * (i + 1)), chart_lane, 0, "sustain", thisnote)
                        charts[note_player].notes.append(thatnote)

            section_start += section_length

        for c in charts:
            c.events = events
            c.notes.sort()
            c.events.sort()
            logger.debug(f"Parsed chart {c.instrument} with {len(c.notes)} notes.")

        unknown_lanes = sorted(set(unknown_lanes))
        if unknown_lanes:
            raise UnknownLanesError(f"Unknown lanes found in chart {name}: {unknown_lanes}")

        return charts


class FNFEngine(Engine):
    def __init__(self, chart: Chart, offset: Seconds = -0.075):  # FNF defaults to a 75ms input offset.
        hit_window = 0.166
        mapping = [arcade.key.D, arcade.key.F, arcade.key.J, arcade.key.K]
        judgements = [
            #           ("name",  ms,       score, acc,  hp = 0)
            FNFJudgement("sick",  45,       350,   1,    0.04),
            FNFJudgement("good",  90,       200,   0.75),
            FNFJudgement("bad",   135,      100,   0.5,  -0.03),
            FNFJudgement("awful", 166,      50,    -1,   -0.06),  # I'm not calling this "s***", it's not funny.
            FNFJudgement("miss",  math.inf, 0,     -1,   -0.1)
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
        self.all_judgements: list[tuple[Seconds, Seconds, Judgement]] = []

        self.current_notes: list[FNFNote] = self.chart.notes.copy()
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
        # Get all non-scored notes within the current window
        for note in [n for n in self.current_notes if n.type != "sustain" and n.time <= self.chart_time + self.hit_window]:
            # Missed notes (current time is higher than max allowed time for note)
            if self.chart_time > note.time + self.hit_window:
                note.missed = True
                note.hit_time = math.inf  # how smart is this? :thinking:
                self.score_note(note)
                self.current_notes.remove(note)
            else:
                if note.type == "sustain":
                    if self.key_state[note.lane]:
                        note.hit = True
                        note.hit_time = note.time
                        self.score_note(note)
                        self.current_notes.remove(note)
                # Check non-used events to see if one matches our note
                for event in [e for e in self.current_events if e.new_state == "down"]:
                    # We've determined the note was hit
                    if event.key == note.lane and abs(event.time - note.time) <= self.hit_window:
                        note.hit = True
                        note.hit_time = event.time
                        self.score_note(note)
                        self.current_notes.remove(note)
                        self.current_events.remove(event)
                        break

        # Make sure we can't go below min_hp or above max_hp
        self.hp = clamp(self.min_hp, self.hp, self.max_hp)
        if self.hp == self.min_hp:
            self.has_died = True

    def score_note(self, note: FNFNote):
        # Ignore notes we haven't done anything with yet
        if not (note.hit or note.missed):
            return

        # Sustains use different scoring
        if note.type == "sustain":
            self.last_p1_note = note.lane
            if note.hit:
                self.hp += 0.02
                self.last_note_missed = False
            elif note.missed:
                self.hp -= 0.05
                self.last_note_missed = True
            return

        # Death notes set HP to minimum when hit
        if note.type == "death":
            if note.hit:
                self.hp = self.min_hp
            return

        # Bomb notes penalize HP when hit
        if note.type == "bomb":
            if note.hit:
                self.hp -= self.bomb_hp
            return

        # Score the note
        j = self.get_note_judgement(note)
        self.score += j.score
        self.weighted_hit_notes += j.accuracy_weight

        # Give HP for hit note (heal notes give more)
        if note.type == "heal":
            self.hp += self.heal_hp
        else:
            self.hp += j.hp_change

        # Judge the player
        rt = abs(note.hit_time - note.time)
        self.latest_judgement = j.name
        self.latest_judgement_time = self.chart_time
        self.all_judgements.append((self.latest_judgement_time, rt, self.latest_judgement))

        # Animation and hit/miss tracking
        self.last_p1_note = note.lane
        if note.hit:
            self.hits += 1
            self.last_note_missed = False
        elif note.missed:
            self.misses += 1
            self.last_note_missed = True


class FNFNoteSprite(arcade.Sprite):
    def __init__(self, note: FNFNote, height = 128, *args, **kwargs):
        self.note = note
        try:
            self.image = img_from_resource(fnfskin, note.image_name + ".png")
            whratio = self.image.width / self.image.height
            if self.image.height != height:
                self.image = self.image.resize((int(height * whratio), height), PIL.Image.LANCZOS)
        except Exception:
            self.image = generate_missing_texture_image(height, height)
        tex = arcade.Texture(f"_fnfnote_{note.image_name}", image=self.image, hit_box_algorithm=None)
        super().__init__(texture=tex, *args, **kwargs)

    def __lt__(self, other: "FNFNoteSprite"):
        return self.note.time < other.note.time


class FNFLongNoteSprite(FNFNoteSprite):
    pass


class FNFHighway(Highway):
    def __init__(self, chart: FNFChart, pos: tuple[int, int], size: tuple[int, int] = None, gap: int = 5, auto = False):
        viewport = 1 / (chart.notespeed * 0.75)
        if size is None:
            size = int(Settings.width / (1280 / 400)), Settings.height

        super().__init__(chart, pos, size, gap, viewport)

        self.auto = auto

        for note in self.notes:
            sprite = FNFNoteSprite(note, self.note_size) if note.length == 0 else FNFLongNoteSprite(note, self.note_size)
            sprite.top = self.note_y(note.time)
            sprite.left = self.lane_x(note.lane)
            self.sprite_list.append(sprite)

        self.strikeline = arcade.SpriteList()
        for i in [0, 1, 2, 3]:
            sprite = FNFNoteSprite(FNFNote(self.chart, 0, i, 0), self.note_size)
            sprite.top = self.strikeline_y
            sprite.left = self.lane_x(sprite.note.lane)
            sprite.alpha = 64
            self.strikeline.append(sprite)

        self.last_draw_time = 0
        logger.debug(f"Generated highway for chart {chart.instrument}.")

    def update(self, song_time: float):
        super().update(song_time)
        for n in self.sprite_list:
            if n.note.hit:
                n.alpha = 0
        self.camera.scale = bounce(1, 1.05, self.chart.bpm / 2, self.song_time)

    def draw(self):
        _cam = arcade.get_window().current_camera
        self.camera.use()
        self.strikeline.draw()
        delta_draw_time = self.song_time - self.last_draw_time
        scroll = (self.px_per_s * delta_draw_time / 2)
        vp = arcade.get_viewport()
        arcade.set_viewport(
            0,
            Settings.width,
            vp[2] - scroll,
            vp[3] - scroll
        )
        self.sprite_list.draw()
        self.last_draw_time = self.song_time
        _cam.use()
