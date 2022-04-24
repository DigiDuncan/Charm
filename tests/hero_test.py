from importlib import resources as pkg_resources
from charm.lib.gamemodes.ch import HeroSong
import charm.data.tests

soulless = None

def test_parse_soulless():
    global soulless
    with pkg_resources.path(charm.data.tests, "soulless5") as p:
        soulless = HeroSong.parse(p)
    assert soulless is not None