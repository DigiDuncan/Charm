import arcade

from charmtests.lib.charm import CharmColors, generate_gum_wrapper, move_gum_wrapper
from charmtests.lib.digiview import DigiView
from charmtests.lib.utils import clamp
from charmtests.objects.menu import MainMenu, MainMenuItem
from charmtests.objects.song import Song
from charmtests.views.song import SongView
from charmtests.views.songmenu import SongMenuView

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
                MainMenuItem("Songs", "songs", SongMenuView( back = self)),
                MainMenuItem("Options", "option", None)
            ]
        )

    def on_key_press(self, symbol: int, modifiers: int):
        match symbol:
            case arcade.key.RIGHT:
                self.menu.selected_id += 1
            case arcade.key.LEFT:
                self.menu.selected_id -= 1
            case arcade.key.BACKSPACE:
                self.window.show_view(self.back)
                arcade.play_sound(self.window.sounds["back"])
            case arcade.key.ENTER:
                if self.menu.selected.goto is not None:
                    self.menu.selected.goto.setup()
                    self.window.show_view(self.menu.selected.goto)
                    arcade.play_sound(self.window.sounds["valid"])

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

        self.menu.draw()

        super().on_draw()
