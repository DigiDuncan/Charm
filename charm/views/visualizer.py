import importlib.resources as pkg_resources

import arcade
import librosa

import charm.data.audio
from charm.lib.digiview import DigiView

class VisualizerView(DigiView):
    def __init__(self, *args, **kwargs):
        super().__init__(fade_in=1, bg_color=arcade.color.BLACK, *args, **kwargs)

    def setup(self):
        with pkg_resources.path(charm.data.audio, "song.mp3") as p:
            self._song = arcade.load_sound(p)
            self.waveform, self.sample_rate = librosa.load(p)
        super().setup()

    def on_show(self):
        super().on_show()
        self.window.theme_song.volume = 0
        self.song = arcade.play_sound(self._song, self.volume, looping=False)

    def on_update(self, delta_time: float):
        return super().on_update(delta_time)

    def on_key_press(self, symbol: int, modifiers: int):
        match symbol:
            case arcade.key.BACKSPACE:
                self.back.setup()
                self.window.show_view(self.back)
                arcade.play_sound(self.window.sounds["back"])

        return super().on_key_press(symbol, modifiers)

    def on_draw(self):
        self.clear()
        self.camera.use()

        super().on_draw()
