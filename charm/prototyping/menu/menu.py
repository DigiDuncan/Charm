from functools import lru_cache
from itertools import cycle
from typing import List

import nygame
import pygame
from nygame import DigiText as T
from pygame.constants import K_DOWN, K_RETURN, K_UP
from pygame.surface import Surface


def stacksurfs(surf1: Surface, surf2: Surface, gap = 0) -> Surface:
    if surf2 is None:
        return surf1
    if surf1 is None:
        return surf2

    width = max(surf1.get_width(), surf2.get_width())
    height = surf1.get_height() + surf2.get_height() + gap
    yoffset = surf1.get_height() + gap

    newsurf = pygame.Surface((width, height))
    newsurf.blit(surf1, (0, 0))
    newsurf.blit(surf2, (0, yoffset))

    return newsurf


class MenuItem:
    def __init__(self, key: str, title: str, artist: str):
        self.key = key
        self.title = title
        self.artist = artist

        self.selected = False

    @property
    def color(self):
        return "red" if self.selected else "green"

    def render(self):
        titlesurf = T(self.title, font = "Lato Semibold", size = 32, color = self.color, underline = True).render()
        artistsurf = T(self.artist, font = "Lato Medium", size = 24, color = self.color).render()
        return stacksurfs(titlesurf, artistsurf)


class Menu:
    def __init__(self, items: List[MenuItem] = []):
        self.items = items
        self.selected = 0

    @property
    def selected_item(self):
        return self.items[self.selected]

    def sort(self, key, reverse = False):
        self.items = self.sorted(key = key, reverse = reverse)

    @lru_cache
    def sorted(self, key, reverse = False):
        return sorted(self.items, key = lambda x: getattr(x, key), reverse = reverse)

    def update(self):
        for n, i in enumerate(self.items):
            if n == self.selected:
                i.selected = True
            else:
                i.selected = False

    def render(self):
        surf: Surface = None
        for i in self.items:
            isurf = i.render()
            surf = stacksurfs(surf, isurf, 5)
        return surf


class Game(nygame.Game):
    def __init__(self):
        super().__init__(fps = 120, showfps = True)
        self.data = [
            {"key": "nevergonnagiveyouup", "title": "Never Gonna Give You Up", "artist": "Rick Astley"},
            {"key": "aceofspades", "title": "Ace of Spades", "artist": "Motorhead"},
            {"key": "fistbump", "title": "Sonic Forces (Fist Bump)", "artist": "Crush 40"},
            {"key": "lesstalkmorerokk", "title": "Less Talk More Rokk", "artist": "Freezepop"}
        ]
        self.items = [MenuItem(i["key"], i["title"], i["artist"]) for i in self.data]
        self.menu = Menu(self.items)
        self.selected = 0
        self.sorttypes = cycle(["title", "artist"])
        self.sorttype = next(self.sorttypes)

    def loop(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == K_DOWN:
                    self.selected += 1
                elif event.key == K_UP:
                    self.selected -= 1
                elif event.key == K_RETURN:
                    self.sorttype = next(self.sorttypes)
                    self.menu.sort(self.sorttype)

        self.selected %= len(self.menu.items)
        self.menu.selected = self.selected

        self.menu.update()

        sel_item = T(self.menu.selected_item.key, font = "Lato Medium", size = 16, color = "yellow").render()
        sel_dest = sel_item.get_rect()
        sel_dest.bottomleft = self.surface.get_rect().bottomleft

        menusurf = self.menu.render()

        self.surface.blit(menusurf, (5, 5))
        self.surface.blit(sel_item, sel_dest)


Game().run()
