import json
import logging
import math
from dataclasses import dataclass
from hashlib import sha1
from pathlib import Path
from typing import Optional, TypedDict

import arcade

from charm.lib.errors import NoChartsError, UnknownLanesError
from charm.lib.generic.engine import DigitalKeyEvent, Engine, Judgement, KeyStates
from charm.lib.generic.song import BPMChangeEvent, Chart, Event, Milliseconds, Note, Seconds, Song
from charm.lib.paths import modsfolder, songspath
from charm.lib.utils import clamp

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


class NoteType:
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
    def icon(self):
        if self.is_sustain and self.type == NoteType.NORMAL:
            return f"sustain-{self.lane}"
        elif self.is_sustain:
            return f"{self.type}-sustain"
        else:
            return f"{self.type}-{self.lane}"


class FNFChart(Chart):
    def __init__(self, song: 'FNFSong', difficulty: str, player: int, speed: float, hash: str):
        super().__init__("fnf", difficulty, f"player{player}", 4)
        self.player1 = "bf"
        self.player2 = "dad"
        self.spectator = "gf"
        self.stage = "stage"
        self.notespeed = speed
        self.song = song
        self.hash = hash


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

        charts = song.path.glob(f"{folder}*.json")
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

    @classmethod
    def parse_chart(cls, file_path: Path, song: 'FNFSong') -> list[FNFChart]:
        j: SongFileJson = json.load(file_path)
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
            chart.player1 = songdata.get("player1", "bf")
            chart.player2 = songdata.get("player2", "dad")
            chart.spectator = songdata.get("player3", "gf")
            chart.stage = songdata.get("stage", "stage")

        sections = songdata["song"]

        last_bpm = bpm
        last_focus: Optional[int] = None
        section_start = 0.0
        events: list[Event] = []
        sections = song["notes"]
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
                focused, unfocused = 1, 2
            else:
                focused, unfocused = 2, 1

            if focused != last_focus:
                events.append(CameraFocusEvent(section_start, focused))
                last_focus = focused

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

                thisnote = FNFNote(pos, chart_lane, length, type = note_type)
                thisnote.extra_data = extra
                charts[note_player - 1].notes.append(thisnote)
                charts[note_player - 1].note_by_uuid[thisnote.uuid] = thisnote

                # TODO: Fake sustains (change this.)
                if thisnote.length != 0:
                    sustainbeats = round(thisnote.length / seconds_per_sixteenth)
                    for i in range(sustainbeats):
                        j = i + 1
                        thatnote = FNFNote(pos + (seconds_per_sixteenth * (i + 1)), chart_lane, 0, "sustain", thisnote)
                        charts[note_player - 1].notes.append(thatnote)
                        charts[note_player - 1].note_by_uuid[thatnote.uuid] = thatnote

            section_start += section_length

        for c in charts:
            c.events = events
            c.notes.sort()
            c.active_notes = c.notes.copy()
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
        for note in [n for n in self.current_notes if n.time <= self.chart_time + self.hit_window]:
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
        if self.hp == self.min_hp:
            self.has_died = True

    def score_note(self, note: FNFNote):
        if note.type == "sustain":
            if note.hit:
                self.hp += 0.02
            elif note.missed:
                self.hp -= 0.05
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
