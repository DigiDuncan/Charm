from functools import total_ordering
import arcade
from nindex import Index

@total_ordering
class TimePoint:
    def __init__(self, point: tuple[float, float], time: float):
        self.point = point
        self.time = time

    @property
    def x(self) -> float:
        return self.point[0]

    @x.setter
    def x(self, val: float):
        self.point = (val, self.point[1])

    @property
    def y(self) -> float:
        return self.point[1]

    @x.setter
    def y(self, val: float):
        self.point = (self.point[0], val)

    def move(self, x: float, y: float):
        self.point = (self.point[0] + x, self.point[1] + y)

    def __lt__(self, other: "TimePoint") -> bool:
        return self.time < other.time

    def __eq__(self, other: "TimePoint") -> bool:
        return self.time == other.time and self.point == other.point

class LineRenderer:
    def __init__(self, points: list[TimePoint], color: arcade.Color, width: float):
        self.points: list[TimePoint] = points
        self.color = color
        self.width = width

        self.current_time = 0

        self.points.sort()
        self.points_by_time = Index(self.points, "time")

    def move(self, x: float, y: float):
        for p in self.points:
            p.move(x, y)

    def move_points_past_time(self, x: float, y: float, time: float):
        for p in self.points[self.points_by_time.gt_index(time):]:
            p.move(x, y)

    def move_from_now(self, x: float, y: float):
        self.move_points_past_time(x, y, self.current_time)

    @property
    def point_tuples(self) -> list[tuple[float, float]]:
        return [p.point for p in self.points]

    def update(self, delta_time: float):
        self.current_time += delta_time

    def draw(self):
        arcade.draw_line_strip(self.point_tuples, self.color, self.width)