from arcade import Color, Sprite
import arcade
import PIL.Image, PIL.ImageOps

import charmtests.data.icons
from charmtests.lib.anim import ease_circout
from charmtests.lib.charm import CharmColors, generate_missing_texture_image
from charmtests.lib.digiview import DigiView
from charmtests.lib.settings import Settings
from charmtests.lib.utils import clamp, img_from_resource


class MainMenuItem(Sprite):
    def __init__(self, label: str, icon: str, goto: DigiView,
                 width: int = 200, border_color: Color = arcade.color.WHITE, border_width: int = 5,
                 *args, **kwargs):
        try:
            self.icon = img_from_resource(charmtests.data.icons, f"icon.png")
            self.icon.resize((width, width), PIL.Image.LANCZOS)
        except:
            self.icon = generate_missing_texture_image(width, width)
        self.icon = PIL.ImageOps.expand(self.icon ,border=border_width, fill=border_color)
        tex = arcade.Texture(f"_icon_{icon}", image=self.icon, hit_box_algorithm=None)
        super().__init__(texture = tex, *args, **kwargs)

        self.goto = goto

        self.label = arcade.Text(label, 0, 0, CharmColors.PURPLE, anchor_x='center', anchor_y="top", font_name="bananaslip plus plus", font_size=24)
        self.center_y = Settings.height // 2

class MainMenu:
    def __init__(self, items: list[MainMenuItem] = []) -> None:
        self.items = items

        self.sprite_list = arcade.SpriteList()
        for item in self.items:
            self.sprite_list.append(item)

        self._selected_id = 0

        self.local_time = 0
        self.move_start = 0
        self.move_speed = 0.5

    @property
    def selected_id(self) -> int:
        return self._selected_id

    @selected_id.setter
    def selected_id(self, v: int):
        self._selected_id = clamp(0, v, len(self.items) - 1)
        self.move_start = self.local_time

    @property
    def selected(self) -> MainMenuItem:
        return self.items[self.selected_id]

    @property
    def move_end(self) -> float:
        return self.move_start + self.move_speed

    def sort(self, key: str, rev: bool = False):
        selected = self.items[self.selected_id]
        self.items.sort(key=lambda item: getattr(item.song, key), reverse=rev)
        self.selected_id = self.items.index(selected)

    def update(self, local_time: float):
        self.local_time = local_time
        old_pos = {}
        for item in self.items:
            old_pos[item] = (item.center_x, item.scale, item.alpha)
        current = self.items[self.selected_id]
        current.center_x = ease_circout(old_pos[current][0], Settings.width // 2, self.move_start, self.move_end, self.local_time)
        current.scale = ease_circout(old_pos[current][1], 1, self.move_start, self.move_end, self.local_time)
        current.alpha = ease_circout(old_pos[current][2], 255, self.move_start, self.move_end, self.local_time)

        x_bumper = Settings.width // 4
        left_item = self.items[self.selected_id - 1]
        left_item.center_x = ease_circout(old_pos[left_item][0], x_bumper, self.move_start, self.move_end, self.local_time)
        left_item.scale = ease_circout(old_pos[left_item][1], 0.5, self.move_start, self.move_end, self.local_time)
        left_item.alpha = ease_circout(old_pos[left_item][2], 127, self.move_start, self.move_end, self.local_time)

        right_id = self.selected_id + 1
        if right_id >= len(self.items):
            right_id = len(self.items) - 1 - right_id
        right_item = self.items[right_id]
        right_item.center_x = ease_circout(old_pos[right_item][0], Settings.width - x_bumper, self.move_start, self.move_end, self.local_time)
        right_item.scale = ease_circout(old_pos[right_item][1], 0.5, self.move_start, self.move_end, self.local_time)
        right_item.alpha = ease_circout(old_pos[left_item][2], 127, self.move_start, self.move_end, self.local_time)

        for i in [current, left_item, right_item]:
            i.label.x = i.center_x
            i.label.y = i.bottom
            i.label.scale = i.scale

    def draw(self):
        self.sprite_list.draw()
        current = self.items[self.selected_id]
        left_item = self.items[self.selected_id - 1]
        right_id = self.selected_id + 1
        if right_id >= len(self.items):
            right_id = len(self.items) - 1 - right_id
        right_item = self.items[right_id]

        for i in [current, left_item, right_item]:
            i.label.draw()
