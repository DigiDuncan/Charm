import arcade
from arcade import View, Window

from charmtests.lib.anim import ease_linear
from charmtests.lib.settings import Settings


class DigiView(View):
    def __init__(self, window: Window = None, *, back: View = None,
                 fade_in: float = 0, bg_color = (0, 0, 0)):
        super().__init__(window)
        self.back = back
        self.size = self.window.get_size()
        self.local_time = 0
        self.fade_in = fade_in
        self.bg_color = bg_color
        self.camera = arcade.Camera(Settings.width, Settings.height, self.window)
        self.debug_options = {
            "camera_scale": 1,
            "box": False}

    def setup(self):
        self.local_time = 0

        arcade.set_background_color(self.bg_color)

    def on_resize(self, width: int, height: int):
        self.size = self.window.get_size()

    def on_key_press(self, symbol: int, modifiers: int):
        if symbol == arcade.key.KEY_7:
            self.window.debug = not self.window.debug
            if self.window.debug:
                self.camera.scale = self.debug_options["camera_scale"]
            else:
                self.camera.scale = 1
        if self.window.debug and modifiers & arcade.key.MOD_SHIFT:
            match symbol:
                case arcade.key.Z:  # camera zoon
                    self.debug_options["camera_scale"] = 2 if self.debug_options["camera_scale"] == 1 else 1
                    self.camera.scale = self.debug_options["camera_scale"]
                case arcade.key.B:  # camera outline
                    self.debug_options["box"] = not self.debug_options["box"]
                case arcade.key.A:  # show atlas
                    self.window.ctx.default_atlas.show()
                case arcade.key.L:  # show log
                    self.window.show_log = not self.window.show_log
        return super().on_key_press(symbol, modifiers)

    def on_update(self, delta_time: float):
        self.local_time += delta_time

    def on_draw(self):
        if self.local_time <= self.fade_in:
            alpha = ease_linear(255, 0, 0, self.fade_in, self.local_time)
            arcade.draw_lrtb_rectangle_filled(0, Settings.width, Settings.height, 0,
                                              (0, 0, 0, alpha))

        if self.window.debug and self.debug_options["box"]:
            arcade.draw_lrtb_rectangle_outline(0, Settings.width, Settings.height, 0, arcade.color.RED, 3)

        self.window.debug_draw()
