import arcade
import pyglet
import importlib.resources as pkg_resources

from charmtests.lib.charm import CharmColors, generate_gum_wrapper, move_gum_wrapper
from charmtests.lib.digiview import DigiView
import charmtests.data.charts.fnf
from charmtests.lib.gamemodes.fnf import FNFSong, wordmap, colormap

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
        self.local_time_text = arcade.Text("????", (self.size[0] // 2), 0, font_size = 36,
                                        anchor_x="center", color=arcade.color.BLACK)
        self.song_time_text = arcade.Text("????", (self.size[0] // 2), 50, font_size = 18,
                                        anchor_x="center", color=arcade.color.BLACK)

        # Generate "gum wrapper" background
        self.logo_width, self.small_logos_forward, self.small_logos_backward = generate_gum_wrapper(self.size)

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

        self.local_time_text._label.text = str(round(self.local_time, 3))
        self.song_time_text._label.text = str(round(self.song.time, 3))

        player1notes = [n for n in self.songdata.charts[0].notes if n.position <= self.local_time]
        if player1notes:
            player1note = player1notes[-1].lane
            self.player1_text._label.text = wordmap[player1note]
            self.player1_text.color = colormap[player1note]
        player2notes = [n for n in self.songdata.charts[1].notes if n.position <= self.local_time]
        if player2notes:
            player2note = player2notes[-1].lane
            self.player2_text._label.text = wordmap[player2note]
            self.player2_text.color = colormap[player2note]

    def on_draw(self):
        self.clear()
        self.camera.use()

        # Charm BG
        self.small_logos_forward.draw()
        self.small_logos_backward.draw()

        self.player1_text.draw()
        self.player2_text.draw()
        self.local_time_text.draw()
        self.song_time_text.draw()
        
        super().on_draw()
