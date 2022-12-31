from typing import Hashable

import arcade

TuplePoint = tuple[int | float, int | float]
Seconds = float

class Point:
    def __init__(self, point: TuplePoint):
        self._point = point

    @property
    def x(self) -> float:
        return self._point[0]

    @x.setter
    def x(self, val: float):
        self._point = (val, self._point[1])

    @property
    def y(self) -> float:
        return self._point[1]

    @y.setter
    def y(self, val: float):
        self._point = (self._point[0], val)

    def move(self, x: float, y: float):
        self._point = (self._point[0] + x, self._point[1] + y)

class LineRenderer:
    def __init__(self, points: list[Point], color: arcade.Color, width: float):
        self.points: list[Point] = points
        self.color = color
        self.width = width

    def move(self, x: float, y: float):
        for p in self.points:
            p.move(x, y)

    @property
    def point_tuples(self) -> list[tuple[float, float]]:
        return [p._point for p in self.points]

    def update(self, delta_time: float):
        self.current_time += delta_time

    def draw(self):
        arcade.draw_line_strip(self.point_tuples, self.color, self.width)

class MultiLineRenderer:
    def __init__(self, line_renderers: dict[Hashable, LineRenderer] = {}):
        self.line_renderers = line_renderers

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

    def draw(self):
        for lr in self.line_renderers.values():
            lr.draw()

class NoteTrail(MultiLineRenderer):
    def __init__(self, note_id: Hashable, note_center: Point, time_start: Seconds, length: Seconds,
                 px_per_s: float, color: arcade.Color, point_depth: float = 50, width: float = 100,
                 *, resolution: int = 5, thickness: int = 3, upscroll = False,
                 fill_color: arcade.Color | None = None, curve = False):

        self.note_id = note_id
        self.note_center = note_center
        self.width = width
        self.resolution = resolution
        self.upscroll = upscroll
        self.fill_color = fill_color
        self.point_depth = point_depth
        self.color = color
        self.thickness = thickness
        self.curve = curve

        points1: list[TuplePoint] = []
        points2: list[TuplePoint] = []

        self._trail_length = int(length * px_per_s) - self.point_depth

        start_y = note_center[1]
        self.left_x = note_center[0] - (width / 2)
        self.right_x = note_center[0] + (width / 2)

        if upscroll:
            self._trail_end = start_y - self._trail_length
            self._point_tip = self._trail_end - self.point_depth
            self.end_y = int(-(length * px_per_s))
            resolution = -resolution
        else:
            self._trail_end = start_y + self._trail_length
            self._point_tip = self._trail_end + self.point_depth
            self.end_y = int(length * px_per_s)

        # top of line
        points1.append((self.left_x + self.thickness, start_y))
        points2.append((self.right_x - self.thickness, start_y))
        # bottom of line
        points1.append((self.left_x + self.thickness, self._trail_end))
        points2.append((self.right_x - self.thickness, self._trail_end))
        if not self.curve:
            points1.append((self.note_center[0], self._point_tip))
            points2.append((self.note_center[0], self._point_tip))

        self.line_renderer1 = LineRenderer([Point(p) for p in points1], self.color, self.thickness)
        self.line_renderer2 = LineRenderer([Point(p) for p in points2], self.color, self.thickness)

        self.rectangles = arcade.ShapeElementList()
        self.curve_cap = None
        self.texture = None
        self.sprite = None
        if self.curve:
            self.texture = arcade.Texture.create_empty(f"_line_renderer_{self.color}_{self.fill_color}_{self.width}_{self.point_depth}", (self.width, self.point_depth))
            self.sprite = arcade.Sprite(texture = self.texture)
            offset = -self.point_depth / 2 if self.upscroll else self.point_depth / 2
            self.sprite.set_position(self.note_center[0], self._trail_end + offset)
            self.curve_cap = arcade.SpriteList()
            self.curve_cap.append(self.sprite)
        self.generate_fill()

        nid = str(note_id)

        super().__init__({f"{nid}_left": self.line_renderer1, f"{nid}_right": self.line_renderer2})

    def generate_fill(self):
        self.rectangles = arcade.ShapeElementList()
        if self.fill_color:
            mid_point_x = (self.left_x + self.right_x) / 2
            mid_point_y = (self.note_center[1] + self._trail_end) / 2
            rect = arcade.create_rectangle_filled(mid_point_x, mid_point_y, self.width - self.thickness, self._trail_length, self.fill_color)
            self.rectangles.append(rect)
            if not self.curve:
                tri_left = (self.left_x + self.thickness, self._trail_end)
                tri_right = (self.right_x - self.thickness, self._trail_end)
                tri_bottom = (self.note_center[0], self._point_tip)
                self.rectangles.append(arcade.create_polygon([tri_left, tri_right, tri_bottom], self.fill_color))
        if self.curve:
            window = arcade.get_window()
            ctx = window.ctx
            ctx.blend_func = ctx.BLEND_ADDITIVE
            with self.curve_cap.atlas.render_into(self.texture) as fbo:
                fbo.clear()
                if self.fill_color:
                    arcade.draw_arc_filled(self.width / 2, 0, self.width - self.thickness * 2,
                                           self.point_depth - self.thickness, self.fill_color, 0, 180)
                arcade.draw_arc_outline(self.width / 2, 0, self.width - self.thickness * 2,
                                        self.point_depth - self.thickness, self.color, 0, 180, self.thickness * 2)
            ctx.blend_func = ctx.BLEND_DEFAULT

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

    def draw(self):
        if self.rectangles:
            self.rectangles.draw()
        for lr in self.line_renderers.values():
            lr.draw()
        if self.curve_cap:
            self.curve_cap.draw()
