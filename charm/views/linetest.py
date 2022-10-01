import arcade

from charm.lib.charm import CharmColors, generate_gum_wrapper, move_gum_wrapper
from charm.lib.digiview import DigiView
from charm.lib.settings import Settings
from charm.objects.line_renderer import NoteTrail


class LineTestView(DigiView):
    def __init__(self, *args, **kwargs):
        super().__init__(fade_in=1, bg_color=CharmColors.FADED_GREEN, *args, **kwargs)
        self.song = None
        self.volume = 1

        self.note_trail: NoteTrail = None
        self.time_text: arcade.Text = None

    def setup(self):
        super().setup()
        
        self.note_trail = NoteTrail(123456789, (Settings.width / 2, Settings.height - 50), 0, 12, 50,
                          arcade.color.PURPLE, upscroll = True, fill_color=(0, 0, 0, 60), resolution=5, simple=False)

        self.time_text = arcade.Text("0.00", Settings.width - 5, Settings.height - 5, arcade.color.BLUE,
                                     24, Settings.width - 5, align="right", anchor_x="right", anchor_y="top")

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
            case arcade.key.R:
                self.setup()

        return super().on_key_press(symbol, modifiers)

    def on_update(self, delta_time):
        super().on_update(delta_time)
        self.note_trail.update(delta_time)

        self.time_text.text = str(round(self.local_time, 2))

        if self.window.keyboard[arcade.key.LEFT]:
            self.note_trail.move_from_now(-1, 0)
        if self.window.keyboard[arcade.key.RIGHT]:
            self.note_trail.move_from_now(1, 0)

        move_gum_wrapper(self.logo_width, self.small_logos_forward, self.small_logos_backward, delta_time)

    def on_draw(self):
        self.clear()
        self.camera.use()

        # Charm BG
        self.small_logos_forward.draw()
        self.small_logos_backward.draw()

        self.note_trail.draw()

        self.time_text.draw()

        super().on_draw()
