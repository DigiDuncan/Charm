from __future__ import annotations
from typing import cast
from pyglet.image import AbstractImage, Texture
from pyglet.text.document import AbstractDocument
from pyglet.graphics import Batch, Group

import logging
from importlib.resources import files
from functools import cache
import json
import re

import emoji_data_python

from pyglet.text.formats.structured import ImageElement
from pyglet.text.document import FormattedDocument
from pyglet.text import DocumentLabel

import charm.data.images
from charm.lib.utils import pt_to_px, pyglet_img_from_path

emoji_data_python.get_emoji_regex = cache(emoji_data_python.get_emoji_regex)
logger = logging.getLogger("charm")


class EmojiPicker:
    def __init__(self, sheet: AbstractImage, region_data: dict):
        self.sheet = sheet
        self.region_data = region_data

        self.set_name: str = self.region_data["name"]
        self.emoji_width: int = self.region_data["emoji_width"]
        self.emoji_height: int = self.region_data["emoji_height"]
        self.emojis: list[str] = self.region_data["emojis"]

        self.emoji_coords = {}

        grid_width = self.sheet.width // self.emoji_width
        for i, e in enumerate(self.emojis):
            row = i // grid_width
            col = i % grid_width
            coords = col * self.emoji_width, self.sheet.height - (row * self.emoji_height) - self.emoji_height
            self.emoji_coords[e] = coords
            if not e.endswith("\ufe0f"):
                self.emoji_coords[e + "\ufe0f"] = coords
        logger.debug(f"Loaded emoji set {self.set_name}")

    def get_emoji_coords(self, emoji: str) -> tuple[int, int]:
        emoji = emoji.removesuffix("\ufe0f").removesuffix("\ufe0e")
        return self.emoji_coords.get(emoji, (0, 0))

    @cache
    def get_emoji_texture(self, emoji: str, size: int) -> Texture:
        x, y = self.get_emoji_coords(emoji)
        img_region = self.sheet.get_region(x, y, self.emoji_width, self.emoji_height)
        img = cast(Texture, img_region.get_texture())
        px = pt_to_px(size)
        img.width = px
        img.height = px
        logger.debug(f"Got emoji {emoji}@{px}px in set {self.set_name}")
        return img

    def get_emoji_element(self, emoji: str, size: int) -> ImageElement:
        img = self.get_emoji_texture(emoji, size)
        element = ImageElement(image=img)
        return element

    def get_clean_string(self, s: str, size: int) -> tuple[str, list[tuple[int, ImageElement]]]:
        inserts = []
        emojized_string = emoji_data_python.replace_colons(s)
        while m := re.search(emoji_data_python.get_emoji_regex(), emojized_string):
            emojized_string = re.sub(emoji_data_python.get_emoji_regex(), "", emojized_string)
            inserts.append((m.start(1), self.get_emoji_element(m.group(1), size)))
        return emojized_string, inserts


def get_emoji_picker(id: str) -> EmojiPicker:
    with (files(charm.data.images) / "emoji" / f"{id}.json").open("r") as f:
        region_data = json.load(f)
    png = pyglet_img_from_path(files(charm.data.images) / "emoji" / f"{id}.png")
    return EmojiPicker(png, region_data)


emojisets: dict[str, EmojiPicker] = {}


