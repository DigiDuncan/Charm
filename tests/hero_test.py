from importlib import resources as pkg_resources
from charm.lib.gamemodes.hero import HeroSong
import charm.data.tests

soulless: HeroSong = None

def test_parse_soulless():
    global soulless
    with pkg_resources.path(charm.data.tests, "soulless5") as p:
        soulless = HeroSong.parse(p)
    assert soulless is not None

def test_soulless_chord_count():
    expert_chart = soulless.get_chart("Expert")
    assert len(expert_chart.chords) == 10699  # Known value

def test_soulless_metadata():
    assert soulless.metadata.title == "Soulless 5"  # Known values
    assert soulless.metadata.artist == "ExileLord"
    assert soulless.metadata.album == "Get Smoked"
    assert soulless.metadata.year == 2018