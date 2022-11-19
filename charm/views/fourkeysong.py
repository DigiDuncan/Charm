import logging
from math import ceil
from pathlib import Path

import arcade

from charm.lib.anim import ease_linear, ease_circout
from charm.lib.charm import CharmColors, generate_gum_wrapper, move_gum_wrapper
from charm.lib.digiview import DigiView, shows_errors
from charm.lib.gamemodes.four_key import FourKeySong, FourKeyHighway, FourKeyEngine
from charm.lib.logsection import LogSection
from charm.lib.trackcollection import TrackCollection

logger = logging.getLogger("charm")


class FourKeySongView(DigiView):
    def __init__(self, path: Path, *args, **kwargs):
        super().__init__(fade_in=1, bg_color=CharmColors.FADED_GREEN, *args, **kwargs)
        self.song_path = path
        self.tracks: TrackCollection = None
        self.highway: FourKeyHighway = None
        self.engine: FourKeyEngine = None
        self.volume = 0.25
        self.countdown: float = 3
        self.countdown_over = False

    def setup(self):
        super().setup()

        with LogSection(logger, "loading audio"):
            audio_paths = [a for a in self.song_path.glob("*.mp3")] + [a for a in self.song_path.glob("*.wav")] + [a for a in self.song_path.glob("*.ogg")]
            self.tracks = TrackCollection([arcade.load_sound(s) for s in audio_paths])

        with LogSection(logger, "loading song data"):
            self.sm_song = FourKeySong.parse(self.song_path)
            self.chart = self.sm_song.get_chart("Challenge")

        with LogSection(logger, "loading engine"):
            self.engine = FourKeyEngine(self.chart)
            self.key_state = [False] * 4

        with LogSection(logger, "loading highway"):
            self.highway = FourKeyHighway(self.chart, (0, 0))
            self.highway.x += self.window.width // 2 - self.highway.w // 2  # center the highway
            self.highway.hit_window_top = self.highway.note_y(-self.engine.judgements[-2].seconds)
            self.highway.hit_window_bottom = self.highway.note_y(self.engine.judgements[-2].seconds)

        self.text = arcade.Text("[LOADING]", -5, self.window.height - 5, color = arcade.color.BLACK, font_size = 24, align = "right", anchor_y="top", font_name = "bananaslip plus plus", width = self.window.width)
        self.countdown_text = arcade.Text("0", self.window.width / 2, self.window.height / 2, arcade.color.BLACK, 72, align="center", anchor_x="center", anchor_y="center", font_name = "bananaslip plus plus", width = 100)

        with LogSection(logger, "loading judgements"):
            judgement_textures: list[arcade.Texture] = [j.get_texture() for j in self.engine.judgements]
            self.judgement_sprite = arcade.Sprite(texture = judgement_textures[0])
            self.judgement_sprite.textures = judgement_textures
            self.judgement_sprite.scale = (self.highway.w * 0.8) / self.judgement_sprite.width
            self.judgement_sprite.center_x = self.window.width / 2
            self.judgement_sprite.center_y = self.window.height / 4
            self.judgement_jump_pos = self.judgement_sprite.center_y + 25
            self.judgement_land_pos = self.judgement_sprite.center_y
            self.judgement_sprite.alpha = 0

        # Generate "gum wrapper" background
        self.logo_width, self.small_logos_forward, self.small_logos_backward = generate_gum_wrapper(self.size)
        self.success = True

    @shows_errors
    def on_show_view(self):
        self.window.theme_song.volume = 0
        if self.success is False:
            self.window.show_view(self.back)
            self.window.theme_song.volume = 0.25
        self.countdown = 3
        super().on_show()

    @shows_errors
    def on_key_something(self, symbol: int, modifiers: int, press: bool):
        if symbol in self.engine.mapping:
            i = self.engine.mapping.index(symbol)
            self.key_state[i] = press
            self.highway.strikeline[i].alpha = 255 if press else 64
        self.engine.process_keystate(self.key_state)

    def generate_data_string(self):
        return (f"Time: {int(self.tracks.time // 60)}:{int(self.tracks.time % 60):02}\n"
                f"Score: {self.engine.score}\n"
                f"Acc: {self.engine.accuracy:.2%} ({self.engine.grade})\n"
                f"Avg. DT: {self.engine.average_acc * 1000:.2f}ms\n"
                f"{self.engine.fc_type}\n"
                f"Streak: {self.engine.streak}")
         
    @shows_errors
    def on_key_press(self, symbol: int, modifiers: int):
        match symbol:
            case arcade.key.BACKSPACE:
                self.tracks.close()
                self.back.setup()
                self.window.show_view(self.back)
                arcade.play_sound(self.window.sounds["back"])
            case arcade.key.SPACE:
                if self.countdown <= 0:
                    self.tracks.pause() if self.tracks.playing else self.tracks.play()
            case arcade.key.KEY_0:
                self.tracks.seek(0)
            case arcade.key.MINUS:
                self.tracks.seek(self.tracks.time - 5)
            case arcade.key.EQUAL:
                self.tracks.seek(self.tracks.time + 5)
        if self.window.debug:
            if modifiers & arcade.key.MOD_SHIFT:
                match symbol:
                    case arcade.key.H:
                        self.highway.show_hit_window = not self.highway.show_hit_window

        self.on_key_something(symbol, modifiers, True)
        return super().on_key_press(symbol, modifiers)

    @shows_errors
    def on_key_release(self, symbol: int, modifiers: int):
        self.on_key_something(symbol, modifiers, False)
        return super().on_key_release(symbol, modifiers)

    def on_update(self, delta_time):
        super().on_update(delta_time)

        if not self.tracks.loaded:
            return

        self.highway.update(0 - self.countdown if not self.countdown_over else self.tracks.time)
        self.engine.update(self.tracks.time)

        # TODO: Lag? Maybe not calculate this every tick?
        # The only way to solve this I think is to create something like an
        # on_note_valid and on_note_expired event, which you can do with
        # Arcade.schedule() if we need to look into that.
        self.engine.calculate_score()

        # Judgement
        judgement_index = self.engine.judgements.index(self.engine.latest_judgement) if self.engine.latest_judgement else 0
        judgement_time = self.engine.latest_judgement_time
        if judgement_time:
            self.judgement_sprite.center_y = ease_circout(self.judgement_jump_pos, self.judgement_land_pos, judgement_time, judgement_time + 0.25, self.tracks.time)
            self.judgement_sprite.alpha = ease_circout(255, 0, judgement_time + 0.5, judgement_time + 1, self.tracks.time)
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

        move_gum_wrapper(self.logo_width, self.small_logos_forward, self.small_logos_backward, delta_time)

    def on_draw(self):
        self.clear()
        self.camera.use()

        # Charm BG
        self.small_logos_forward.draw()
        self.small_logos_backward.draw()

        self.highway.draw()
        self.judgement_sprite.draw()

        self.text.draw()

        if self.countdown > 0:
            self.countdown_text.draw()

        super().on_draw()