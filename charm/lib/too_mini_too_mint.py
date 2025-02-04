"""
Mini Mint 2

The second iteration of the stop gap between the old charm ui and the eventual mint ui library.
This version improves on the previous with better rendering pipelines, and a more solid visual
goal.

-- FEATURE GUIDE --

Spill Over : Parent elements can have smaller Min Sizes than their children. This can cause the children to be larger than their parents.

-- STYLE GUIDE --

class methods with an underscore at the start are `private` and should not be called
by external objects. These generally should also be ignored by subclasses. Such as `_recompute_rect`.

non built-in class methods with doublescores are 'abstract' and can be overridden by
subclasses. Such as `__recompute_layout__`.
"""

from __future__ import annotations
from enum import Enum
from typing import NamedTuple
from arcade import Rect, LRBT, XYWH, Vec2

# -- DEBUG --
from arcade import draw_rect_outline, draw_point

# Rects generally with UV values (0.0 - 1.0)
type Anchors = Rect

# Unit values which represent axis aligned offsets from edges
class Offsets(NamedTuple):
    left: float = .0
    right: float = .0
    bottom: float = .0
    top: float = .0

# Useful anchor presets.
class AnchorPresets:
    FULL = LRBT(0.0, 1.0, 0.0, 1.0)

    LEFT = LRBT(0.0, 0.0, 0.0, 1.0)
    RIGHT = LRBT(1.0, 1.0, 0.0, 1.0)
    BOTTOM = LRBT(0.0, 1.0, 0.0, 0.0)
    TOP = LRBT(0.0, 1.0, 1.0, 1.0)
    
    BOTTOM_LEFT = LRBT(0.0, 0.0, 0.0, 0.0)
    BOTTOM_RIGHT = LRBT(1.0, 1.0, 0.0, 0.0)
    TOP_LEFT = LRBT(0.0, 0.0, 1.0, 1.0)
    TOP_RIGHT = LRBT(1.0, 1.0, 1.0, 1.0)

    HORIZONTAL = LRBT(0.0, 1.0, 0.5, 0.5)
    VERTICAL = LRBT(0.5, 0.5, 0.0, 1.0)

class AxisAnchor(Enum):
    BEGINNING = 0
    LEFT = 0
    TOP = 0

    CENTER = 1
    BOTH = 1
    MIDDLE = 1

    BOTTOM = 2
    RIGHT = 2
    END = 2

