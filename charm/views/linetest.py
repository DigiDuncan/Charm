import importlib.resources as pkg_resources

import arcade

from charm.lib.charm import CharmColors, generate_gum_wrapper, move_gum_wrapper
from charm.lib.digiview import DigiView
from charm.lib.settings import Settings
from charm.objects.line_renderer import LineRenderer, TimePoint


class LineTestView(DigiView):
    def __init__(self, *args, **kwargs):
        super().__init__(fade_in=1, bg_color=CharmColors.FADED_GREEN, *args, **kwargs)
        self.song = None
        self.volume = 1

    def setup(self):
        super().setup()
        points: list[tuple[tuple[int, int], float]] = []
        points2 = []
        for i in range(20, 600, 10):
            points.append(((100, i), i / 50))
            points2.append(((200, i), i / 50))
        points.append(((150, 10), 0))
        points2.append(((150, 10), 0))

        self.line_renderer = LineRenderer([TimePoint(*p) for p in points], arcade.color.BLUE, 3)
        self.line_renderer2 = LineRenderer([TimePoint(*p) for p in points2], arcade.color.BLUE, 3)

        self.time_text = arcade.Text("0.00", Settings.width - 5, Settings.height - 5, arcade.color.BLUE, 24, Settings.width - 5, align="right", anchor_x="right", anchor_y="top")

        # Generate "gum wrapper" background
        self.logo_width, self.small_logos_forward, self.small_logos_backward = generate_gum_wrapper(self.size)

    def on_show_view(self):
        self.window.theme_song.volume = 0

    def on_key_press(self, symbol: int, modifiers: int):
        match symbol:
            case arcade.key.BACKSPACE:
                self.back.setup()
                self.window.show_view(self.back)
                arcade.play_sound(self.window.sounds["back"])

        return super().on_key_press(symbol, modifiers)

    def on_update(self, delta_time):
        super().on_update(delta_time)
        self.line_renderer.update(delta_time)
        self.line_renderer2.update(delta_time)

        self.time_text.text = str(round(self.local_time, 2))

        if self.window.keyboard[arcade.key.LEFT]:
            self.line_renderer.move_from_now(-1, 0)
            self.line_renderer2.move_from_now(-1, 0)
        if self.window.keyboard[arcade.key.RIGHT]:
            self.line_renderer.move_from_now(1, 0)
            self.line_renderer2.move_from_now(1, 0)

        move_gum_wrapper(self.logo_width, self.small_logos_forward, self.small_logos_backward, delta_time)

    def on_draw(self):
        self.clear()
        self.camera.use()

        # Charm BG
        self.small_logos_forward.draw()
        self.small_logos_backward.draw()

        self.line_renderer.draw()
        self.line_renderer2.draw()

        self.time_text.draw()

        super().on_draw()
