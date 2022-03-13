import logging

import arcade
from pyglet.media import Player

from charm.lib import anim
from charm.lib.adobexml import sprite_from_adobe
from charm.lib.charm import CharmColors, generate_gum_wrapper, move_gum_wrapper
from charm.lib.digiview import DigiView, shows_errors
from charm.lib.gamemodes.fnf import CameraFocusEvent, FNFEngine, FNFHighway, FNFSong
from charm.lib.settings import Settings
from charm.lib.paths import songspath

logger = logging.getLogger("charm")


class FNFSongView(DigiView):
    def __init__(self, name: str, *args, **kwargs):
        super().__init__(fade_in=1, bg_color=CharmColors.FADED_GREEN, *args, **kwargs)
        self.volume = 0.5
        self.name = name

    @shows_errors
    def setup(self):
        super().setup()

        self.path = songspath / "fnf" / self.name
        self.songdata: FNFSong = None
        diffs = ["-ex", "-hard", "", "-easy"]
        for diff in diffs:
            p = self.path / f"{self.name}{diff}.json"
            if p.exists():
                with open(self.path / f"{self.name}{diff}.json", encoding="utf-8") as chart:
                    c = chart.read()
                    self.songdata = FNFSong.parse(self.name, c)
                    break
        if not self.songdata:
            raise ValueError("No valid chart found!")
        self.highway_1 = FNFHighway(self.songdata.charts[0], (((Settings.width // 3) * 2), 0))
        self.highway_2 = FNFHighway(self.songdata.charts[1], (10, 0), auto=True)
        self.engine = FNFEngine(self.songdata.charts[0])

        self._songs: list[arcade.Sound] = []
        for f in self.path.glob("*.*"):
            if f.is_file() and f.suffix in [".ogg", ".mp3", ".wav"]:
                s = arcade.load_sound(f)
                self._songs.append(s)

        self.window.theme_song.volume = 0

        self.song_time_text = arcade.Text("??:??", (self.size[0] // 2), 10, font_size=24,
                                          anchor_x="center", color=arcade.color.BLACK,
                                          font_name="bananaslip plus plus")

        self.score_text = arcade.Text("0", (self.size[0] // 2), self.size[1] - 10, font_size=24,
                                      anchor_x="center", anchor_y="top", color=arcade.color.BLACK,
                                      font_name="bananaslip plus plus")

        self.judge_text = arcade.Text("", (self.size[0] // 2), self.size[1] // 2, font_size=48,
                                      anchor_x="center", anchor_y="center", color=arcade.color.BLACK,
                                      font_name="bananaslip plus plus")

        self.grade_text = arcade.Text("Clear", (self.size[0] // 2), self.size[1] - 135, font_size=16,
                                      anchor_x="center", anchor_y="center", color=arcade.color.BLACK,
                                      font_name="bananaslip plus plus")

        self.pause_text = arcade.Text("PAUSED", (self.size[0] // 2), (self.size[1] // 2), font_size=92,
                                      anchor_x="center", anchor_y="center", color=arcade.color.BLACK,
                                      font_name="bananaslip plus plus")

        self.dead_text = arcade.Text("DEAD.", (self.size[0] // 2), (self.size[1] // 3) * 2, font_size=64,
                                     anchor_x="center", anchor_y="center", color=arcade.color.BLACK,
                                     font_name="bananaslip plus plus")

        # Generate "gum wrapper" background
        self.logo_width, self.small_logos_forward, self.small_logos_backward = generate_gum_wrapper(self.size)

        self.last_player1_note = None
        self.last_player2_note = None
        self.last_camera_event = CameraFocusEvent(0, 2)
        self.last_spotlight_position = 0
        self.last_spotlight_change = 0
        self.go_to_spotlight_position = 0
        self.spotlight_position = 0

        self.hp_bar_length = 250

        self.key_state = [False] * 4

        self.boyfriend = sprite_from_adobe("BOYFRIEND", ["bottom", "center_x"])
        self.boyfriend.set_animation("BF idle dance")
        self.boyfriend.scale = 0.5
        self.boyfriend.right = Settings.width - 10
        self.boyfriend.bottom = 10
        self.boyfriend_anim = None
        self.boyfriend_anim_missed = False

        self.paused = False
        self.show_text = True

    @property
    def song(self):
        return self.songs[0]

    @shows_errors
    def on_show(self):
        self.songs: list[Player] = []
        for s in self._songs:
            p = arcade.play_sound(s, self.volume, looping=False)
            self.songs.append(p)
        for p in self.songs:
            p.seek(0)

    @shows_errors
    def on_key_something(self, symbol: int, modifiers: int, press: bool):
        if symbol in self.engine.mapping:
            i = self.engine.mapping.index(symbol)
            self.key_state[i] = press
            self.highway_1.strikeline[i].alpha = 255 if press else 64
        self.engine.process_keystate(self.key_state)

    @shows_errors
    def on_key_press(self, symbol: int, modifiers: int):
        match symbol:
            case arcade.key.BACKSPACE:
                self.back.setup()
                for s in self.songs:
                    s.delete()
                self.window.show_view(self.back)
                arcade.play_sound(self.window.sounds["back"])
            case arcade.key.SPACE:
                self.paused = not self.paused
                for s in self.songs:
                    s.pause() if self.paused else s.play()
                for s in self.songs:
                    s.seek(self.song.time)
            case arcade.key.EQUAL:
                self.song.seek(self.song.time + 5)
            case arcade.key.MINUS:
                self.song.seek(self.song.time - 5)
            case arcade.key.T:
                self.show_text = not self.show_text
            case arcade.key.S:
                for s in self.songs:
                    s.pause()
                for s in self.songs:
                    s.play()
                for s in self.songs:
                    s.seek(self.song.time)

        self.on_key_something(symbol, modifiers, True)
        return super().on_key_press(symbol, modifiers)

    @shows_errors
    def on_key_release(self, symbol: int, modifiers: int):
        self.on_key_something(symbol, modifiers, False)
        return super().on_key_release(symbol, modifiers)

    @shows_errors
    def on_update(self, delta_time):
        super().on_update(delta_time)

        if not self.songs:
            return

        self.engine.update(self.song.time)

        # TODO: Lag? Maybe not calculate this every tick?
        # The only way to solve this I think is to create something like an
        # on_note_valid and on_note_expired event, which you can do with
        # Arcade.schedule() if we need to look into that.
        self.engine.calculate_score()

        move_gum_wrapper(self.logo_width, self.small_logos_forward, self.small_logos_backward, delta_time)

        time = f"{int(self.song.time // 60)}:{int(self.song.time % 60):02}"
        if self.song_time_text._label.text != time:
            self.song_time_text._label.text = time
        if self.score_text._label.text != str(self.engine.score):
            self.score_text._label.text = str(self.engine.score)
        if self.judge_text._label.text != self.engine.latest_judgement:
            self.judge_text._label.text = self.engine.latest_judgement

        self.get_spotlight_position(self.song.time)

        self.highway_1.update(self.song.time)
        self.highway_2.update(self.song.time)

        self.judge_text.y = anim.ease_circout((self.size[1] // 2) + 20, self.size[1] // 2, self.engine.latest_judgement_time, self.engine.latest_judgement_time + 0.25, self.engine.chart_time)
        if self.engine.accuracy:
            if self.grade_text._label.text != f"{self.engine.fc_type} | {round(self.engine.accuracy * 100, 2)}% ({self.engine.grade})":
                self.grade_text._label.text = f"{self.engine.fc_type} | {round(self.engine.accuracy * 100, 2)}% ({self.engine.grade})"

        if (self.engine.last_p1_note, self.engine.last_note_missed) != (self.boyfriend_anim, self.boyfriend_anim_missed):
            # logger.debug(f"animation changed from {(self.engine.last_p1_note, self.engine.last_note_missed)} to {(self.boyfriend_anim, self.boyfriend_anim_missed)}")
            if self.engine.last_p1_note is None:
                self.boyfriend.set_animation("BF idle dance")
                self.boyfriend_anim = None
            else:
                a = ""
                match self.engine.last_p1_note:
                    case 0:
                        a = "BF NOTE LEFT"
                        self.boyfriend_anim = self.engine.last_p1_note
                    case 1:
                        a = "BF NOTE DOWN"
                        self.boyfriend_anim = self.engine.last_p1_note
                    case 2:
                        a = "BF NOTE UP"
                        self.boyfriend_anim = self.engine.last_p1_note
                    case 3:
                        a = "BF NOTE RIGHT"
                        self.boyfriend_anim = self.engine.last_p1_note
                if self.engine.last_note_missed:
                    a += " MISS"
                    self.boyfriend_anim_missed = True
                else:
                    self.boyfriend_anim_missed = False
                self.boyfriend.set_animation(a)

        self.boyfriend.update_animation(delta_time)

    def get_spotlight_position(self, song_time: float):
        focus_pos = {
            2: Settings.width // 2,
            1: 0
        }
        cameraevents = [e for e in self.songdata.events if isinstance(e, CameraFocusEvent) and e.time < self.song.time + 0.25]
        if cameraevents:
            current_camera_event = cameraevents[-1]
            if self.last_camera_event != current_camera_event:
                self.last_spotlight_change = song_time
                self.last_spotlight_position = self.spotlight_position
                self.go_to_spotlight_position = focus_pos[current_camera_event.focused_player]
                self.last_camera_event = current_camera_event
        self.spotlight_position = anim.ease_circout(self.last_spotlight_position, self.go_to_spotlight_position, self.last_spotlight_change, self.last_spotlight_change + 0.125, song_time)

    def hp_draw(self):
        hp_min = self.size[0] // 2 - self.hp_bar_length // 2
        hp_max = self.size[0] // 2 + self.hp_bar_length // 2
        hp_normalized = anim.time_to_zero_one_ramp(self.engine.min_hp, self.engine.max_hp, self.engine.hp)
        hp = anim.zero_one_to_range(hp_min, hp_max, hp_normalized)
        arcade.draw_lrtb_rectangle_filled(
            hp_min, hp_max,
            self.size[1] - 100, self.size[1] - 110,
            arcade.color.BLACK
        )
        arcade.draw_circle_filled(hp, self.size[1] - 105, 20, arcade.color.BLUE)

    def spotlight_draw(self):
        arcade.draw_lrtb_rectangle_filled(
            self.spotlight_position, self.spotlight_position + Settings.width // 2, Settings.height, 0,
            arcade.color.BLACK + (127,)
        )

    @shows_errors
    def on_draw(self):
        self.clear()
        self.camera.use()

        # Charm BG
        self.small_logos_forward.draw()
        self.small_logos_backward.draw()

        self.boyfriend.draw()

        if self.show_text:
            self.song_time_text.draw()
            self.score_text.draw()
            self.judge_text.draw()
            self.grade_text.draw()
            if self.engine.has_died:
                self.dead_text.draw()

        if self.paused:
            self.pause_text.draw()

        self.hp_draw()

        self.highway_2.draw()
        self.spotlight_draw()
        self.highway_1.draw()

        super().on_draw()
