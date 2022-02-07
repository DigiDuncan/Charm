import arcade
import pyglet
import importlib.resources as pkg_resources

from charmtests.lib.charm import CharmColors, generate_gum_wrapper, move_gum_wrapper
from charmtests.lib.digiview import DigiView
import charmtests.data.charts.fnf
from charmtests.lib.gamemodes.fnf import FNFSong, altcolormap, wordmap, colormap

class TestView(DigiView):
    def __init__(self, *args, **kwargs):
        super().__init__(fade_in=1, bg_color=CharmColors.FADED_GREEN, *args, **kwargs)
        self.volume = 1

    def setup(self):
        super().setup()

        c = pkg_resources.read_text(charmtests.data.charts.fnf, "ballistic.json")
        self.songdata = FNFSong.parse(c)

        with pkg_resources.path(charmtests.data.charts.fnf, "ballistic.mp3") as p:
            song = arcade.load_sound(p)
            self.song = arcade.play_sound(song, self.volume, looping = False)
        self.window.theme_song.volume = 0

        self.player1_text = arcade.Text("????", (self.size[0] // 4) * 3, self.size[1] // 2, font_size = 72,
                                        anchor_x="center", anchor_y="center")
        self.player2_text = arcade.Text("????", (self.size[0] // 4), self.size[1] // 2, font_size = 72,
                                        anchor_x="center", anchor_y="center")
        self.song_time_text = arcade.Text("????", (self.size[0] // 2), 10, font_size = 18,
                                        anchor_x="center", color=arcade.color.BLACK)

        # Generate "gum wrapper" background
        self.logo_width, self.small_logos_forward, self.small_logos_backward = generate_gum_wrapper(self.size)

        self.last_player1_note = None
        self.last_player2_note = None

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

        self.song_time_text._label.text = str(round(self.song.time, 3))

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

    def on_draw(self):
        self.clear()
        self.camera.use()

        # Charm BG
        self.small_logos_forward.draw()
        self.small_logos_backward.draw()

        self.player1_text.draw()
        self.player2_text.draw()
        self.song_time_text.draw()
        
        super().on_draw()
