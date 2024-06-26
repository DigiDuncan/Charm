from __future__ import annotations

from pathlib import Path

from charm.lib.gamemodes.four_key import FourKeyChart, FourKeyEngine, FourKeyNote, FourKeySong
from charm.lib.gamemodes.osu import OsuHitCircle, OsuHold, RawOsuChart
from charm.lib.generic.song import Metadata


class ManiaSong(FourKeySong):
    def __init__(self, path: Path):
        """A four-key song from osu!mania."""
        super().__init__(path)

    @classmethod
    def parse(cls, path: Path) -> ManiaSong:
        song = ManiaSong(path)

        chart_files = path.glob("*.osu")

        added_bpm_events = False

        for p in chart_files:
            raw_chart = RawOsuChart.parse(p)  # SO MUCH is hidden by this function
            chart = FourKeyChart(song, raw_chart.metadata.difficulty, None)
            if not added_bpm_events:
                song.events.extend(raw_chart.timing_points)
                added_bpm_events = True
            for hit_object in raw_chart.hit_objects:
                if isinstance(hit_object, OsuHitCircle):
                    chart.notes.append(FourKeyNote(chart, hit_object.time, hit_object.get_lane(4)))
                elif isinstance(hit_object, OsuHold):
                    chart.notes.append(FourKeyNote(chart, hit_object.time, hit_object.get_lane(4), length = hit_object.length))
            song.charts.append(chart)
        # TODO: Handle no charts
        return song

    @classmethod
    def get_metadata(cls, folder: Path) -> Metadata:
        chart_files = folder.glob("*.osu")
        raw_chart = RawOsuChart.parse(next(chart_files))
        m = raw_chart.metadata
        return Metadata(
            path=folder,
            title=m.title,
            artist=m.artist,
            album=m.source,
            charter=m.charter,
            gamemode="4k"
        )


class ManiaEngine(FourKeyEngine):
    def score_sustains(self) -> None:
        pass
