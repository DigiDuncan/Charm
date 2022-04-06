import string
import arcade

from charm.lib.charm import CharmColors, generate_gum_wrapper, move_gum_wrapper
from charm.lib.digiview import DigiView
from charm.lib.settings import Settings

valid_letters = [let for let in string.ascii_uppercase] + ["KEY_" + d for d in string.digits]
keymap = {getattr(arcade.key, v): v.removeprefix("KEY_").lower() for v in valid_letters}


class CheatView(DigiView):
    def __init__(self, *args, **kwargs):
        super().__init__(fade_in=1, bg_color=CharmColors.FADED_GREEN, *args, **kwargs)
        self.song = None

    def setup(self):
        super().setup()
        self.current_cheat = ""

        self.instructions = arcade.Text(
            "Enter Cheat:", Settings.width // 2, (Settings.height // 3) * 2, arcade.color.BLACK, 48,
            align="center", anchor_x="center", anchor_y="center", width = Settings.width, font_name="bananaslip plus plus"
        )
        self.cheat = arcade.Text(
            "", Settings.width // 2, Settings.height // 2, CharmColors.PURPLE, 72,
            align="center", anchor_x="center", anchor_y="center", width = Settings.width, font_name="bananaslip plus plus"
        )
        self.more_instructions = arcade.Text(
            "SHIFT+BACKSPACE to exit.", Settings.width // 2, 10, arcade.color.BLACK, 24,
            align="center", anchor_x="center", width = Settings.width, font_name="bananaslip plus plus"
        )

        # Generate "gum wrapper" background
        self.logo_width, self.small_logos_forward, self.small_logos_backward = generate_gum_wrapper(self.size)

    def on_key_press(self, symbol: int, modifiers: int):
        match symbol:
            case arcade.key.BACKSPACE:
                if modifiers & arcade.key.MOD_SHIFT:
                    self.back.setup()
                    self.window.show_view(self.back)
                    arcade.play_sound(self.window.sounds["back"])
                else:
                    self.current_cheat = self.current_cheat[:-1]
            case arcade.key.ENTER:
                if self.current_cheat in self.window.cheats:
                    self.window.cheats[self.current_cheat] = True
                    arcade.play_sound(self.window.sounds["valid"])

        if symbol in keymap:
            self.current_cheat += keymap[symbol]

        self.cheat.text = self.current_cheat

        return super().on_key_press(symbol, modifiers)

    def on_update(self, delta_time):
        super().on_update(delta_time)

        move_gum_wrapper(self.logo_width, self.small_logos_forward, self.small_logos_backward, delta_time)

    def on_draw(self):
        self.clear()
        self.camera.use()

        # Charm BG
        self.small_logos_forward.draw()
        self.small_logos_backward.draw()

        self.instructions.draw()
        self.cheat.draw()
        self.more_instructions.draw()

        super().on_draw()
