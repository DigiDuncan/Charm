class State:
    pass

class Element:
    def add_state(self, state: State, **kwargs):
        pass

class FrameElement(Element):
    core: Element = None
    bottom: Element = None


class TextureElement(Element):
    size: tuple[float, float] = None


class TextElement(Element):
    size: float = None


class SolidElement(Element):
    pass


class ListElement(Element):
    pass


MainMenuItem = FrameElement(
    bottom=TextElement()
)

MainMenuItemCore = TextureElement(
    size = (32, 32),
    opacity = 0.5
)

MainMenuItemCore.add_state(
    MainMenuItem.SELECTED,
    scale = 1.5,
    opacity = 1.0
)

MainMenuItem.core.add(MainMenuItemCore)

