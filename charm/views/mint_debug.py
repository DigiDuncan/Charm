import logging

from charm.core.digiview import DigiView, shows_errors
from charm.core.keymap import KeyMap

from charm.lib.too_mini_too_mint import Element, AnchorPresets, Offsets, debug_draw_element
from arcade import LRBT, Sprite, draw_sprite

from importlib.resources import files
import charm.data.images.debug as imgs

logger = logging.getLogger("charm")


class MintView(DigiView):
    def __init__(self, back: DigiView):
        super().__init__(fade_in=1, back=back)
        self.deboobop = Sprite(files(imgs) / "menu_layout_test_blur.png", 1.0, self.center_x, self.center_y)

        self.root = Element()
        self.root.set_bounds(self.window.rect)

        self.list = Element()
        self.list.anchors = LRBT(0.0, 2.0/3.0, 0.0, 1.0)
        self.root.add_child(self.list)

        self.panel = Element()
        self.panel.anchors = LRBT(2.0/3.0, 1.0, 0.0, 1.0)
        self.root.add_child(self.panel)

    @shows_errors
    def setup(self) -> None:
        super().presetup()
        super().postsetup()

    @shows_errors
    def on_resize(self, width: int, height: int) -> None:
        super().on_resize(width, height)
        self.root.set_bounds(self.window.rect)
        self.root.recompute_layout(waterfall=True)

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
        draw_sprite(self.deboobop)

        debug_draw_element(self.root)

        super().postdraw()
