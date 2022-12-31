import statistics
import typing

import arcade
import pyglet
from pypresence import Presence

from charm.objects.debug_log import DebugLog

rpc_client_id = "1056710104348639305"

if typing.TYPE_CHECKING:
    from charm.lib.digiview import DigiView

class DigiWindow(arcade.Window):
    def __init__(self, size: tuple[int, int], title: str, fps_cap: int, initial_view: "DigiView"):
        super().__init__(size[0], size[1], title, update_rate=1/fps_cap, enable_polling=True)

        self.fps_cap = fps_cap
        self.initial_view = initial_view

        self.delta_time = 0.0
        self.time = 0.0
        self.fps_checks = 0
        self.debug = False
        self.show_fps = True
        self.show_log = False
        self.sounds: dict[str, arcade.Sound] = {}
        self.theme_song: pyglet.media.Player = None

        # Discord RP
        self.rpc = Presence(rpc_client_id)
        self.last_rp_time = 0
        self.current_rp_state = ":jiggycat:"
        self._rp_stale = True
        self.rpc.connect()

        self.fps_averages = []

        arcade.draw_text(" ", 0, 0)  # force font init (fixes lag on first text draw)

        self.debug_camera = arcade.Camera(size[0], size[1])
        self.fps_label = pyglet.text.Label("???.? FPS",
                          font_name='bananaslip plus plus',
                          font_size=12,
                          x=0, y=self.height,
                          anchor_x='left', anchor_y='top',
                          color=(0, 0, 0) + (0xFF,))
        self.fps_shadow_label = pyglet.text.Label("???.? FPS",
                          font_name='bananaslip plus plus',
                          font_size=12,
                          x=1, y=self.height - 1,
                          anchor_x='left', anchor_y='top',
                          color=(0xAA, 0xAA, 0xAA) + (0xFF,))
        self.more_info_label = pyglet.text.Label("DEBUG",
                          font_name='bananaslip plus plus',
                          font_size=12,
                          x=0, y=self.height - self.fps_label.content_height - 5, multiline=True, width=self.width,
                          anchor_x='left', anchor_y='top',
                          color=(0, 0, 0) + (0xFF,))
        self.alpha_label = pyglet.text.Label("ALPHA",
                          font_name='bananaslip plus plus',
                          font_size=16,
                          x=self.width - 5, y=5,
                          anchor_x='right', anchor_y='bottom',
                          color=(0, 0, 0) + (32,))

        self.debug_log = DebugLog()
        self.log = self.debug_log.layout
        self.log.position = (5, 5)

        cheats = []
        self.cheats = {c: False for c in cheats}

    def setup(self):
        self.initial_view.setup()
        self.show_view(self.initial_view)
        self.update_rp()

    def update(self, delta_time: float):
        self.delta_time = delta_time
        self.time += delta_time
        self.update_rp()

    def update_rp(self, new_state: str = None):
        if new_state:
            self.current_rp_state = new_state
            self._rp_stale = True
        if self.last_rp_time + 15 > self.time and self._rp_stale:
            self.rpc.update(state=self.current_rp_state,
            large_image="charm-icon-square", large_text="Charm Logo")
            self.last_rp_time = self.time
            self._rp_stale = False

    def debug_draw(self):
        self.fps_checks += 1
        _cam = self.current_camera
        self.debug_camera.use()
        if self.fps_checks % (self.fps_cap / 8) == 0:
            average = statistics.mean(self.fps_averages)
            self.fps_label.color = arcade.color.BLACK + (0xFF,) if average >= 120 else arcade.color.RED + (0xFF,)
            self.fps_label.text = self.fps_shadow_label.text = f"{average:.1f} FPS"
            self.fps_averages.clear()
        else:
            self.fps_averages.append(1 / self.delta_time)
        with self.ctx.pyglet_rendering():
            if self.show_fps or self.debug:
                self.fps_shadow_label.draw()
                self.fps_label.draw()
            if self.debug:
                self.more_info_label.draw()
                if self.show_log:
                    self.log.draw()
            self.alpha_label.draw()
        if _cam is not None:
            _cam.use()
