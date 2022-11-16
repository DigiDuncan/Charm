from __future__ import annotations
from functools import cache

import logging
from dataclasses import dataclass
from pathlib import Path

import PIL, PIL.ImageFilter

import simfile
from simfile.sm import SMChart
from simfile.ssc import SSCChart
from simfile.notes import NoteData
from simfile.notes.group import group_notes, NoteWithTail
from simfile.timing import TimingData, BeatValue
from simfile.timing.engine import TimingEngine

import arcade
from charm.lib.charm import load_missing_texture

from charm.lib.generic.highway import Highway
from charm.lib.generic.song import Note, Chart, Song, BPMChangeEvent
from charm.lib.settings import Settings
from charm.lib.spritebucket import SpriteBucketCollection
from charm.lib.utils import img_from_resource
from charm.objects.line_renderer import NoteTrail
import charm.data.images.skins.fnf as fnfskin

logger = logging.getLogger("charm")

class NoteType:
    NORMAL = "normal"
    BOMB = "bomb"
    DEATH = "death"
    HEAL = "heal"
    CAUTION = "caution"

sm_to_fnf_name_map = {
    "TAP": NoteType.NORMAL,
    "MINE": NoteType.BOMB
}

class NoteColor:
    GREEN = arcade.color.LIME_GREEN
    RED = arcade.color.RED
    PINK = arcade.color.PINK
    BLUE = arcade.color.CYAN
    BOMB = arcade.color.DARK_RED
    DEATH = arcade.color.BLACK
    HEAL = arcade.color.WHITE
    CAUTION = arcade.color.YELLOW

    @classmethod
    def from_note(cls, note: "FourKeyNote"):
        match note.type:
            case NoteType.NORMAL:
                if note.lane == 0:
                    return cls.PINK
                elif note.lane == 1:
                    return cls.BLUE
                elif note.lane == 2:
                    return cls.GREEN
                elif note.lane == 3:
                    return cls.RED
            case NoteType.BOMB:
                return cls.BOMB
            case NoteType.DEATH:
                return cls.DEATH
            case NoteType.HEAL:
                return cls.HEAL
            case NoteType.CAUTION:
                return cls.CAUTION
            case _:
                return arcade.color.BLACK

@cache
def load_note_texture(note_type, note_lane, height):
    image_name = f"{note_type}-{note_lane + 1}"
    try:
        image = img_from_resource(fnfskin, image_name + ".png")
        if image.height != height:
            width = int((height / image.height) * image.width)
            image = image.resize((width, height), PIL.Image.LANCZOS)
    except Exception:
        logger.error(f"Unable to load texture: {image_name}")
        return load_missing_texture(height, height)
    return arcade.Texture(f"_fnfnote_{image_name}", image=image, hit_box_algorithm=None)

@dataclass
class FourKeyNote(Note):
    parent: FourKeyNote = None
    sprite: "FourKeyNoteSprite" | "FourKeyLongNoteSprite" = None

    def __lt__(self, other):
        return (self.time, self.lane, self.type) < (other.time, other.lane, other.type)

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
        files = folder.glob("*.ssc") or folder.glob("*.sm")
        sm_file = next(files)
        with open(sm_file, "r") as f:
            sm = simfile.load(f)

        song = FourKeySong(folder.stem)

        charts: dict[str, FourKeyChart] = {}

        for c in sm.charts:
            c: SMChart | SSCChart = c
            chart = FourKeyChart(song, c.difficulty, None)
            charts[c.difficulty] = chart

            # Use simfile to make our life so much easier.
            notedata = NoteData(c)
            grouped_notes = group_notes(notedata, join_heads_to_tails = True)
            timing = TimingData(sm, c)
            timing_engine = TimingEngine(timing)

            for notes in grouped_notes:
                note = notes[0]
                time = timing_engine.time_at(note.beat)
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

