from charm.lib.generic.engine import Engine
from charm.lib.generic.highway import Highway
from charm.lib.generic.song import Chart, Note, Seconds, Event


class Modchart:
    def __init__(self, engine: Engine, chart: Chart, highway: Highway):
        self.engine = engine
        self.chart = chart
        self.highway = highway

        self.song_time = 0
        self.local_variables = {}

    @property
    def chart_time(self) -> Seconds:
        return self.song_time + self.engine.offset

    def update(self, song_time: Seconds):
        self.song_time = song_time
        self.on_tick()

    def on_beat(self, beat: int):
        raise NotImplementedError

    def on_tick(self, tick: int):
        pass

    def on_key_press(self, key: int):
        raise NotImplementedError

    def on_key_release(self, key: int):
        raise NotImplementedError

    def on_note_hit(self, note: Note, player = 0):
        raise NotImplementedError

    def on_note_missed(self, note: Note, player = 0):
        raise NotImplementedError

    def on_chart_event(self, event: Event):
        raise NotImplementedError
