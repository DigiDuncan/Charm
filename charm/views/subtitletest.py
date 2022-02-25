import importlib.resources as pkg_resources

import arcade

from charm.lib.charm import CharmColors, generate_gum_wrapper, move_gum_wrapper
from charm.lib.digiview import DigiView
from charm.lib.settings import Settings

import charm.data.subtitle
from charm.objects.lyric import LyricAnimator


class SubtitleView(DigiView):
    def __init__(self, *args, **kwargs):
        super().__init__(fade_in=1, bg_color=CharmColors.FADED_GREEN, *args, **kwargs)

    def setup(self):
        super().setup()

        with pkg_resources.path(charm.data.subtitle, "crossing_field_8bit.mp3") as p:
            self._song = arcade.load_sound(p)

        with pkg_resources.path(charm.data.subtitle, "crossing_field.ass") as p:
            self.lyric_animator = LyricAnimator(p)

        # Generate "gum wrapper" background
        self.logo_width, self.small_logos_forward, self.small_logos_backward = generate_gum_wrapper(self.size)

    def on_show(self):
        self.song = arcade.play_sound(self._song, self.volume, looping=False)

    def on_key_press(self, symbol: int, modifiers: int):
        match symbol:
            case arcade.key.BACKSPACE:
                self.back.setup()
                self.window.show_view(self.back)
                arcade.play_sound(self.window.sounds["back"])

        return super().on_key_press(symbol, modifiers)

    def on_update(self, delta_time):
        super().on_update(delta_time)
        self.sprite.update_animation(delta_time)

        move_gum_wrapper(self.logo_width, self.small_logos_forward, self.small_logos_backward, delta_time)

    def on_draw(self):
        self.clear()
        self.camera.use()

        # Charm BG
        self.small_logos_forward.draw()
        self.small_logos_backward.draw()

        super().on_draw()
