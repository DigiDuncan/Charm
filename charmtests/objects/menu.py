import arcade
from arcade import Sprite
from charmtests.lib.settings import Settings
from charmtests.objects.song import Song


class MenuItem(Sprite):
    cid = 0

    def __init__(self, song: Song, w: int = None, h: int = None, *args, **kwargs):
        self.song = song
    
        self.title = song.title
        self.artist = song.artist
        self.album = song.album
        self.grade = song.grade

        self.album_art = None

        self._w = w if w else Settings.width // 2
        self._h = h if h else Settings.height // 8

        self._tex = arcade.Texture.create_empty(f"{self.__class__.__name__}-{self.__class__.cid}", (self._w, self._h))
        self.__class__.cid += 1
        super().__init__(texture = self._tex, *args, **kwargs)
        self._sprite_list = arcade.SpriteList()
        self._sprite_list.append(self)

        with self._sprite_list.atlas.render_into(self._tex) as fbo:
            fbo.clear()
            arcade.draw_circle_filled(self.width - self.height / 2, self.height / 2, self.height / 2, arcade.color.WHITE)
            arcade.draw_lrtb_rectangle_filled(0, self.width - self.height / 2, self.height, 0, arcade.color.WHITE)
            arcade.draw_text(
                self.title, self.width - self.height / 2 - 5, self.height / 2, arcade.color.BLACK,
                font_size=self.height/3 * (3/4), font_name="bananaslip plus plus", anchor_x="right"
            )
            arcade.draw_text(
                self.artist + ", " + self.album, self.width - self.height / 2 - 5, self.height / 2, arcade.color.BLACK,
                font_size=self.height/4 * (3/4), font_name="bananaslip plus plus", anchor_x="right", anchor_y="top"
            )

class Menu:
    def __init__(self, songs: list[Song] = None, radius = 4, buffer = 5, move_speed = 1) -> None:
        self._songs = songs
        self.items: list[MenuItem] = []
        if songs:
            for song in self._songs:
                self.items.append(MenuItem(song))
        self.sprite_list = arcade.SpriteList()
        for item in self.items:
            self.sprite_list.append(item)
            item.position = (-1000, -1000)

        self.buffer = buffer
        self.move_speed = move_speed
        self.radius = radius

        self.camera = arcade.Camera(Settings.width, Settings.height)
        self.selected_id = 0

        self.moving_direction = None
        self.moving_started = None

        self.update_please = True

    def sort(self, key: str, rev: bool = False):
        selected = self.items[self.selected_id]
        self.items.sort(key=lambda item: getattr(item.song, key), reverse=rev)
        self.selected_id = self.items.index(selected)

    def update(self, local_time: float):
        if not self.update_please:
            return
        old_pos = {}
        for item in self.items:
            old_pos[item] = (item.left, item.center_y)
            item.position = (-1000, -1000)
        current = self.items[self.selected_id]
        current.left = 0
        current.center_y = Settings.height // 2
        up_id = self.selected_id
        down_id = self.selected_id
        x_delta = current.width / (self.radius + 1) / 1.5
        x_offset = 0
        y_offset = 0
        for i in range(self.radius):
            up_id -= 1
            down_id += 1
            x_offset += x_delta
            y_offset += current.height + self.buffer
            if up_id > -1:
                up = self.items[up_id]
                up.left = current.left - x_offset
                up.center_y = y_offset + current.center_y
            if down_id < len(self.items):
                down = self.items[down_id]
                down.left = current.left - x_offset
                down.center_y = -y_offset + current.center_y
        self.update_please = False

    def draw(self):
        self.camera.use()
        self.sprite_list.draw()
