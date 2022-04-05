from dataclasses import dataclass
import importlib.resources as pkg_resources

import arcade
import librosa
import nindex
from numpy import ndarray

import charm.data.audio
from charm.lib.anim import ease_linear
from charm.lib.digiview import DigiView
from charm.lib.settings import Settings


@dataclass
class SoundPoint:
    time: float
    amplitude: float


@dataclass
class Beat:
    time: float


class VisualizerView(DigiView):
    def __init__(self, *args, **kwargs):
        super().__init__(fade_in=1, bg_color=arcade.color.BLACK, *args, **kwargs)

    def setup(self):
        super().setup()
        with pkg_resources.path(charm.data.audio, "fourth_wall.wav") as p:
            self._song = arcade.load_sound(p)
            load = librosa.load(p, mono=True)
        self.waveform: ndarray[float] = load[0]
        self.sample_rate: int = load[1]

        samples: list[SoundPoint] = []
        for n, s in enumerate(self.waveform):
            samples.append(SoundPoint((1 / self.sample_rate) * n, s))
        self.samples = nindex.Index(samples, "time")

        self.bpm, beats = librosa.beat.beat_track(self.waveform, self.sample_rate, units="time")
        self.beats = nindex.Index([Beat(t) for t in beats[::2]], "time")

        self.multiplier = 250
        self.y = Settings.height // 2
        self.line_width = 1
        self.x_scale = 2
        self.beat_time = 0.5

        self.pixels: list[tuple[int, int]] = [(0, 0) * Settings.width]
        self.last_beat = -self.beat_time

    def on_show(self):
        self.window.theme_song.volume = 0
        self.song = arcade.play_sound(self._song, 1, looping=False)
        super().on_show()

    def on_update(self, delta_time: float):
        super().on_update(delta_time)
        if not self.shown:
            return
        time = self.song.time
        sample_index: SoundPoint = self.samples.lt_index(time)
        if sample_index:
            samples = self.samples.items[sample_index-(Settings.width*self.x_scale-1):sample_index+1:self.x_scale]
            self.pixels = [(n, (s.amplitude * self.multiplier + self.y)) for n, s in enumerate(samples)]
        last_beat: Beat = self.beats.lt(self.song.time)
        if last_beat:
            self.last_beat = last_beat.time

    def on_key_press(self, symbol: int, modifiers: int):
        match symbol:
            case arcade.key.BACKSPACE:
                self.back.setup()
                self.window.show_view(self.back)
                self.song.delete()
                arcade.play_sound(self.window.sounds["back"])

        return super().on_key_press(symbol, modifiers)

    def on_draw(self):
        self.clear()
        self.camera.use()
        if not self.shown:
            return
        flash = int(ease_linear(255, 0, self.last_beat, self.last_beat + self.beat_time, self.song.time))
        green_amount = int(ease_linear(0, 255, self.last_beat, self.last_beat + self.beat_time, self.song.time))
        arcade.draw_lrtb_rectangle_filled(
            0, Settings.width, Settings.height, 0,
            (0, 255, 255, flash)
        )
        line_color = (0, green_amount, 0, 255)
        arcade.draw_line_strip(self.pixels, line_color, self.line_width)

        super().on_draw()
