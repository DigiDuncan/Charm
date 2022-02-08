import io
import logging
import string
import requests

import arcade
from arcade import Sprite, generate_uuid_from_kwargs
import PIL.Image

from charm.lib.anim import ease_circout
from charm.lib.charm import CharmColors
from charm.lib.settings import Settings
from charm.lib.utils import clamp
from charm.objects.song import Song

logger = logging.getLogger("charm")


class SongMenuItem(Sprite):
    def __init__(self, song: Song, w: int = None, h: int = None, *args, **kwargs):
        self.song = song

        self.title = song.title
        self.artist = song.artist
        self.album = song.album
        self.grade = song.grade
        self.length = song.length
        self.difficulty = song.difficulty
        self.best_score = song.best_score

        # Make a real hash, probably on Song.
        self.key = generate_uuid_from_kwargs(title=self.title, artist=self.artist, album=self.album)
        self.key = "".join([c for c in self.key if c in string.ascii_letters + string.digits])

        try:
            album_art_img = PIL.Image.open(f"./albums/album_{self.key}.png")
        except FileNotFoundError:
            album_art = io.BytesIO(requests.get("https://picsum.photos/200.jpg").content)
            album_art_img = PIL.Image.open(album_art)
            album_art_img = album_art_img.convert("RGBA")
            album_art_img.save(f"./albums/album_{self.key}.png")
        self.album_art = arcade.Texture(f"{self.key}-albumart", album_art_img, hit_box_algorithm=None)

        self._w = w if w else Settings.width // 2
        self._h = h if h else Settings.height // 8

        self._tex = arcade.Texture.create_empty(f"{self.key}-menuitem", (self._w, self._h))
        super().__init__(texture=self._tex, *args, **kwargs)
        self._sprite_list = arcade.SpriteList()
        self._sprite_list.append(self)

        self.position = (0, -Settings.height)

        with self._sprite_list.atlas.render_into(self._tex) as fbo:
            fbo.clear()
            arcade.draw_circle_filled(self.width - self.height / 2, self.height / 2, self.height / 2, CharmColors.FADED_PURPLE)
            arcade.draw_lrtb_rectangle_filled(0, self.width - self.height / 2, self.height, 0, CharmColors.FADED_PURPLE)
            arcade.draw_text(
                self.title, self.width - self.height / 2 - 5, self.height / 2, arcade.color.BLACK,
                font_size=self.height / 3 * (3 / 4), font_name="bananaslip plus plus", anchor_x="right"
            )
            arcade.draw_text(
                self.artist + ", " + self.album, self.width - self.height / 2 - 5, self.height / 2, arcade.color.BLACK,
                font_size=self.height / 4 * (3 / 4), font_name="bananaslip plus plus", anchor_x="right", anchor_y="top"
            )

        logger.info(f"Loaded MenuItem {self.title}")


class SongMenu:
    def __init__(self, songs: list[Song] = None, radius = 4, buffer = 5, move_speed = 0.2) -> None:
        self._songs = songs
        self.items: list[SongMenuItem] = []
        if songs:
            for song in self._songs:
                self.items.append(SongMenuItem(song))
        self.sprite_list = arcade.SpriteList()
        for item in self.items:
            self.sprite_list.append(item)

        self.buffer = buffer
        self.move_speed = move_speed
        self.radius = radius

        self._selected_id = 0

        self.local_time = 0
        self.move_start = 0
        self.old_pos = {}
        for item in self.items:
            self.old_pos[item] = (item.left, item.center_y)

    @property
    def selected_id(self) -> int:
        return self._selected_id

    @selected_id.setter
    def selected_id(self, v: int):
        self._selected_id = clamp(0, v, len(self.items) - 1)
        self.move_start = self.local_time
        for item in self.items:
            self.old_pos[item] = (item.left, item.center_y)

    @property
    def selected(self) -> SongMenuItem:
        return self.items[self.selected_id]

    @property
    def move_end(self) -> float:
        return self.move_start + self.move_speed

    def sort(self, key: str, rev: bool = False):
        selected = self.items[self.selected_id]
        self.items.sort(key=lambda item: getattr(item.song, key), reverse=rev)
        self.selected_id = self.items.index(selected)

    def update(self, local_time: float):
        self.local_time = local_time
        current = self.items[self.selected_id]
        current.left = ease_circout(self.old_pos[current][0], 0, self.move_start, self.move_end, self.local_time)
        current.center_y = ease_circout(self.old_pos[current][1], Settings.height // 2, self.move_start, self.move_end, self.local_time)
        up_id = self.selected_id
        down_id = self.selected_id
        x_delta = current.width / (self.radius + 1) / 1.5
        x_offset = 0
        y_offset = 0
        for i in range(self.radius + 1):
            up_id -= 1
            down_id += 1
            x_offset += x_delta
            y_offset += current.height + self.buffer
            if up_id > -1:
                up = self.items[up_id]
                up.left = ease_circout(self.old_pos[up][0], current.left - x_offset, self.move_start, self.move_end, self.local_time)
                up.center_y = ease_circout(self.old_pos[up][1], y_offset + current.center_y, self.move_start, self.move_end, self.local_time)
            if down_id < len(self.items):
                down = self.items[down_id]
                down.left = ease_circout(self.old_pos[down][0], current.left - x_offset, self.move_start, self.move_end, self.local_time)
                down.center_y = ease_circout(self.old_pos[down][1], -y_offset + current.center_y, self.move_start, self.move_end, self.local_time)

    def draw(self):
        self.sprite_list.draw()
