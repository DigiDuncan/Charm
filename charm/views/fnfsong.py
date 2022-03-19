import logging

import arcade
from pyglet.media import Player

from charm.lib import anim
from charm.lib.adobexml import sprite_from_adobe
from charm.lib.charm import CharmColors, generate_gum_wrapper, move_gum_wrapper
from charm.lib.digiview import DigiView, shows_errors
from charm.lib.gamemodes.fnf2 import CameraFocusEvent, FNFEngine, FNFHighway, FNFSong
from charm.lib.settings import Settings
from charm.lib.paths import songspath

logger = logging.getLogger("charm")


class TrackCollection:
    def __init__(self):
        self.tracks = list[Player]

    def load(self, sounds):
        self.tracks = []
        for s in sounds:
            t = arcade.play_sound(s, self.volume, looping=False)
            self.tracks.append(t)
        self.sync()

    @property
    def time(self):
        return self.tracks[0].time

    def seek(self, time):
        for t in self.tracks:
            t.seek(time)

    def play(self):
        for t in self.tracks:
            t.play()
    
    def pause(self):
        for t in self.tracks:
            t.pause()

    @property
    def out_of_sync(self):
        return any(abs(t.time - self.time) > 0.01 for t in self.tracks[1:])

    def sync(self):
        if self.out_of_sync:
            raise Exception(f"Tracks are out of sync by more than 10ms!")
        for t in self.tracks[1:]:
            t.seek(self.time)

    def close(self):
        for t in self.tracks:
            t.delete()
        self.tracks = []

    @property
    def loaded(self):
        return bool(self.tracks)


class FNFSongView(DigiView):
    def __init__(self, name: str, *args, **kwargs):
        super().__init__(fade_in=1, bg_color=CharmColors.FADED_GREEN, *args, **kwargs)
        self.volume = 0.5
        self.name = name
        self.tracks = TrackCollection()

    def setup(self):
        super().setup()

        self.path = songspath / "fnf" / self.name
        self.songdata = FNFSong.parse(self.path)
        if not self.songdata:
            raise ValueError("No valid chart found!")
        self.highway_1 = FNFHighway(self.songdata.charts[0], (((Settings.width // 3) * 2), 0))
        self.highway_2 = FNFHighway(self.songdata.charts[1], (10, 0), auto=True)
        self.engine = FNFEngine(self.songdata.charts[0])

        self.trackfiles: list[arcade.Sound] = []
        for f in self.path.glob("*.*"):
            if f.is_file() and f.suffix in [".ogg", ".mp3", ".wav"]:
                s = arcade.load_sound(f)
                self.trackfiles.append(s)

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

    @shows_errors
    def on_show(self):
        self.tracks.load(self.trackfiles)

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
                self.tracks.close()
                self.window.show_view(self.back)
                arcade.play_sound(self.window.sounds["back"])
            case arcade.key.SPACE:
                self.paused = not self.paused
                self.tracks.pause() if self.paused else self.tracks.play()
                self.tracks.sync()
            case arcade.key.EQUAL:
                self.tracks.seek(self.tracks.time + 5)
            case arcade.key.MINUS:
                self.tracks.seek(self.tracks.time - 5)
            case arcade.key.T:
                self.show_text = not self.show_text
            case arcade.key.S:
                self.tracks.pause()
                self.tracks.sync()
                self.tracks.play()

        self.on_key_something(symbol, modifiers, True)
        return super().on_key_press(symbol, modifiers)

    @shows_errors
    def on_key_release(self, symbol: int, modifiers: int):
        self.on_key_something(symbol, modifiers, False)
        return super().on_key_release(symbol, modifiers)

    @shows_errors
    def on_update(self, delta_time):
        super().on_update(delta_time)

        if not self.tracks.loaded:
            return

        self.engine.update(self.tracks.time)

        # TODO: Lag? Maybe not calculate this every tick?
        # The only way to solve this I think is to create something like an
        # on_note_valid and on_note_expired event, which you can do with
        # Arcade.schedule() if we need to look into that.
        self.engine.calculate_score()

        move_gum_wrapper(self.logo_width, self.small_logos_forward, self.small_logos_backward, delta_time)

        time = f"{int(self.tracks.time // 60)}:{int(self.tracks.time % 60):02}"
        if self.song_time_text._label.text != time:
            self.song_time_text._label.text = time
        if self.score_text._label.text != str(self.engine.score):
            self.score_text._label.text = str(self.engine.score)
        if self.judge_text._label.text != self.engine.latest_judgement:
            self.judge_text._label.text = self.engine.latest_judgement

        self.get_spotlight_position(self.tracks.time)

        self.highway_1.update(self.tracks.time)
        self.highway_2.update(self.tracks.time)

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
        cameraevents = [e for e in self.songdata.events if isinstance(e, CameraFocusEvent) and e.time < self.tracks.time + 0.25]
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