class FourKeyNoteSprite(arcade.Sprite):
    def __init__(self, note: FourKeyNote, highway: FourKeyHighway, height = 128, *args, **kwargs):
        self.note: FourKeyNote = note
        self.note.sprite = self
        self.highway: FourKeyHighway = highway
        tex = load_note_texture(note.type, note.lane, height)
        super().__init__(texture=tex, *args, **kwargs)
        if self.note.type == "sustain":
            self.alpha = 0

    def __lt__(self, other: FourKeyNoteSprite):
        return self.note.time < other.note.time

    def update_animation(self, delta_time: float):
        if self.highway.auto:
            if self.highway.song_time >= self.note.time:
                self.note.hit = True
        # if self.note.hit and self.highway.song_time >= self.note.time:
        #     self.alpha = 0
        if self.note.hit:
            self.alpha = 0


class FourKeyLongNoteSprite(FourKeyNoteSprite):
    id = 0
    def __init__(self, note: FourKeyNote, highway: FourKeyHighway, height=128, *args, **kwargs):
        super().__init__(note, highway, height, *args, **kwargs)
        self.id += 1
        self.dead = False

        color = NoteColor.from_note(self.note)
        self.trail = NoteTrail(self.id, self.position, self.note.time, self.note.length, self.highway.px_per_s,
        color, width = self.highway.note_size, upscroll = True, fill_color = color + (60,), resolution = 100)
        self.dead_trail = NoteTrail(self.id, self.position, self.note.time, self.note.length, self.highway.px_per_s,
        arcade.color.GRAY, width = self.highway.note_size, upscroll = True, fill_color = arcade.color.GRAY + (60,), resolution = 100)

    def update_animation(self, delta_time: float):
        self.trail.set_position(*self.position)
        self.dead_trail.set_position(*self.position)
        return super().update_animation(delta_time)

    def draw_trail(self):
        self.dead_trail.draw() if self.dead else self.trail.draw()


class FourKeyHighway(Highway):
    def __init__(self, chart: FourKeyChart, pos: tuple[int, int], size: tuple[int, int] = None, gap: int = 5, auto = False):
        if size is None:
            size = int(Settings.width / (1280 / 400)), Settings.height

        super().__init__(chart, pos, size, gap)

        self.viewport = 1  # TODO: BPM scaling?

        self.auto = auto

        self.sprite_buckets = SpriteBucketCollection()
        for note in self.notes:
            sprite = FourKeyNoteSprite(note, self, self.note_size) if note.length == 0 else FourKeyLongNoteSprite(note, self, self.note_size)
            sprite.top = self.note_y(note.time)
            sprite.left = self.lane_x(note.lane)
            note.sprite = sprite
            self.sprite_buckets.append(sprite, note.time, note.length)
        print(len([s for s in self.sprite_buckets.sprites if isinstance(s, FourKeyLongNoteSprite)]))

        self.strikeline = arcade.SpriteList()
        for i in [0, 1, 2, 3]:
            sprite = FourKeyNoteSprite(FourKeyNote(self.chart, 0, i, 0), self, self.note_size)
            sprite.top = self.strikeline_y
            sprite.left = self.lane_x(sprite.note.lane)
            sprite.alpha = 64
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
    def pixel_offset(self):
        # TODO: Replace with better pixel_offset calculation
        return self._pixel_offset

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

    def draw(self):
        _cam = arcade.get_window().current_camera
        self.camera.use()
        arcade.draw_lrtb_rectangle_filled(self.x, self.x + self.w,
                                          self.y + self.h, self.y,
                                          (0, 0, 0, 128))
        self.strikeline.draw()
        vp = arcade.get_viewport()
        height = vp[3] - vp[2]
        arcade.set_viewport(
            0,
            Settings.width,
            -self.pixel_offset,
            -self.pixel_offset + height
        )
        # This is slow, don't loop over things.
        b = self.sprite_buckets.calc_bucket(self.song_time)
        for bucket in self.sprite_buckets.buckets[b:b+2] + [self.sprite_buckets.overbucket]:
            for note in bucket.sprite_list:
                if isinstance(note, FourKeyLongNoteSprite) and note.note.time < self.song_time + self.viewport:
                    note.draw_trail()
        self.sprite_buckets.draw(self.song_time)
        _cam.use()