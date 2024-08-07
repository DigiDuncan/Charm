import logging
from math import ceil
from pathlib import Path

import arcade
from arcade import Sprite, Texture, Text, Sound, color as colors

import ndjson

from charm.lib.anim import ease_circout, perc
from charm.lib.charm import GumWrapper
from charm.lib.digiview import DigiView, disable_when_focus_lost, shows_errors
from charm.lib.errors import NoChartsError
from charm.lib.gamemodes.four_key import FourKeyHighway, FourKeyEngine
from charm.lib.gamemodes.sm import SMEngine, SMSong
from charm.lib.keymap import keymap
from charm.lib.logsection import LogSection
from charm.lib.modchart import Modchart, ModchartProcessor
from charm.lib.oggsound import OGGSound
from charm.lib.trackcollection import TrackCollection
from charm.views.results import ResultsView

logger = logging.getLogger("charm")


class FourKeySongView(DigiView):
    def __init__(self, path: Path, back: DigiView):
        super().__init__(fade_in=1, back=back)
        self.song_path = path
        self.tracks: TrackCollection = None
        self.highway: FourKeyHighway = None
        self.engine: FourKeyEngine = None
        self.countdown: float = 3
        self.countdown_over = False

    @shows_errors
    def setup(self) -> None:
        super().presetup()

        with LogSection(logger, "loading audio"):
            audio_paths = [a for a in self.song_path.glob("*.mp3")] + [a for a in self.song_path.glob("*.wav")] + [a for a in self.song_path.glob("*.ogg")]
            trackfiles = []
            for s in audio_paths:
                trackfiles.append(OGGSound(s) if s.suffix == ".ogg" else Sound(s))
            self.tracks = TrackCollection([Sound(s) for s in audio_paths])

        with LogSection(logger, "loading song data"):
            self.sm_song = SMSong.parse(self.song_path)
            for diff in ["Edit", "Challenge", "Expert", "Difficult", "Hard", "Basic", "Medium", "Beginner", "Easy"]:
                self.chart = self.sm_song.get_chart(diff)
                if self.chart is not None:
                    break
            if self.chart is None:
                logger.warn(str([c.difficulty for c in self.sm_song.charts]))
                raise NoChartsError(self.sm_song.metadata.title)

        with LogSection(logger, "loading engine"):
            self.engine = SMEngine(self.chart)

        with LogSection(logger, "loading highway"):
            self.highway = FourKeyHighway(self.chart, self.engine, (0, 0))

        self.text = Text("[LOADING]", -5, self.window.height - 5, color = colors.BLACK, font_size = 24, align = "right", anchor_y="top", font_name = "bananaslip plus", width = self.window.width, multiline = True)
        self.countdown_text = Text("0", *self.window.center, colors.BLACK, 72, align="center", anchor_x="center", anchor_y="center", font_name = "bananaslip plus", width = 100)

        with LogSection(logger, "loading judgements"):
            judgement_textures: list[Texture] = [j.get_texture() for j in self.engine.judgements]
            self.judgement_sprite = Sprite(judgement_textures[0])
            self.judgement_sprite.textures = judgement_textures
            self.judgement_sprite.scale = (self.highway.w * 0.8) / self.judgement_sprite.width
            self.judgement_sprite.center_x = self.window.center_x
            self.judgement_sprite.center_y = self.window.height / 4
            self.judgement_jump_pos = self.judgement_sprite.center_y + 25
            self.judgement_land_pos = self.judgement_sprite.center_y
            self.judgement_sprite.alpha = 0

        self.window.presence.set("Playing 4K")

        if (self.song_path / "modchart.ndjson").exists():
            with open(self.song_path / "modchart.ndjson") as p:
                md = ndjson.load(p)
            modchart = Modchart.from_NDJSON(md)
            self.modchart_processor = ModchartProcessor(modchart, self)
        else:
            self.modchart_processor = None

        # Generate "gum wrapper" background
        self.gum_wrapper = GumWrapper()  # noqa: F821

        self.success = True

        super().postsetup()

    def on_show_view(self) -> None:
        self.window.theme_song.volume = 0
        if self.success is False:
            self.window.show_view(self.back)
            self.window.theme_song.volume = 0.25
        self.countdown = 4
        super().on_show_view()

    def generate_data_string(self) -> str:
        return (f"Time: {int(self.tracks.time // 60)}:{int(self.tracks.time % 60):02}\n"
                f"Score: {self.engine.score}\n"
                f"Acc: {self.engine.accuracy:.2%} ({self.engine.grade})\n"
                f"Avg. DT: {self.engine.average_acc * 1000:.2f}ms\n"
                f"{self.engine.fc_type}\n"
                f"Streak: {self.engine.streak}")

    @shows_errors
    @disable_when_focus_lost(keyboard=True)
    def on_key_press(self, symbol: int, modifiers: int) -> None:
        super().on_key_press(symbol, modifiers)
        if keymap.back.pressed:
            self.go_back()
        elif keymap.pause.pressed:
            if self.countdown <= 0:
                self.tracks.pause() if self.tracks.playing else self.tracks.play()
        elif keymap.seek_zero.pressed:
            self.tracks.seek(0)
        elif keymap.seek_backward.pressed:
            self.tracks.seek(self.tracks.time - 5)
        elif keymap.seek_forward.pressed:
            self.tracks.seek(self.tracks.time + 5)
        elif self.window.debug.enabled and keymap.debug_toggle_hit_window.pressed:
            self.highway.show_hit_window = not self.highway.show_hit_window
        elif self.window.debug.enabled and keymap.debug_show_results.pressed:
            self.show_results()

        if self.tracks.playing:
            self.engine.on_key_press(symbol, modifiers)

    @shows_errors
    def on_key_release(self, symbol: int, modifiers: int) -> None:
        super().on_key_release(symbol, modifiers)
        if self.tracks.playing:
            self.engine.on_key_release(symbol, modifiers)

    def go_back(self) -> None:
        self.tracks.close()
        super().go_back()

    def show_results(self) -> None:
        self.tracks.close()
        results_view = ResultsView(back=self.back, results=self.engine.generate_results())
        results_view.setup()
        self.window.show_view(results_view)

    def on_resize(self, width: int, height: int) -> None:
        super().on_resize(width, height)
        self.highway.pos = (0, 0)
        self.highway.x += self.window.center_x - self.highway.w // 2  # center the highway
        self.highway.hit_window_top = self.highway.note_y(-self.engine.judgements[-2].seconds)
        self.highway.hit_window_bottom = self.highway.note_y(self.engine.judgements[-2].seconds)
        self.text.position = (-5, self.window.height - 5)
        self.countdown_text.position = self.window.center
        self.judgement_sprite.center_x = self.window.center_x
        self.judgement_sprite.center_y = self.window.height / 4

    def on_update(self, delta_time: float) -> None:
        super().on_update(delta_time)

        if not self.tracks.loaded:
            return

        self.highway.update(0 - self.countdown if not self.countdown_over else self.tracks.time)
        self.engine.update(self.tracks.time)
        if self.modchart_processor:
            self.modchart_processor.process_modchart()

        # TODO: Lag? Maybe not calculate this every tick?
        # The only way to solve this I think is to create something like an
        # on_note_valid and on_note_expired event, which you can do with
        # Arcade.schedule() if we need to look into that.
        # 2023-12-25: This doesn't seem to lag that bad. Maybe profile it but eh.
        self.engine.calculate_score()

        # Judgement
        judgement_index = self.engine.judgements.index(self.engine.latest_judgement) if self.engine.latest_judgement else 0
        judgement_time = self.engine.latest_judgement_time
        if judgement_time:
            self.judgement_sprite.center_y = ease_circout(self.judgement_jump_pos, self.judgement_land_pos, perc(judgement_time, judgement_time + 0.25, self.tracks.time))
            self.judgement_sprite.alpha = int(ease_circout(255, 0, perc(judgement_time + 0.5, judgement_time + 1, self.tracks.time)))
            self.judgement_sprite.set_texture(judgement_index)

        data_string = self.generate_data_string()
        if self.text.text != data_string:
            self.text.text = data_string

        if self.countdown > 0:
            self.countdown -= delta_time
            if self.countdown < 0:
                self.countdown = 0
            self.countdown_text.text = str(ceil(self.countdown))

        if self.countdown <= 0 and not self.countdown_over:
            self.tracks.play()
            self.countdown_over = True

        if self.tracks.time >= self.tracks.duration:
            self.show_results()

        self.gum_wrapper.on_update(delta_time)

    def on_draw(self) -> None:
        super().predraw()
        self.gum_wrapper.draw()

        self.highway.draw()
        arcade.draw_sprite(self.judgement_sprite)

        self.text.draw()

        if self.countdown > 0:
            self.countdown_text.draw()
        super().postdraw()
