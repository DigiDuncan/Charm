import arcade
from arcade import Sprite
from charmtests.lib.settings import Settings
from charmtests.objects.song import Song


class MenuItem(Sprite):
    cid = 0

    def __init__(self, song: Song, w: int = None, h: int = None, *args, **kwargs):
        self.title = song.title
        self.artist = song.artist
        self.album = song.album
        self.grade = song.grade

        self._w = w if w else Settings.width // 2
        self._h = h if h else Settings.height // 8

        self._tex = arcade.Texture.create_empty(f"{self.__class__.__name__}-{self.__class__.cid}", (self._w, self._h))
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
