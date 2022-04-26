from importlib import resources as pkg_resources
from charm.lib.gamemodes.ch import HeroSong
import charm.data.tests

soulless: HeroSong = None

def test_parse_soulless():
    global soulless
    with pkg_resources.path(charm.data.tests, "soulless5") as p:
        soulless = HeroSong.parse(p)
    assert soulless is not None

def test_soulless_chords():
    expert_chart = soulless.get_chart("Expert")
    assert len(expert_chart.chords) == 10699  # Known value