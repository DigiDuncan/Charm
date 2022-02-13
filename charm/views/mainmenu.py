import arcade
from charm.lib.anim import ease_quartout

from charm.lib.charm import CharmColors, generate_gum_wrapper, move_gum_wrapper
from charm.lib.digiview import DigiView
from charm.objects.menu import MainMenu, MainMenuItem
from charm.views.songmenu import SongMenuView
from charm.views.spritetest import SpriteTestView
from charm.views.test import TestView


class MainMenuView(DigiView):
    def __init__(self, *args, **kwargs):
        super().__init__(fade_in=1, bg_color=CharmColors.FADED_GREEN, *args, **kwargs)

    def setup(self):
        super().setup()

        # Generate "gum wrapper" background
        self.logo_width, self.small_logos_forward, self.small_logos_backward = generate_gum_wrapper(self.size)

        self.menu = MainMenu(
            [
                MainMenuItem("Playlists", "playlist", None),
                MainMenuItem("Songs", "songs", SongMenuView(back=self)),
                MainMenuItem("Options", "option", None),
                MainMenuItem("Test", "test", TestView(back=self)),
                MainMenuItem("Sprite Test", "spritetest", SpriteTestView(back=self))
            ]
        )

    def on_key_press(self, symbol: int, modifiers: int):
        match symbol:
            case arcade.key.RIGHT:
                self.menu.selected_id += 1
            case arcade.key.LEFT:
                self.menu.selected_id -= 1
            case arcade.key.BACKSPACE:
                self.back.setup()
                self.window.show_view(self.back)
                arcade.play_sound(self.window.sounds["back"])
            case arcade.key.ENTER:
                if self.menu.selected.goto is not None:
                    self.menu.selected.goto.setup()
                    self.window.show_view(self.menu.selected.goto)
                    arcade.play_sound(self.window.sounds["valid"])
                else:
                    self.menu.selected.jiggle_start = self.local_time

        return super().on_key_press(symbol, modifiers)

    def on_update(self, delta_time):
        super().on_update(delta_time)

        move_gum_wrapper(self.logo_width, self.small_logos_forward, self.small_logos_backward, delta_time)
        self.menu.update(self.local_time)

    def on_draw(self):
        self.clear()
        self.camera.use()

        # Charm BG
        self.small_logos_forward.draw()
        self.small_logos_backward.draw()

        left = ease_quartout(self.size[0], 0, 0.5, 1.5, self.local_time)
        arcade.draw_lrtb_rectangle_filled(left, self.size[0], (self.size[1] // 4) * 3, self.size[1] // 4, arcade.color.WHITE + (127,))

        self.menu.draw()

        super().on_draw()
