from functools import total_ordering
from typing import Hashable
import PIL.Image

import arcade
from nindex import Index

from charm.lib.utils import scale_float

Point = tuple[int | float, int | float]
Seconds = float


@total_ordering
class TimePoint:
    def __init__(self, point: Point, time: float):
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

        self.current_time = 0.0

        self.points.sort()
        self.points_by_time = Index(self.points, "time")

    def move(self, x: float, y: float):
        for p in self.points:
            p.move(x, y)

    def move_points_past_time(self, x: float, y: float, time: float, lock_final = False):
        # anchor_point = self.points_by_time.lteq(time)
        ind = self.points_by_time.gteq_index(time)
        if ind is None:
            return
        if lock_final and len(self.points[ind:]) == 1:
            return
        for p in self.points[ind:]:
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

    def draw_points_past_time(self, time: float):
        points = [p.point for p in self.points if p.time >= time]
        arcade.draw_line_strip(points, self.color, self.width)

    def draw_from_now(self):
        self.draw_points_past_time(self.current_time)

class MultiLineRenderer:
    def __init__(self, line_renderers: dict[Hashable, LineRenderer] = {}):
        self.line_renderers = line_renderers
        self.current_time = 0.0

    def add_renderer(self, id: Hashable, renderer: LineRenderer):
        if id in self.line_renderers:
            raise ValueError(f"ID {id} already in multi-line renderer!")
        self.line_renderers[id] = renderer

    def remove_renderer(self, id: Hashable):
        self.line_renderers.pop(id)

    def remove_renderers_with_prefix(self, prefix: Hashable):
        p = str(prefix)
        for id in self.line_renderers.keys():
            if str(id).startswith(p):
                self.line_renderers.pop(id)

    def move(self, x: float, y: float):
        for lr in self.line_renderers.values():
            lr.move(x, y)

    def move_points_past_time(self, x: float, y: float, time: float, lock_final = False):
        for lr in self.line_renderers.values():
            lr.move_points_past_time(x, y, time, lock_final)

    def move_from_now(self, x: float, y: float):
        for lr in self.line_renderers.values():
            lr.move_points_past_time(x, y, self.current_time)

    def update(self, delta_time: float):
        self.current_time += delta_time

    def draw(self):
        for lr in self.line_renderers.values():
            lr.draw()

    def draw_points_past_time(self, time: float):
        for lr in self.line_renderers.values():
            lr.draw_points_past_time(time)

    def draw_from_now(self):
        for lr in self.line_renderers.values():
            lr.draw_points_past_time(self.current_time)

