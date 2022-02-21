from itertools import cycle
import arcade
from charm.lib.adobexml import sprite_from_adobe

from charm.lib.charm import CharmColors, generate_gum_wrapper, move_gum_wrapper
from charm.lib.digiview import DigiView
from charm.lib.settings import Settings


class SpriteTestView(DigiView):
    def __init__(self, *args, **kwargs):
        super().__init__(fade_in=1, bg_color=CharmColors.FADED_GREEN, *args, **kwargs)

    def setup(self):
        super().setup()

        self.sprite = sprite_from_adobe("BOYFRIEND")
        self.sprite.bottom = 0
        self.sprite.left = 0
        self.sprite.set_animation("boyfriend attack")
        self.anims = cycle(self.sprite.animations)
        self.anim_label = arcade.Text("", Settings.width // 2, Settings.height, font_size = 24, color = arcade.color.BLACK, anchor_x="center", anchor_y="top")

        # Generate "gum wrapper" background
        self.logo_width, self.small_logos_forward, self.small_logos_backward = generate_gum_wrapper(self.size)

    def on_key_press(self, symbol: int, modifiers: int):
        match symbol:
            case arcade.key.BACKSPACE:
                self.back.setup()
                self.window.show_view(self.back)
                arcade.play_sound(self.window.sounds["back"])
            case arcade.key.ENTER:
                a = next(self.anims)
                self.sprite.set_animation(a)
                self.anim_label.value = a

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

        self.sprite.draw()
        self.anim_label.draw()

        super().on_draw()
