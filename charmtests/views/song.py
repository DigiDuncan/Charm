import arcade

from charmtests.lib.charm import CharmColors, generate_gum_wrapper, move_gum_wrapper
from charmtests.lib.digiview import DigiView
from charmtests.objects.song import Song

class SongView(DigiView):
    def __init__(self, song: Song, *args, **kwargs):
        super().__init__(fade_in=1,
        bg_color=CharmColors.FADED_GREEN,
        show_fps=True, *args, **kwargs)
        
        self.main_sprites = None
        self.volume = 0.5
        self.songdata = song

    def setup(self):
        super().setup()

        # Generate "gum wrapper" background
        self.logo_width, self.small_logos_forward, self.small_logos_backward = generate_gum_wrapper(self.size)

        self.title_label = arcade.Text(self.songdata.title,
                          font_name='bananaslip plus plus',
                          font_size=60,
                          start_x=self.window.width//2, start_y=self.window.height//2,
                          anchor_x='center', anchor_y='bottom',
                          color = CharmColors.PURPLE + (0xFF,))

        self.artistalbum_label = arcade.Text(self.songdata.artist + " - " + self.songdata.album,
                          font_name='bananaslip plus plus',
                          font_size=40,
                          start_x=self.window.width//2, start_y=self.window.height//2,
                          anchor_x='center', anchor_y='top',
                          color = CharmColors.PURPLE + (0xFF,))

    def on_key_press(self, symbol: int, modifiers: int):
        match symbol:
            case arcade.key.BACKSPACE:
                self.window.show_view(self.back)
                arcade.play_sound(self.window.sounds["back"])
            case arcade.key.KEY_7:
                self.window.debug = not self.window.debug
                if self.window.debug:
                    self.camera.scale = 2
                else:
                    self.camera.scale = 1
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

        self.title_label.draw()
        self.artistalbum_label.draw()

        super().on_draw()
