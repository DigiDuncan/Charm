from __future__ import annotations

from hashlib import sha1
from io import StringIO
import itertools
from pathlib import Path

import simfile
from simfile.sm import SMChart
from simfile.ssc import SSCChart
from simfile.notes import NoteData
from simfile.notes.group import group_notes, NoteWithTail
from simfile.timing import TimingData, BeatValue
from simfile.timing.engine import TimingEngine

from charm.lib.errors import NoChartsError
from charm.lib.gamemodes.four_key import FourKeyChart, FourKeyEngine, FourKeyNote, FourKeySong, NoteType
from charm.lib.generic.song import BPMChangeEvent, Metadata

sm_to_fnf_name_map = {
    "TAP": NoteType.NORMAL,
    "MINE": NoteType.BOMB
}


class SMSong(FourKeySong):
    def __init__(self, path: Path):
        super().__init__(path)

        self.timing_engine: TimingEngine = None

    @classmethod
    def parse(cls, path: Path) -> SMSong:
        # OK, figure out what chart file to use.
        try:
            sm_file = next(itertools.chain(path.glob("*.ssc"), path.glob("*.sm")))
        except StopIteration as err:
            raise NoChartsError(path.stem) from err
        with sm_file.open("r") as f:
            sm = simfile.load(f)

        song = SMSong(path)

        charts: dict[str, FourKeyChart] = {}

        # THIS PARSER RELIES ON THE smfile LIBRARY (PROBABLY TOO MUCH)
        # This means I *don't know how this works*
        # The only reason SM long notes are scored right now is because smfile gives us a handy TimingEngine
        # and this is great but breaks parity with every other system we have!
        # Need to figure how to a) not use TimingEngine for SMEngine, and b) maybe not use this library at all
        # for parsing? But it's so good...

        for c in sm.charts:
            c: SMChart | SSCChart = c
            chart = FourKeyChart(song, c.difficulty, None)
            temp_file = StringIO()
            c.serialize(temp_file)
            chart.hash = sha1(bytes(temp_file.read(), encoding = "utf-8")).hexdigest()
            charts[c.difficulty] = chart

            # Use simfile to make our life so much easier.
            notedata = NoteData(c)
            grouped_notes = group_notes(notedata, join_heads_to_tails=True)
            timing = TimingData(sm, c)
            timing_engine = TimingEngine(timing)
            song.timing_engine = timing_engine

            for notes in grouped_notes:
                note = notes[0]
                time = timing_engine.time_at(note.beat)
                beat = note.beat % 1
                value = beat.denominator  # TODO: Reimplement?
                note_type = sm_to_fnf_name_map.get(note.note_type.name, None)
                if isinstance(note, NoteWithTail):
                    end_time = timing_engine.time_at(note.tail_beat)
                    chart.notes.append(FourKeyNote(chart, time, note.column, end_time - time, NoteType.NORMAL))
                else:
                    chart.notes.append(FourKeyNote(chart, time, note.column, 0, note_type))

            for bpm in timing.bpms.data:
                bpm: BeatValue = bpm
                bpm_event = BPMChangeEvent(timing_engine.time_at(bpm.beat), float(bpm.value))
                chart.events.append(bpm_event)

        song.charts.extend([v for v in charts.values()])

        return song

    @classmethod
    def get_metadata(cls, folder: Path) -> Metadata:
        # OK, figure out what chart file to use.
        files = itertools.chain(folder.glob("*.ssc"), folder.glob("*.sm"))
        sm_file = next(files)
        with open(sm_file, "r") as f:
            sm = simfile.load(f)
        title = sm.title
        artist = sm.artist
        album = sm.cdtitle
        length = sm.get("musiclength", 0)
        genre = sm.genre
        charter = sm.credit
        return Metadata(title = title, artist = artist, album = album,
                        length = length, genre = genre, charter = charter, path = folder,
                        gamemode = "4k")


class SMEngine(FourKeyEngine):
    # See the comment in SMSong.parse for why this is hacky and bad.
    def score_sustains(self):
        timing_engine: TimingEngine = self.chart.song.timing_engine
        current_beat = timing_engine.beat_at(self.chart_time)
        time_since_last_tick = self.chart_time - self.last_sustain_tick
        beats_since_last_tick = time_since_last_tick * float(timing_engine.bpm_at(current_beat) / 60)

        sixteenths = int(beats_since_last_tick * 16)
        if sixteenths < 1:
            return

        for sustain in self.active_sustains:
            if self.keystate[sustain.lane]:
                self.hp += int(self.judgements[0].hp_change / 4) * sixteenths  # TODO: Does this feel right?
                self.score += int(self.judgements[0].score / 4) * sixteenths
            else:
                self.hp -= int(self.judgements[0].hp_change / 4) * sixteenths

        self.last_sustain_tick = self.chart_time
