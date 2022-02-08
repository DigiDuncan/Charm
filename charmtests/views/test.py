import arcade
import importlib.resources as pkg_resources
from charmtests.lib import anim

from charmtests.lib.charm import CharmColors, generate_gum_wrapper, move_gum_wrapper
from charmtests.lib.digiview import DigiView
import charmtests.data.charts.fnf
from charmtests.lib.gamemodes.fnf import CameraFocusEvent, FNFHighway, FNFSong, altcolormap, wordmap, colormap
from charmtests.lib.settings import Settings

class TestView(DigiView):
    def __init__(self, *args, **kwargs):
        super().__init__(fade_in=1, bg_color=CharmColors.FADED_GREEN, *args, **kwargs)
        self.volume = 1

    def setup(self):
        super().setup()

        c = pkg_resources.read_text(charmtests.data.charts.fnf, "ballistic.json")
        self.songdata = FNFSong.parse(c)
        self.highway_1 = FNFHighway(self.songdata.charts[0], (((Settings.width // 3) * 2), 0))
        self.highway_2 = FNFHighway(self.songdata.charts[1], (10, 0), auto = True)

        with pkg_resources.path(charmtests.data.charts.fnf, "ballistic.mp3") as p:
            song = arcade.load_sound(p)
            self.song = arcade.play_sound(song, self.volume, looping = False)
        self.window.theme_song.volume = 0

        self.player1_text = arcade.Text("????", (self.size[0] // 4) * 3, self.size[1] // 2, font_size = 72,
                                        anchor_x="center", anchor_y="center")
        self.player2_text = arcade.Text("????", (self.size[0] // 4), self.size[1] // 2, font_size = 72,
                                        anchor_x="center", anchor_y="center")
        self.song_time_text = arcade.Text("??:??", (self.size[0] // 2), 10, font_size = 24,
                                          anchor_x="center", color=arcade.color.BLACK,
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

    def on_key_press(self, symbol: int, modifiers: int):
        match symbol:
            case arcade.key.BACKSPACE:
                self.back.setup()
                self.song.delete()
                self.window.show_view(self.back)
                arcade.play_sound(self.window.sounds["back"])

        return super().on_key_press(symbol, modifiers)

    def on_update(self, delta_time):
        super().on_update(delta_time)

        move_gum_wrapper(self.logo_width, self.small_logos_forward, self.small_logos_backward, delta_time)

        time = f"{int(self.song.time // 60)}:{int(self.song.time % 60):02}"
        if self.song_time_text._label.text != time:
            self.song_time_text._label.text = time

        # self.text_update()
        self.get_spotlight_position(self.song.time)

        self.highway_1.update(self.song.time)
        self.highway_2.update(self.song.time)

    def text_update(self):
        player1notes = [n for n in self.songdata.charts[0].notes if n.position <= self.song.time]
        if player1notes:
            current_player1_note = player1notes[-1]
            if self.last_player1_note != current_player1_note:
                self.player1_text._label.text = wordmap[current_player1_note.lane]
                color = colormap[current_player1_note.lane]
                if self.last_player1_note is not None and self.last_player1_note.lane == current_player1_note.lane:
                    color = altcolormap[current_player1_note.lane] if len(player1notes) % 2 else colormap[current_player1_note.lane]
                else:
                    color = colormap[current_player1_note.lane]
                self.player1_text.color = color
            self.last_player1_note = current_player1_note

        player2notes = [n for n in self.songdata.charts[1].notes if n.position <= self.song.time]
        if player2notes:
            current_player2_note = player2notes[-1]
            if self.last_player2_note != current_player2_note:
                self.player2_text._label.text = wordmap[current_player2_note.lane]
                if self.last_player2_note is not None and self.last_player2_note.lane == current_player2_note.lane:
                    color = altcolormap[current_player2_note.lane] if len(player2notes) % 2 else colormap[current_player2_note.lane]
                else:
                    color = colormap[current_player2_note.lane]
                self.player2_text.color = color
            self.last_player2_note = current_player2_note

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
        self.spotlight_position = anim.ease_circout(self.last_spotlight_position, self.go_to_spotlight_position, self.last_spotlight_change, self.last_spotlight_change + 0.25, song_time)
                

    def on_draw(self):
        self.clear()
        self.camera.use()

        # Charm BG
        self.small_logos_forward.draw()
        self.small_logos_backward.draw()

        # self.player1_text.draw()
        # self.player2_text.draw()
        self.song_time_text.draw()

        self.highway_1.draw()
        self.highway_2.draw()

        arcade.draw_lrtb_rectangle_filled(
            self.spotlight_position, self.spotlight_position + Settings.width // 2, Settings.height, 0,
            arcade.color.BLACK + (127,)
        )
        
        super().on_draw()
