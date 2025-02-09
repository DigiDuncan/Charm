import logging

from charm.core.charm import GumWrapper
from charm.core.digiview import DigiView, shows_errors, disable_when_focus_lost
from charm.core.keymap import KeyMap

from charm.ui.settings.settings_menu import SettingsMenuElement
logger = logging.getLogger("charm")


class SettingsView(DigiView):
    def __init__(self, back: DigiView):
        super().__init__(fade_in=1, back=back)
        self.element = SettingsMenuElement()
        self.element.bounds = self.window.rect

    def on_resize(self, width: int, height: int) -> None:
        super().on_resize(width, height)
        self.element.bounds = self.window.rect

    @shows_errors
    def setup(self) -> None:
        super().presetup()
        super().postsetup()

    def on_show_view(self) -> None:
        self.window.theme_song.volume = 0

    @shows_errors
    def on_button_press(self, keymap: KeyMap) -> None:
        if keymap.back.pressed:
            self.go_back()

    @shows_errors
    def on_button_release(self, keymap: KeyMap) -> None:
        pass

    @shows_errors
    def on_update(self, delta_time: float) -> None:
        super().on_update(delta_time)
        self.wrapper.update(delta_time)

    @shows_errors
    def on_draw(self) -> None:
        super().predraw()
        # Charm BG
        self.wrapper.draw()
        self.element.draw()
        super().postdraw()

