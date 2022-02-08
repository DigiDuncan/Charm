from calendar import setfirstweekday
from arcade import Camera
import arcade
from .song import Chart
from charmtests.lib.settings import Settings
from charmtests.lib import anim

class Highway:
    def __init__(self, chart: Chart, pos: tuple[int, int], size: tuple[int, int] = None,
                 gap: int = 5, viewport: float = 1):
        self.chart = chart
        self.notes = self.chart.notes

        self.pos = pos
        self.size = size if size is not None else (Settings.width // 3, Settings.height)
        self.gap = gap
        self.viewport = viewport
        self.sprite_list = arcade.SpriteList()

        self.camera = Camera(Settings.width, Settings.height)
        self.song_time: float = 0

    @property
    def x(self) -> int:
        return self.pos[0]

    @property
    def y(self) -> int:
        return self.pos[1]

    @property
    def w(self) -> int:
        return self.size[0]

    @property
    def h(self) -> int:
        return self.size[1]

    @property
    def note_size(self) -> int:
        return (self.w - (self.gap * self.chart.lanes)) // self.chart.lanes

    @property
    def strikeline_y(self):
        return self.h - 25

    @property
    def visible_notes(self):
        return [n for n in self.notes if self.song_time - self.viewport < n.position <= self.song_time + self.viewport]

    def apos(self, rpos: tuple[int, int]) -> tuple[int, int]:
        return (rpos[0] + self.pos[0], rpos[1] + self.pos[1])

    def lane_x(self, lane_num):
        return (self.note_size * (lane_num) + (self.gap * (lane_num) - 1)) + self.x

    def note_y(self, at: float):
        rt = at - self.song_time
        return ((self.strikeline_y / self.viewport) * -rt + self.strikeline_y) + self.y

    def update(self, song_time):
        self.song_time = song_time

    def draw(self):
        raise NotImplementedError
