import logging
from os import PathLike
from pathlib import Path
import importlib.resources as pkg_resources
import re
import xml.etree.ElementTree as ET

from arcade import Sprite
import arcade

import charm.data.images.spritesheets

logger = logging.getLogger("charm")

subtexture_name = re.compile(r"(.+?)(\d+)$")


def strint(i: int | str | None) -> int:
    """Convert a str to an int, or return an existing int or None."""
    if isinstance(i, int) or i is None:
        return i
    elif isinstance(i, str):
        return int(i)
    else:
        raise ValueError(f"{i} is not a int or str.")


class Subtexture:
    def __init__(self, name: str, x: int | str, y: int | str, width: int | str, height: int | str,
                 frame_x: int | str = None, frame_y: int | str = None, frame_width: int | str = None, frame_height: int | str = None):
        self._name = name
        name_re = subtexture_name.match(self._name)
        if name_re is None:
            raise ValueError(f"{name} is not a valid Subtexture name.")
        self.name = name_re.group(1)
        self.index = name_re.group(2)

        self.x = strint(x)
        self.y = strint(y)
        self.width = strint(width)
        self.height = strint(height)
        self.frame_x = strint(frame_x)
        self.frame_y = strint(frame_y)
        self.frame_width = strint(frame_width)
        self.frame_height = strint(frame_height)

    def __str__(self):
        return f"<Subtexture {self._name}>"

    def __repr__(self) -> str:
        return str(self)


class AdobeTextureAtlas:
    def __init__(self, image_path: str, subtextures: list[Subtexture]):
        self.image_path = image_path
        self.subtextures = subtextures

    @property
    def width(self):
        return max([st.width for st in self.subtextures])

    @property
    def height(self):
        return max([st.height for st in self.subtextures])

    @classmethod
    def parse(cls, s: str) -> "AdobeTextureAtlas":
        tree = ET.ElementTree(ET.fromstring(s))
        root = tree.getroot()
        image_path = root.attrib["imagePath"]

        subtextures: list[Subtexture] = []
        for subtexture in root.iter("SubTexture"):
            st = subtexture.attrib
            name = st["name"]
            x = st["x"]
            y = st["y"]
            width = st["width"]
            height = st["height"]
            frame_x = st.get("frameX", None)
            frame_y = st.get("frameY", None)
            frame_width = st.get("frameWidth", None)
            frame_height = st.get("frameHeight", None)
            subtextures.append(Subtexture(
                name, x, y, width, height, frame_x, frame_y, frame_width, frame_height
            ))

        return cls(image_path, subtextures)


class AdobeSprite(Sprite):
    def __init__(self, folder_path: PathLike, name: str):
        self.folder = Path(folder_path)
        self._xml_path = self.folder / f"{name}.xml"
        self._image_path = self.folder / f"{name}.png"
        with open(self._xml_path, "r", encoding="utf-8") as f:
            self._xml = f.read()
        self._ata = AdobeTextureAtlas.parse(self._xml)
        self.texture_map: dict[Subtexture, int] = {}
        textures = []
        for n, st in enumerate(self._ata.subtextures):
            tx = arcade.load_texture(self._image_path, st.x, st.y, st.width, st.height)
            textures.append(tx)
            self.texture_map[st] = n

        super().__init__(image_width=self._ata.width, image_height=self._ata.height)
        for tx in textures:
            self.append_texture(tx)
        self.set_texture(0)
        self.animations = set([st.name for st in self.texture_map])

        self._current_animation = []
        self._current_animation_index = 0
        self.fps = 24
        self._animation_time = 0

    def set_animation(self, name: str):
        self._current_animation = []
        for st, n in self.texture_map.items():
            if st.name == name:
                self._current_animation.append(n)
        self._current_animation_index = 0
        self._animation_time = 0

    def update_animation(self, delta_time):
        self._animation_time += delta_time
        if self._current_animation:
            if self._animation_time >= 1 / self.fps:
                self._current_animation_index += 1
                self._current_animation_index %= len(self._current_animation)
                self.set_texture(self._current_animation[self._current_animation_index])
                self._animation_time = 0
        return super().update_animation(delta_time)


def sprite_from_adobe(s: str) -> AdobeSprite:
    with pkg_resources.path(charm.data.images.spritesheets, f"{s}.xml") as p:
        parent = p.parent
        return AdobeSprite(parent, s)
