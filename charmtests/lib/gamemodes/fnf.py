from dataclasses import dataclass
import json
from typing import Literal, Optional, TypedDict

import arcade

from charmtests.lib.song import BPMChangeEvent, Chart, Event, Milliseconds, Note, Song

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


class FNFChart(Chart):
    def __init__(self, difficulty: str, instrument: str, notespeed :float = 1) -> None:
        self.notespeed = notespeed
        super().__init__("fnf", difficulty, instrument)

class FNFSong(Song):
    @classmethod
    def parse(cls, s: str):
        j: SongFileJson = json.loads(s)
        song = j["song"]

        name = song["song"]
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
                chart_lane = lanemap[lane]

                returnsong.charts[note_player - 1].notes.append(Note(pos, chart_lane, length))

            # Since in theory you can have events in these sections
            # without there being notes there, I need to calculate where this
            # section occurs from scratch, and some engines have a startTime
            # thing here but I can't guarantee it so it's basically pointless
            seconds_per_beat = 60 / bpm
            seconds_per_measure = seconds_per_beat * 4
            seconds_per_sixteenth = seconds_per_measure / 16
            section_length = section["lengthInSteps"] * seconds_per_sixteenth
            section_start += section_length

        for c in returnsong.charts:
            c.notes.sort()
            c.active_notes = c.notes.copy()
            c.events.sort()

        return returnsong
