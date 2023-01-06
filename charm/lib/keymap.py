import arcade.key
from arcade.key import ENTER, NUM_ENTER, ESCAPE, BACKSPACE, \
    D, F, J, K, KEY_1, KEY_2, KEY_3, KEY_4, KEY_5, UP, DOWN

from charm.lib.utils import findone

Keys = list[int]
Key = int

def get_arcade_key_name(i: int) -> str:
    findone([k for k, v in arcade.key.__dict__.values() if v == i])


class KeyMap:
    def __init__(self):
        # This is going to have to be a long list of like, every key we look for.
        # There *might* be a better way to do this, but not with typing.
        self.key_names = ["start", "fourkey_1", "fourkey_2", "fourkey_3", "fourkey_4",
            "hero_1", "hero_2", "hero_3", "hero_4", "hero_5", "hero_strum_up", "hero_strum_down"]

        # Generic
        self.start: Keys = [ENTER, NUM_ENTER]
        self.back: Keys = [ESCAPE, BACKSPACE]

        # 4K
        self.fourkey_1: Key = D
        self.fourkey_2: Key = F
        self.fourkey_3: Key = J
        self.fourkey_4: Key = K

        # Hero
        self.hero_1: Key = KEY_1
        self.hero_2: Key = KEY_2
        self.hero_3: Key = KEY_3
        self.hero_4: Key = KEY_4
        self.hero_5: Key = KEY_5
        self.hero_strum_up: Key = UP
        self.hero_strum_down: Key = DOWN

    @property
    def fourkey_mapping(self) -> Keys:
        return [self.fourkey_1, self.fourkey_2, self.fourkey_3, self.fourkey_4]

    def get_keys(self, name: str) -> Keys:
        if name not in self.key_names:
            return ValueError(f"{name!r} is not a valid key name!")
        return getattr(self, name)

    def bind_key(self, name: str, key: Key):
        if name not in self.key_names:
            return ValueError(f"{name!r} is not a valid key name!")
        self.get_keys(name).append(key)

    def get_name(self, key: Key) -> str:
        return findone([n for n, i in [(k, getattr(self, k)) for k in self.key_names] if i == key])

    def to_JSON(self) -> dict[str, Keys]:
        return {k: getattr(self, k) for k in self.key_names}

    @classmethod
    def from_JSON(cls, jsondata: dict[str, Keys]) -> 'KeyMap':
        keymap = KeyMap()
        for k, v in jsondata.items():
            setattr(keymap, k, v)
        return keymap


keymap = KeyMap()