class FormattedLabel(DocumentLabel):
    def __init__(
            self,
            text: str = '',
            font_name: str | list[str] | None = None,
            font_size: float | None = None,
            bold: bool | str = False,
            italic: bool | str = False,
            stretch: bool | str = False,
            color: tuple[int, int, int, int] = (255, 255, 255, 255),
            x: int = 0,
            y: int = 0,
            z: int = 0,
            width: int | None = None,
            height: int | None = None,
            anchor_x: str = 'left',
            anchor_y: str = 'baseline',
            align: str = 'left',
            multiline: bool = False,
            dpi: float | None = None,
            batch: Batch | None = None,
            group: Group | None = None,
            rotation: float = 0
    ):
        """:Parameters:
            `text` : str
                Text to display.
            `font_name` : str or list
                Font family name(s).  If more than one name is given, the
                first matching name is used.
            `font_size` : float
                Font size, in points.
            `bold` : bool/str
                Bold font style.
            `italic` : bool/str
                Italic font style.
            `stretch` : bool/str
                 Stretch font style.
            `color` : (int, int, int, int)
                Font colour, as RGBA components in range [0, 255].
            `x` : int
                X coordinate of the label.
            `y` : int
                Y coordinate of the label.
            `z` : int
                Z coordinate of the label.
            `width` : int
                Width of the label in pixels, or None
            `height` : int
                Height of the label in pixels, or None
            `anchor_x` : str
                Anchor point of the X coordinate: one of ``"left"``,
                ``"center"`` or ``"right"``.
            `anchor_y` : str
                Anchor point of the Y coordinate: one of ``"bottom"``,
                ``"baseline"``, ``"center"`` or ``"top"``.
            `align` : str
                Horizontal alignment of text on a line, only applies if
                a width is supplied. One of ``"left"``, ``"center"``
                or ``"right"``.
            `multiline` : bool
                If True, the label will be word-wrapped and accept newline
                characters.  You must also set the width of the label.
            `dpi` : float
                Resolution of the fonts in this layout.  Defaults to 96.
            `batch` : `~pyglet.graphics.Batch`
                Optional graphics batch to add the label to.
            `group` : `~pyglet.graphics.Group`
                Optional graphics group to use.
            `rotation`: float
                The amount to rotate the label in degrees. A positive amount
                will be a clockwise rotation, negative values will result in
                counter-clockwise rotation.

        """
        doc = FormattedDocument(text)
        super().__init__(doc, x, y, z, width, height, anchor_x, anchor_y, rotation, multiline, dpi, batch, group)
        self.stretch = stretch
        self.align = align
        self.document.set_style(0, len(self.document.text), {
            'font_name': font_name,
            'font_size': font_size,
            'bold': bold,
            'italic': italic,
            'stretch': stretch,
            'color': color,
            'align': align,
        })

    @property
    def document(self) -> AbstractDocument:
        """Document to display.

         For :py:class:`~pyglet.text.layout.IncrementalTextLayout` it is
         far more efficient to modify a document in-place than to replace
         the document instance on the layout.

         :type: `AbstractDocument`
         """
        return self._document

    @document.setter
    def document(self, document: AbstractDocument) -> None:
        document.set_style(0, len(document.text), {
            'font_name': self.font_name,
            'font_size': self.font_size,
            'bold': self.bold,
            'italic': self.italic,
            'stretch':self.stretch,
            'color': self.color,
            'align': self.align,
        })
        self._set_document(document)
        self._init_document()


class EmojiLabel(FormattedLabel):
    def __init__(self, text: str, *args, emojiset: str = "twemoji", **kwargs):
        super().__init__(text, *args, **kwargs)
        if emojiset in emojisets:
            emoji_picker = emojisets[emojiset]
        else:
            emojisets[emojiset] = get_emoji_picker(emojiset)
            emoji_picker = emojisets[emojiset]

        new_text, inserts = emoji_picker.get_clean_string(self.text, self.font_size)
        self.text = new_text

        doc: AbstractDocument = self.document
        for pos, i in inserts:
            doc.insert_text(pos, '\0', None)
            i._position = pos # noqa: SLF001
            doc._elements.append(i) # noqa: SLF001
            logger.debug(f"Inserted element {i} at {pos}")
        doc._elements.sort(key=lambda d: d.position)  # noqa: SLF001

        self.document = doc


def update_emoji_doc(doc: AbstractDocument, text: str, font_size: int, emojiset: str = 'twemoji') -> None:
    if emojiset in emojisets:
        emoji_picker: EmojiPicker = emojisets[emojiset]
    else:
        emojisets[emojiset] = get_emoji_picker(emojiset)
        emoji_picker: EmojiPicker = emojisets[emojiset]

    cleaned_text, inserts = emoji_picker.get_clean_string(text, font_size)
    doc.text = cleaned_text
    for pos, i in inserts:
        doc.insert_text(pos, '\0', None)
        i._position = pos # noqa: SLF001
        doc._elements.append(i) # noqa: SLF001
        logger.debug(f"Inserted element {i} at {pos}")
    doc._elements.sort(key=lambda d: d.position)  # noqa: SLF001
    return doc

