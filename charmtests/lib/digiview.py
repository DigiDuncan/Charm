import arcade
from arcade import View, Window

from charmtests.lib.anim import ease_linear

class DigiView(View):
    def __init__(self, window: Window = None, *, back: View = None,
                 fade_in: float = 0, bg_color = (0, 0, 0)):
        super().__init__(window)
        self.back = back
        self.size = self.window.get_size()
        self.local_time = 0

    def setup(self):
        self.local_time = 0

        arcade.set_background_color(self.bg_color)

    def on_resize(self, width: int, height: int):
        self.size = self.window.get_size()

    def on_update(self, delta_time: float):
        self.local_time += delta_time

    def on_draw(self):
        if self.local_time <= self.fade_in:
            alpha = ease_linear(255, 0, 0, self.fade_in, self.local_time)
            arcade.draw_lrtb_rectangle_filled(0, 1280, 720, 0,
                (0, 0, 0, alpha)
            )