class Element:

    def __init__(self) -> None:
        # -- AREA VALUES --

        # The bounds is the area provided by the element's parent
        self._bounds: Rect | None = None
        # The rect is the area of the element that is actually utilised,
        # either divided among its children, or for its visual componenets
        self._rect: Rect = XYWH(0.0, 0.0, 0.0, 0.0)

        # -- AREA CONTROLS --

        # The anchors are fractional values which define the area of the bounds the element uses.
        # If the anchors have 0 area then the element won't change size along the axis with 0 size.
        self._anchors: Anchors = AnchorPresets.FULL
        # Offsets are unit values which represent offsets from the fractional anchors. 
        self._offsets: Offsets = Offsets()
        # The size of the element in units is derived from the anchors and offsets along with the bounds
        self._size: Vec2 = Vec2()
        # The position of the element is the location of its center in units derived from the anchors and offsets along with the bounds
        self._position: Vec2 = Vec2()

        # -- PARENT INTERACTIONS --

        # The minimum size in units the element will accept from its parent
        self._min_size: Vec2 = Vec2()
        # How the Element should grow in size/position when its min_size changes
        self._growth_horizontal: AxisAnchor = AxisAnchor.BOTH
        self._growth_vertical: AxisAnchor = AxisAnchor.BOTH
        # The priority of this element as weighted against the priority of other elements.
        # When 0.0 or less it will only be given the minimum amount.
        self._priority: float = 1.0

        # -- CHILD INTERACTIONS --

        # Whether this Element has a layout defining property change and so needs to update it's children's bounds
        self._has_changed_layout: bool = False
        # This elements children:
        self._children: list[Element] = []

    # |-- UTIL METHODS --|

    # -- LAYOUT PROPERTIES --

    @property
    def anchors(self) -> Anchors:
        return self._anchors
    
    @anchors.setter
    def anchors(self, anchors: Anchors) -> None:
        if anchors == self._anchors:
            return

        self._anchors = anchors
        self._recompute_rect()

        self._has_changed_layout = True

    @property
    def offsets(self) -> Offsets:
        return self._offsets
    
    @offsets.setter
    def offsets(self, offsets: Offsets) -> None:
        if offsets == self._offsets:
            return

        self._offsets = offsets
        self._recompute_rect()

        self._has_changed_layout = True

    @property
    def size(self) -> Vec2:
        return self._size
    
    @size.setter
    def size(self, size: Vec2) -> None:
        if size == self._size:
            return

        self._size = size
        self._rect = XYWH(self._position.x, self._position.y, size.x, size.y)
        self._recompute_offsets()

        self._has_changed_layout = True

    @property
    def position(self) -> Vec2:
        return self._position
    
    @position.setter
    def position(self, position: Vec2) -> None:
        if position == self._position:
            return

        self._position = position
        self._rect = XYWH(position.x, position.y, self._size.x, self._size.y)
        self._recompute_offsets()

        self._has_changed_layout = True

    @property
    def rect(self) -> Rect:
        return XYWH(self._position.x, self._position.y, self._size.x, self._size.y)
    
    @rect.setter
    def rect(self, rect: Rect) -> None:
        if rect == self._rect:
            return

        self._rect = rect
        
        self._position = rect.center
        self._size = rect.size
        self._recompute_offsets()

        self._has_changed_layout = True

    @property
    def bounds(self) -> Rect | None:
        return self._bounds
    
    @bounds.setter
    def bounds(self, bounds: Rect) -> None:
        if bounds == self._bounds:
            return

        self._bounds = bounds
        self._recompute_rect()

        self._has_changed_layout = True

    @property
    def min_size(self) -> Vec2:
        return self._min_size
    
    @min_size.setter
    def min_size(self, min_size: Vec2) -> None:
        if min_size == self._min_size:
            return
        
        if self._bounds is not None and (self._min_size.x < min_size.x or self._min_size.y < min_size.y):
            self._min_size = min_size
            self.set_bounds(self._bounds)
            return

        self._min_size = min_size

    # -- LAYOUT METHODS --

    def _recompute_rect(self):
        if self._bounds is None:
            left = right = bottom = top = 0.0
        else:
            left, bottom = self._bounds.uv_to_position(self._anchors.bottom_left)
            right, top = self._bounds.uv_to_position(self._anchors.top_right)
        
        offsets = self._offsets

        self._rect = LRBT(left + offsets.left, right + offsets.right, bottom + offsets.bottom, top + offsets.top)
        self._position = self._rect.center
        self._size = self._rect.size
    
    def _recompute_offsets(self):
        if self._bounds is None:
            left = right = bottom = top = 0.0
        else:
            left, bottom = self._bounds.uv_to_position(self._anchors.bottom_left)
            right, top = self._bounds.uv_to_position(self._anchors.top_right)

        rect = self.rect

        self._offsets = Offsets(rect.left - left, rect.right - right, rect.bottom - bottom, rect.top - top)

    def set_bounds(self, raw_bounds: Rect):
        """
        A util method that helps make sure the bounds account for the elements growth attribute.

        This only works because Mint Elements are 'spillover'. A child's minimum size may be
        greater than its parent's. In which case the parent may be given less room than the child needs.

        Args:
            raw_bounds: The bounds rect that might be large enough for the rect.
        """
        l, r, b, t = raw_bounds.lrbt

        if raw_bounds.width < self._min_size.x:
            match self._growth_horizontal:
                case AxisAnchor.BEGINNING:
                    r = l + self._min_size.x
                case AxisAnchor.BOTH:
                    l = (l + r - self._min_size.x) / 2.0
                    r = (l + r + self._min_size.x) / 2.0
                case AxisAnchor.END:
                    l = r - self._min_size.x

        if raw_bounds.height < self._min_size.y:
            match self._growth_vertical:
                case AxisAnchor.BEGINNING:
                    t = b + self._min_size.y
                case AxisAnchor.BOTH:
                    b = (b + t - self._min_size.y) / 2.0
                    t = (b + t + self._min_size.y) / 2.0
                case AxisAnchor.END:
                    b = t - self._min_size.y

        self.bounds = LRBT(l, r, b, t)

    # |-- ELEMENT FUNCTIONALITY --|

    # -- TREE METHODS --

    # Most of the element methods have a public private pair. This saves on boilerplate.
    def recompute_layout(self, force: bool = False, waterfall: bool = False):
        if not self._has_changed_layout and not force:
            return
        
        self.__recompute_layout__()

        if waterfall:
            for child in self._children:
                child.recompute_layout(force, waterfall)

    def __recompute_layout__(self):
        # The overridable function that defines how children recieve their bounds from their parent.
        rect = self._rect
        for child in self._children:
            child.set_bounds(rect)

    # -- CHILD METHODS --

    def add_child(self, child: Element) -> bool:
        if child in self._children:
            return False
        self._children.append(child)
        self._has_changed_layout = True
        return True

    def remove_child(self, child: Element) -> bool:
        if child not in self._children:
            return False
        self._children.remove(child)
        self._has_changed_layout = True
        return True

    def move_child(self, child: Element, idx: int) -> bool:
        if child not in self._children:
            return False
        if -len(self._children) <= idx < len(self._children):
            old = self._children.index(child)
            self._children[idx], self._children[old] = self._children[old], self._children[idx]
            self._has_changed_layout = True
            return True
        return False

    def insert_child(self, child: Element, idx: int) -> bool:
        if child in self._children:
            return False
        self._children.insert(idx, child)
        self._has_changed_layout = True
        return True

    def get_child_idx(self, child: Element) -> int:
        return self._children.index(child)

    def has_child(self, child: Element) -> bool:
        return child in self._children
    

def debug_draw_element(element: Element, *, waterfall: bool = True, bounds: bool = False, rect: bool = True, anchors: bool = True):
    if bounds and element.bounds is not None:
        draw_rect_outline(element.bounds, (255, 0, 0), 2)

    if rect:
        draw_rect_outline(element.rect, (0, 255, 0), 2)

    if anchors:
        if element._bounds is None:
            left = right = bottom = top = 0.0
        else:
            left, bottom = element._bounds.uv_to_position(element._anchors.bottom_left)
            right, top = element._bounds.uv_to_position(element._anchors.top_right)

        draw_point(left, bottom, (0, 0, 255), 4)
        draw_point(left, top, (0, 0, 255), 4)
        draw_point(right, bottom, (0, 0, 255), 4)
        draw_point(right, top, (0, 0, 255), 4)

    if waterfall:
        for child in element._children:
            debug_draw_element(child, waterfall=waterfall, bounds=bounds, rect=rect, anchors=anchors)