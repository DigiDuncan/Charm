from collections import defaultdict
import importlib.resources as pkg_resources
import logging
from typing import Optional

import arcade
from charm.lib.anim import lerp

from charm.lib.charm import CharmColors, generate_gum_wrapper, move_gum_wrapper
from charm.lib.digiview import DigiView
from charm.lib.generic.engine import Judge, NoteJudgement
from charm.lib.generic.results import Results

import charm.data.audio
import charm.data.images.skins
from charm.lib.keymap import get_keymap
from charm.lib.utils import splitby

logger = logging.getLogger("charm")

class ResultsView(DigiView):
    def __init__(self, results: Results, *args, **kwargs):
        super().__init__(fade_in=1, bg_color=CharmColors.FADED_GREEN, *args, **kwargs)
        self.song = None
        self.volume = 1
        self.results = results

    def setup(self):
        super().setup()

        with pkg_resources.path(charm.data.audio, "music-results.mp3") as p:
            self._song = arcade.Sound(p)

        with pkg_resources.path(charm.data.images.skins.base, f"grade-{self.results.grade}.png") as p:
            self.grade_sprite = arcade.Sprite(p)
        self.grade_sprite.bottom = 25
        self.grade_sprite.left = 25

        self.score_text = arcade.Text(f"{self.results.score}",
            self.window.width - 5, self.window.height,
            arcade.color.BLACK, 72, self.window.width,
            "right", "bananaslip plus",
            anchor_x = "right", anchor_y = "top", multiline = True)
        self.data_text = arcade.Text(f"{self.results.fc_type}\nAccuracy: {self.results.accuracy * 100:.2f}%\nMax Streak: {self.results.max_streak}",
            self.window.width - 5, self.score_text.bottom,
            arcade.color.BLACK, 24, self.window.width,
            "right", "bananaslip plus",
            anchor_x = "right", anchor_y = "top", multiline = True)
        self.judgements_text = arcade.Text("", self.grade_sprite.right + 10, self.grade_sprite.bottom, arcade.color.BLACK, 24,
        self.window.width, anchor_x = "left", anchor_y = "bottom", font_name = "bananaslip plus", multiline = True)

        nj_by_key = splitby(self.results.note_judgements, key=lambda nj: nj.judgement.key)
        for j in self.results.judge.judgements:
            self.judgements_text.value += f"{j.name}: {len(nj_by_key[j.key])}\n"

        self.heatmap = Heatmap(self.results.judge.hit_window_ms, self.results.note_judgements)
        self.heatmap.scale = 2
        self.heatmap.bottom = 10
        self.heatmap.right = self.window.width - 10

        # Generate "gum wrapper" background
        self.logo_width, self.small_logos_forward, self.small_logos_backward = generate_gum_wrapper(self.size)
        self.success = True

    def on_show_view(self):
        self.window.theme_song.volume = 0
        self.song = arcade.play_sound(self._song, self.volume, looping=False)

    def on_key_press(self, symbol: int, modifiers: int):
        keymap = get_keymap()
        match symbol:
            case keymap.back | keymap.start:
                self.song.volume = 0
                self.back.setup()
                self.window.show_view(self.back)
                arcade.play_sound(self.window.sounds["back"])

        return super().on_key_press(symbol, modifiers)

    def on_update(self, delta_time):
        super().on_update(delta_time)

        move_gum_wrapper(self.logo_width, self.small_logos_forward, self.small_logos_backward, delta_time)

    def on_draw(self):
        self.clear()
        self.camera.use()

        # Charm BG
        self.small_logos_forward.draw()
        self.small_logos_backward.draw()

        self.grade_sprite.draw()
        self.score_text.draw()
        self.data_text.draw()
        self.judgements_text.draw()
        self.heatmap.draw()

        super().on_draw()


class Heatmap(arcade.Sprite):
    def __init__(self, hit_window_ms: int, note_judgements: list[NoteJudgement], height_px: int = 75, width_px: Optional[int] = None):
        if width_px is None:
            width_px = (hit_window_ms * 2) + 1  # left + mid (1) + right
        mid_x = (width_px - 1) / 2

        self._tex = arcade.Texture.create_empty("_heatmap", (width_px, height_px))
        super().__init__(texture = self._tex)
        self._sprite_list = arcade.SpriteList()
        self._sprite_list.append(self)

        hits = [nj for nj in note_judgements if nj.judgement.key != "miss"]
        total_ms = sum(nj.note.hit_distance_ms for nj in hits)

        hit_counts = defaultdict(lambda: 0)
        for nj in hits:
            hit_counts[nj.note.hit_distance_ms] += 1

        max_hit_count = max(hit_counts.values())
        avg_ms = total_ms / len(hits)

        with self._sprite_list.atlas.render_into(self._tex) as fbo:
            fbo.clear()
            arcade.draw_line(width_px / 2, 0, width_px / 2, height_px, arcade.color.BLACK, 3)
            arcade.draw_line(0, height_px / 2, width_px, height_px / 2, arcade.color.BLACK)

            mid_y = height_px / 2
            hit_max_px = (height_px / 2) * 0.75
            dist_max_px = (width_px / 2)
            for hit_distance_ms, count in hit_counts.items():
                dist_scale = hit_distance_ms / hit_window_ms
                hit_scale = count / max_hit_count
                x = mid_x + (dist_scale * dist_max_px)
                y1 = mid_y + (hit_scale * hit_max_px)
                y2 = mid_y - (hit_scale * hit_max_px)
                r = round(lerp(0, 255, abs(dist_scale)))
                g = round(lerp(255, 0, abs(dist_scale)))
                b = 0
                arcade.draw_line(x, y1, x, y2, (r, g, b, 255))

            avg_scale = avg_ms / hit_window_ms
            x = mid_x + (avg_scale * dist_max_px)
            y = height_px * 0.85
            w = height_px * 0.1
            h = height_px * 0.1
            draw_arrow(x, y, w, h)

def draw_arrow(x: float, y: float, w: float, h: float):
    left = (x - ((w-1)/2), y + (h-1))
    right = (x + ((w-1)/2), y + (h-1))
    tip = (x, y)
    arcade.draw_polygon_filled((left, right, tip), arcade.color.WHITE)
    arcade.draw_polygon_outline((left, right, tip), arcade.color.BLACK)
