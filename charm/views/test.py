import importlib.resources as pkg_resources
import logging

import arcade

from charm.lib import anim
from charm.lib.charm import CharmColors, generate_gum_wrapper, move_gum_wrapper
from charm.lib.digiview import DigiView
from charm.lib.gamemodes.fnf import CameraFocusEvent, FNFEngine, FNFHighway, FNFSong
from charm.lib.settings import Settings
import charm.data.charts.fnf

logger = logging.getLogger("charm")


class TestView(DigiView):
    def __init__(self, *args, **kwargs):
        super().__init__(fade_in=1, bg_color=CharmColors.FADED_GREEN, *args, **kwargs)
        self.volume = 1

    def setup(self):
        super().setup()

        c = pkg_resources.read_text(charm.data.charts.fnf, "ballistic.json")
        self.songdata = FNFSong.parse(c)
        self.highway_1 = FNFHighway(self.songdata.charts[0], (((Settings.width // 3) * 2), 0))
        self.highway_2 = FNFHighway(self.songdata.charts[1], (10, 0), auto=True)
        self.engine = FNFEngine(self.songdata.charts[0])

        with pkg_resources.path(charm.data.charts.fnf, "ballistic.mp3") as p:
            song = arcade.load_sound(p)
            self.song = arcade.play_sound(song, self.volume, looping=False)
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

        # Generate "gum wrapper" background
        self.logo_width, self.small_logos_forward, self.small_logos_backward = generate_gum_wrapper(self.size)

        self.last_player1_note = None
        self.last_player2_note = None
        self.last_camera_event = CameraFocusEvent(0, 1)
        self.last_spotlight_position = 0
        self.last_spotlight_change = 0
        self.go_to_spotlight_position = 0
        self.spotlight_position = 0

        self.hp_bar_length = 250

        self.key_state = [False] * 4

    def on_key_press(self, symbol: int, modifiers: int):
        match symbol:
            case arcade.key.BACKSPACE:
                self.back.setup()
                self.song.delete()
                self.window.show_view(self.back)
                arcade.play_sound(self.window.sounds["back"])
        if symbol in self.engine.mapping:
            i = self.engine.mapping.index(symbol)
            self.key_state[i] = True
            self.highway_1.strikeline[i].alpha = 255
        self.engine.process_keystate(self.key_state)
        return super().on_key_press(symbol, modifiers)

    def on_key_release(self, symbol: int, modifiers: int):
        if symbol in self.engine.mapping:
            i = self.engine.mapping.index(symbol)
            self.key_state[i] = False
            self.highway_1.strikeline[i].alpha = 64
        self.engine.process_keystate(self.key_state)
        return super().on_key_release(symbol, modifiers)

    def on_update(self, delta_time):
        super().on_update(delta_time)

        self.engine.update(self.song.time)

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

    def get_spotlight_position(self, song_time: float):
        focus_pos = {
            2: Settings.width // 2,
            1: 0
        }
        cameraevents = [e for e in self.songdata.events if isinstance(e, CameraFocusEvent) and e.position < self.song.time + 0.25]
        if cameraevents:
            current_camera_event = cameraevents[-1]
            if self.last_camera_event != current_camera_event:
                self.last_spotlight_change = song_time
                self.last_spotlight_position = self.spotlight_position
                self.go_to_spotlight_position = focus_pos[current_camera_event.focused_player]
                self.last_camera_event = current_camera_event
        self.spotlight_position = anim.ease_circout(self.last_spotlight_position, self.go_to_spotlight_position, self.last_spotlight_change, self.last_spotlight_change + 0.125, song_time)

    def on_draw(self):
        self.clear()
        self.camera.use()

        # Charm BG
        self.small_logos_forward.draw()
        self.small_logos_backward.draw()

        self.song_time_text.draw()
        self.score_text.draw()
        self.judge_text.draw()

        hp_min = self.size[0] // 2 - self.hp_bar_length // 2
        hp_max = self.size[0] // 2 + self.hp_bar_length // 2
        hp = anim.zero_one_to_range(hp_min, hp_max, self.engine.hp)
        arcade.draw_lrtb_rectangle_filled(
            hp_min, hp_max,
            self.size[1] - 100, self.size[1] - 110,
            arcade.color.BLACK
        )
        arcade.draw_circle_filled(hp, self.size[1] - 105, 20, arcade.color.BLUE)

        self.highway_1.draw()
        self.highway_2.draw()

        arcade.draw_lrtb_rectangle_filled(
            self.spotlight_position, self.spotlight_position + Settings.width // 2, Settings.height, 0,
            arcade.color.BLACK + (127,)
        )

        super().on_draw()
