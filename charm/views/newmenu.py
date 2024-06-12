import logging

import arcade
from arcade import color as colors

from charm.lib.charm import GumWrapper
from charm.lib.digiview import DigiView
from charm.objects.songmenu2 import SongMenu
from charm.lib.keymap import keymap

logger = logging.getLogger("charm")


class NewMenuView(DigiView):
    def __init__(self, back: DigiView):
        super().__init__(fade_in=1, back=back)
        self.song = None
        self.menu: SongMenu = None

    def setup(self) -> None:
        super().presetup()

        self.menu = SongMenu([])

        # Generate "gum wrapper" background
        self.gum_wrapper = GumWrapper(self.size)

        super().postsetup()

    def on_show_view(self) -> None:
        self.window.theme_song.volume = 0

    def on_key_press(self, symbol: int, modifiers: int) -> None:
        super().on_key_press(symbol, modifiers)
        if keymap.back.pressed:
            self.go_back()


    def on_update(self, delta_time) -> None:
        super().on_update(delta_time)
        if self.window.keyboard[arcade.key.Y]:
            self.menu.min_factor += delta_time
        if self.window.keyboard[arcade.key.H]:
            self.menu.min_factor -= delta_time
        if self.window.keyboard[arcade.key.U]:
            self.menu.max_factor += delta_time
        if self.window.keyboard[arcade.key.J]:
            self.menu.max_factor -= delta_time
        if self.window.keyboard[arcade.key.I]:
            self.menu.offset += delta_time
        if self.window.keyboard[arcade.key.K]:
            self.menu.offset -= delta_time
        if self.window.keyboard[arcade.key.O]:
            self.menu.in_sin += delta_time
        if self.window.keyboard[arcade.key.L]:
            self.menu.in_sin -= delta_time
        if self.window.keyboard[arcade.key.P]:
            self.menu.out_sin += delta_time
        if self.window.keyboard[arcade.key.SEMICOLON]:
            self.menu.out_sin -= delta_time
        if self.window.keyboard[arcade.key.BRACKETLEFT]:
            self.menu.shift += delta_time
        if self.window.keyboard[arcade.key.APOSTROPHE]:
            self.menu.shift -= delta_time
        if self.window.keyboard[arcade.key.BRACKETRIGHT]:
            self.menu.move_forward += delta_time
        if self.window.keyboard[arcade.key.BACKSLASH]:
            self.menu.move_forward -= delta_time
        if self.window.keyboard[arcade.key.COMMA]:
            self.menu.y_shift += delta_time * 100
        if self.window.keyboard[arcade.key.PERIOD]:
            self.menu.y_shift -= delta_time * 100

        self.menu.update(delta_time)

        self.gum_wrapper.on_update(delta_time)

    def on_draw(self) -> None:
        super().predraw()
        # Charm BG
        self.gum_wrapper.draw()

        # Menu
        self.menu.draw()

        arcade.draw_text(f"{self.menu.min_factor=}\n{self.menu.max_factor=}\n{self.menu.offset=}\n{self.menu.in_sin=}\n{self.menu.out_sin=}\n{self.menu.shift=}\n{self.menu.move_forward=}",
                         self.window.width, self.window.height, colors.BLACK, width = self.window.width, align = "right", anchor_x = "right", anchor_y = "top", multiline = True, font_size = 16)
        super().postdraw()