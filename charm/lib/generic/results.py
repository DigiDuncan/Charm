from collections import defaultdict
from dataclasses import dataclass

import arcade

from charm.lib.anim import lerp
from charm.lib.generic.engine import Judgement, Chart
from charm.lib.generic.song import Seconds

@dataclass
class Results:
    chart: Chart
    hit_window: Seconds
    judgements: list[Judgement]
    all_judgements: list[tuple[Seconds, Seconds, Judgement]]
    score: int
    hits: int
    misses: int
    accuracy: float
    grade: str
    fc_type: str
    streak: int
    max_streak: int

class Heatmap(arcade.Sprite):
    def __init__(self, judgements: list[Judgement], all_judgements: list[tuple[Seconds, Seconds, Judgement]], height: int = 75):
        self.judgements = judgements
        self.all_judgements = all_judgements

        hit_window = self.judgements[-2].ms + 1
        width = hit_window * 2 + 1
        center = hit_window + 1

        self._tex = arcade.Texture.create_empty("_heatmap", (width, height))
        super().__init__(texture = self._tex)
        self._sprite_list = arcade.SpriteList()
        self._sprite_list.append(self)

        with self._sprite_list.atlas.render_into(self._tex) as fbo:
            fbo.clear()
            arcade.draw_line(center, 0, center, height, arcade.color.BLACK, 3)
            arcade.draw_line(0, height / 2, width, height / 2, arcade.color.BLACK)

            hits = defaultdict(lambda: 0)
            for _, t, j in self.all_judgements:
                if j.key == "miss":
                    continue
                ms = round(t * 1000)
                hits[ms] += 1

            max_hits = max(hits.values())
            avg_ms = sum([k * v for k, v in hits.items()]) / sum(hits.values())

            for ms, count in hits.items():
                perc = abs(ms / hit_window)
                m = (height * 0.75)
                h = ((count / max_hits) * m) / 2
                color = (lerp(0, 255, perc), lerp(255, 0, perc), 0, 255)
                arcade.draw_line(center + ms, (height / 2) + h, center + ms, (height / 2) - h, color)

            avg_ms_pos = center + avg_ms
            e = (height * 0.05)
            tip = (avg_ms_pos, height * 0.85)
            left = (avg_ms_pos - e, height * 0.95)
            right = (avg_ms_pos + e, height * 0.95)
            arcade.draw_polygon_filled((left, right, tip), arcade.color.WHITE)
            arcade.draw_polygon_outline((left, right, tip), arcade.color.BLACK)
