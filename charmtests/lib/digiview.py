import arcade
from arcade import View, Window

from charmtests.lib.anim import ease_linear
from charmtests.lib.settings import Settings

class DigiView(View):
    def __init__(self, window: Window = None, *, back: View = None,
                 fade_in: float = 0, bg_color = (0, 0, 0), show_fps = False):
        super().__init__(window)
        self.back = back
        self.size = self.window.get_size()
        self.local_time = 0
        self.show_fps = show_fps
        self.fade_in = fade_in
        self.bg_color = bg_color
        self.camera = arcade.Camera(Settings.width, Settings.height, self.window)

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
            arcade.draw_lrtb_rectangle_filled(0, Settings.width, Settings.height, 0,
                (0, 0, 0, alpha)
            )

        if self.window.debug:
            arcade.draw_lrtb_rectangle_outline(0, Settings.width, Settings.height, 0, arcade.color.RED, 3)
        
        if self.show_fps:
            self.window.fps_draw()
