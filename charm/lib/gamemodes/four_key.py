from pathlib import Path

import simfile
from simfile.sm import SMChart
from simfile.ssc import SSCChart
from simfile.notes import NoteData
from simfile.notes.group import group_notes, NoteWithTail
from simfile.notes.timed import time_notes
from simfile.timing import TimingData
from simfile.timing.engine import TimingEngine

from charm.lib.generic.song import Note, Chart, Song, BPMChangeEvent

class FourKeyChart(Chart):
    def __init__(self, song: 'Song', difficulty, hash: str):
        super().__init__(song, "4k", difficulty, "4k", 4, hash)
        self.song: FourKeySong = song

class FourKeySong(Song):
    def __init__(self, name: str):
        super().__init__(name)

    @classmethod
    def parse(cls, folder: Path) -> "FourKeySong":
        # OK, figure out what chart file to use.
        files = folder.glob("*.sm") or folder.glob("*.ssc")
        sm_file = next(files)
        with open(sm_file, "r") as f:
            sm = simfile.load(f)

        song = FourKeySong(folder.stem)

        charts: dict[str, FourKeyChart] = {}

        for c in sm.charts:
            c: SMChart | SSCChart = c
            chart = FourKeyChart(song, c.difficulty, None)
            charts[c.difficulty] = chart
            notedata = NoteData(c)
            grouped_notes = group_notes(notedata)
            timing = TimingData(sm, c)
            timing_engine = TimingEngine(timing)

            for notes in grouped_notes:
                note = notes[0]
                time = timing_engine.time_at(note.beat)
                if isinstance(note, NoteWithTail):
                    end_time = timing_engine.time_at(note.tail_beat)
                    chart.notes.append(Note(chart, time, note.column, end_time - time, note.note_type.name))
                else:
                    chart.notes.append(Note(chart, time, note.column, 0, note.note_type.name))

            for event in c.bpms:
                