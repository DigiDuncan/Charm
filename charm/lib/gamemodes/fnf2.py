from pathlib import Path
from charm.lib.errors import NoChartsError
from charm.lib.paths import modsfolder, songspath
from charm.lib.generic.song import Note, Chart, Song


class NoteType:
    NORMAL = "normal"
    BOMB = "bomb"
    DEATH = "death"
    HEAL = "heal"
    CAUTION = "caution"


class FNFNote(Note):
    @property
    def icon(self):
        if self.is_sustain and self.type == NoteType.NORMAL:
            return f"sustain-{self.lane}"
        elif self.is_sustain:
            return f"{self.type}-sustain"
        else:
            return f"{self.type}-{self.lane}"


class FNFChart(Chart):
    def __init__(self, difficulty: str, player: int):
        super().__init__("fnf", difficulty, f"player{player}", 4)
        self.name = ""
        self.player1 = "bf"
        self.player2 = "dad"
        self.spectator = "gf"
        self.stage = "stage"
        self.notespeed = 1


class FNFMod:
    def __init__(self, folder_name: str) -> None:
        self.folder_name = folder_name
        self.path = modsfolder / self.folder_name
        self.name: str = None
        self.songs = list[FNFSong]


class FNFSong(Song):
    def __init__(self, song_code: str, mod: FNFMod = None) -> None:
        super().__init__(song_code)
        self.mod: FNFMod = mod

    @classmethod
    def parse(cls, folder: str, mod: FNFMod = None):
        song = FNFSong(folder)
        song.path = songspath / "fnf" / folder
        if mod:
            song.mod = mod
            song.path = mod.path / folder

        charts = song.path.glob(f"{folder}*.json")
        parsed_charts = [cls.parse_chart(chart, song) for chart in charts]
        for charts in parsed_charts:
            for chart in charts:
                song.charts.append(chart)

        if not song.charts:
            raise NoChartsError(folder)

        # Global attributes that are stored per-chart, for some reason.
        chart: FNFChart = song.charts[0]
        song.bpm = chart.bpm
        song.metadata["title"] = chart.name

    @classmethod
    def parse_chart(cls, file_path: Path, song: 'FNFSong') -> list[FNFChart]:
        return [FNFChart("", 0)]