class NoteTrail(MultiLineRenderer):
    def __init__(self, note_id: Hashable, note_center: Point, time_start: Seconds, length: Seconds,
                 px_per_s: float, color: arcade.Color, point_depth: float = 50, width: float = 100,
                 *, resolution: int = 5, thickness: int = 3, upscroll = False,
                 fill_color: arcade.Color | None = None, simple = True, curve = False):

        self.note_id = note_id
        self.note_center = note_center
        self.width = width
        self.resolution = resolution
        self.upscroll = upscroll
        self.fill_color = fill_color
        self.simple = simple
        self.point_depth = point_depth
        self.color = color
        self.thickness = thickness
        self.curve = curve

        points1: list[tuple[Point, float]] = []
        points2: list[tuple[Point, float]] = []

        self._trail_length = (length * px_per_s) - self.point_depth
        time_end = time_start + length
        trail_time_end = time_end - (point_depth / px_per_s)

        start_y = note_center[1]
        self.left_x = note_center[0] - (width / 2)
        self.right_x = note_center[0] + (width / 2)

        if upscroll:
            self._trail_end = start_y - self._trail_length
            self._point_tip = self._trail_end - self.point_depth
            self.end_y = -(length * px_per_s)
            resolution = -resolution
        else:
            self._trail_end = start_y + self._trail_length
            self._point_tip = self._trail_end + self.point_depth
            self.end_y = (length * px_per_s)

        if simple:
            # top of line
            points1.append(((self.left_x, start_y), time_start))
            points2.append(((self.right_x, start_y), time_start))
            # bottom of line
            points1.append(((self.left_x, self._trail_end), trail_time_end))
            points2.append(((self.right_x, self._trail_end), trail_time_end))
        else:
            for i in range(int(start_y), int(self._trail_end), resolution):
                time = scale_float(time_start, trail_time_end, i, start_y, self._trail_end)
                points1.append(((self.left_x, i), time))
                points2.append(((self.right_x, i), time))
        if not self.curve:
            points1.append(((self.note_center[0], self._point_tip), time_end))
            points2.append(((self.note_center[0], self._point_tip), time_end))

        self.line_renderer1 = LineRenderer([TimePoint(*p) for p in points1], self.color, self.thickness)
        self.line_renderer2 = LineRenderer([TimePoint(*p) for p in points2], self.color, self.thickness)

        self.rectangles = arcade.ShapeElementList()
        self.curve_cap = None
        self.texture = None
        self.sprite = None
        if self.curve:
            self.texture = arcade.Texture.create_empty(f"_line_renderer_{self.color}_{self.fill_color}_{self.width}_{self.point_depth}", (self.width, self.point_depth))
            self.sprite = arcade.Sprite(texture = self.texture)
            self.sprite.set_position(self.note_center[0], self._trail_end)
            self.curve_cap = arcade.SpriteList()
            self.curve_cap.append(self.sprite)
        self.generate_fill()

        nid = str(note_id)

        super().__init__({f"{nid}_left": self.line_renderer1, f"{nid}_right": self.line_renderer2})

    def generate_fill(self):
        self.rectangles = arcade.ShapeElementList()
        if self.fill_color:
            if self.simple:
                mid_point_x = (self.left_x + self.right_x) / 2
                mid_point_y = (self.note_center[1] + self._trail_end) / 2
                rect = arcade.create_rectangle_filled(mid_point_x, mid_point_y, self.width, self._trail_length, self.fill_color)
                self.rectangles.append(rect)
            else:
                for (point1, point2) in zip(self.line_renderer1.point_tuples[:-1], self.line_renderer2.point_tuples[:-1]):
                    mid_point_x = (point1[0] + point2[0]) / 2
                    mid_point_y = (point1[1] + point2[1]) / 2
                    rect = arcade.create_rectangle_filled(mid_point_x, mid_point_y, self.width, self.resolution, self.fill_color)
                    self.rectangles.append(rect)
            if not self.curve:
                tri_left = (self.left_x, self._trail_end)
                tri_right = (self.right_x, self._trail_end)
                tri_bottom = (self.note_center[0], self._point_tip)
                self.rectangles.append(arcade.create_polygon([tri_left, tri_right, tri_bottom], self.fill_color))
        if self.curve:
            with self.curve_cap.atlas.render_into(self.texture) as fbo:
                fbo.clear()
                if self.fill_color:
                    arcade.draw_arc_filled(self.width / 2, self.point_depth / 2, self.width,
                                           self.point_depth, self.fill_color, 0, 180)
                arcade.draw_arc_outline(self.width / 2, self.point_depth / 2, self.width,
                                        self.point_depth, self.color, 0, 180, self.thickness)

    def move(self, x: float, y: float):
        for lr in self.line_renderers.values():
            lr.move(x, y)
        self.rectangles.move(x, y)
        if self.curve_cap:
            self.curve_cap.move(x, y)
        self.note_center = (self.note_center[0] + x, self.note_center[1] + y)

    def set_position(self, x: float, y: float):
        ox, oy = self.note_center
        mx = x - ox
        my = y - oy
        self.move(mx, my)

    def move_points_past_time(self, x: float, y: float, time: float):
        for lr in self.line_renderers.values():
            lr.move_points_past_time(x, y, time, True)
        self.generate_fill()

    def move_from_now(self, x: float, y: float):
        for lr in self.line_renderers.values():
            lr.move_points_past_time(x, y, self.current_time, True)
        self.generate_fill()

    def draw(self):
        if self.rectangles:
            self.rectangles.draw()
        for lr in self.line_renderers.values():
            lr.draw()
        if self.curve_cap:
            self.curve_cap.draw()

    def draw_points_past_time(self, time: float):
        if self.rectangles:
            self.rectangles.draw()
        for lr in self.line_renderers.values():
            lr.draw_points_past_time(time)

    def draw_from_now(self):
        if self.rectangles:
            self.rectangles.draw()
        for lr in self.line_renderers.values():
            lr.draw_points_past_time(self.current_time)