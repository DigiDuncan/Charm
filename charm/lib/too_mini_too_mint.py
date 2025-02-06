"""
Mini Mint 2

The second iteration of the stop gap between the old charm ui and the eventual mint ui library.
This version improves on the previous with better rendering pipelines, and a more solid visual
goal.

-- FEATURE GUIDE --

Spill Over : Parent elements can have smaller Min Sizes than their children. This can cause the children to be larger than their parents.

-- STYLE GUIDE --

class methods with an underscore at the start are `private` and should not be called by external objects.
These generally should also be ignored by subclasses. Such as `_recompute_rect`.

non built-in class methods with doublescores are 'abstract' and can be overridden by
subclasses. Such as `__recompute_layout__`.
"""

# TODO: Aspect ratio minimum / scaling (yoink from OSU!)

from __future__ import annotations
from enum import Enum, StrEnum
from uuid import uuid4, UUID
from typing import NamedTuple, Iterable, Protocol
import weakref

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
    CENTER = LRBT(0.5, 0.5, 0.5, 0.5)

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

# A 1 dimensional anchor enum for H/V Box, scaling etc
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

# How elements should respond to events in the waterfall
class EventResponse(Enum):
    IGNORE = 0 # Won't trigger off event, but will pass to parent
    PASS = 1 # Will trigger off event, and will pass to parent
    CAPTURE = 2 # Will trigger off event, but won't pass to parent
    BLOCK = 3 # Won't trigger off event, and won't pass to parent

class FrameFit(Enum):
    FIXED = 0 # The Frame will not change size even if the viewport grows in size. (I.E. no Zooming)
    WIDTH = 1 # Fits so that the frame width matches the viewport irrespective of height
    HEIGHT = 2 # Fits so tha the frame height matches the viewport irrespective of width
    MAX = 3 # Fits so that the largest frame area is picked irrespective of if that spills outside viewport
    MIN = 4 # Fits so that the smallest frame area is picked. This insures no spillage occurs
    

class Mint:
    """
    The Mint object acts as the root of an applications GUI.
    """

    RENDERABLES: dict[str, type[Renderable]] = {

    }

    @staticmethod
    def register_renderable(name: str, renderable: type):
        if name in Mint.RENDERABLES:
            # TODO: Log??
            return
        Mint.RENDERABLES[name] = renderable


    def __init__(self) -> None:
        pass

def register_renderable(name: str, renderable: type):
    Mint.register_renderable(name, renderable)

class Tree:
    """
    Tree's are the root of rendering, animations, and events in Mint (mintree!).

    An element's units are all based on the tree's frame, and only elements
    within the tree's viewport (or sub viewport) will be rendered.

    Tree's also hold the batch rendering objects for the various elements,
    and act as the link to the GL context for complex rendering operations.

    When an event is fired it runs depth-first through the nodes in the tree.

    Elements not in a tree won't be drawn.

    # TODO: depth testing, and depth sorting
    """

    def __init__(self) -> None:
        # The aspect respecting frame that Unit's size are based on.
        self._frame = None
        # The actual area rendered into. This doesn't need to match the frame.
        self._viewport = None
        # How the frame fits the viewport
        self._fit: FrameFit = FrameFit.FIXED

        # The root Element of the Tree, will have its bounds equal to the viewport
        self._root: Element | None = None
        # The current max depth of the tree
        self._current_depth = 0
        # The layers of the tree from lowest (root) to highest depth
        self._layers: list[weakref.WeakSet[Element]] = []
        # All member elements of the tree mapped to their currently stored depth.
        self._members: dict[UUID, int] = {}
        # All created renderables in the Tree.
        self._renderables: dict[str, Renderable] = {}
        # Whether the Tree clears empty layers when an element is removed
        self._auto_prune: bool = True

        # TODO: events

    # -- ELEMENT METHODS --

    def set_root(self, root: Element | None):
        if root is None:
            self.clear_root()
            return
        elif self._root is not None:
            self.clear_root()

        # Elements already impliment fully the functionality to 
        # add/remove from the tree so this is easy.
        self._root = root
        root.add_to_tree(self, 0)

    def clear_root(self):
        if self._root is None:
            return
        
        # Elements already impliment fully the functionality to 
        # add/remove from the tree so this is easy.
        self._root.remove_from_tree()

        # We force clear the renderables incase a custom element
        # forgets to remove itself from the renderable
        for renderable in self._renderables.values():
            renderable.clear()

    def _remove_element(self, element: Element):
        # This is a private method as you should use `element.remove_from_tree`.
        if element._tree != self:
            # TODO: complain
            pass

        uid = element._uid

        if uid not in self._members:
            return
        depth = self._members[uid]

        self._layers[depth].remove(element)
        if not self._layers[depth] and self._auto_prune:
            self.prune(depth)
        del self._members[uid]

        # This doesn't get rid of the finaliser, but maybe that's okay?

    def _finalise_element_uid(self, uid: UUID):
        # We need a finaliser which doesn't reference the element
        # as that would mean the finaliser never fires.
        if uid not in self._members:
            return
        
        depth = self._members[uid]
        if not self._layers[depth] and self._auto_prune:
            self.prune(depth)
        del self._members[uid]

    def _add_element(self, element: Element):
        # This is a private method as you should use `element.add_to_tree`.
        if element._tree != self:
            # TODO: complain
            return
        
        uid = element._uid
        depth = element.depth

        if depth == self._current_depth:
            self._layers.append(weakref.WeakSet())
            self._current_depth = len(self._layers)
        elif depth > self._current_depth:
            # TODO: Uhm...
            return
        
        if uid not in self._members:
            self._layers[depth].add(element)
            self._members[uid] = element.depth

            # This helps insure the Tree discards an element correctly when it is no longer referenced
            finaliser = weakref.finalize(element, self._finalise_element_uid, element._uid)
            finaliser.atexit = False
            return
        
        old = self._members[uid]
        
        if old == depth:
            return
        
        self._layers[old].remove(element)
        self._layers[depth].add(element)

    def prune(self, finish: int = 0):
        # Work from the end of the layers and remove all empty layers.
        # Does not handle floating layers (which should be impossible)
        for layer in self._layers[-1:finish:-1]:
            if layer:
                break
            self._layers.remove(layer)
        self._current_depth = len(self._layers)

    # -- RENDERABLE METHODS --

    def draw(self):
        for renderable in self._renderables.values():
            renderable.draw()

    def get_renderable(self, name: str) -> Renderable:
        if name not in self._renderables:
            self.add_renderable(name)

        return self._renderables[name]

    def add_renderable(self, name: str):
        if name in self._renderables:
            return
        
        if name not in Mint.RENDERABLES:
            raise ValueError(f"Renderable {name} not registered")
        
        self._renderables[name] = Mint.RENDERABLES[name]()

    # -- EVENT METHODS --

# |-- RENDERABLES --|

class Renderable(Protocol):
    # TODO: Figure renderables out pronto

    # a Renderable's __init__ has to have no required arguments.

    def draw(self) -> bool | None:
        ...

    def is_empty(self) -> bool:
        ...

    def is_full(self) -> bool:
        return False
    
    def clear(self) -> None:
        ...


class BuiltInRenderable(StrEnum):
    SPRITE = "builtin_sprite"
    TEXT = "builtin_text"
    BATCH = "builtin_batch"


# |-- ELEMENTS --|


class Element:

    def __init__(self, *, bounds: Rect | None = None, minimum: Vec2 = Vec2(), anchors: Anchors = None, offsets: Offsets = None, size: Vec2 = None, position: Vec2 = None, uid: UUID | None = None) -> None:
        self._uid: UUID = uid if uid is not None else uuid4()

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
        self._min_size: Vec2 = minimum
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

        # -- RENDERING AND EVENTS --
        self._tree: Tree | None = None
        self._depth: int = 0
        self._depth_offset: float = 0.0

        self._event_response: EventResponse = EventResponse.PASS  # TODO

        # -- NAVIGATION -- 
        self._links: dict = {}  # TODO

        # -- VALUES --

        if bounds is not None:
            self.set_bounds(bounds)

        if anchors is not None:
            self.anchors = anchors

        if offsets is not None:
            self.offsets = offsets

        if size is not None:
            self.size = size

        if position is not None:
            self.position = position
    
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
        self._has_changed_layout = True

    # -- TREE PROPERTIES --

    @property
    def tree(self) -> Tree | None:
        return self._tree
    
    @property
    def depth(self) -> int:
        return self._depth

    # -- TREE METHODS --

    def add_to_tree(self, tree: Tree | None, depth: int):
        if self._tree != None:
            self.remove_from_tree()
        self._depth = depth
        self._tree = tree

        if tree is not None:
            tree._add_element(self)
            self.__add_to_tree__()
    
        for child in self._children:
            child.add_to_tree(tree, depth+1)

    def __add_to_tree__(self):
        pass

    def remove_from_tree(self):
        if self._tree is None:
            return

        self.__remove_from_tree__()
        for child in self._children:
            child.remove_from_tree()
        
        self._tree = None


    def __remove_from_tree__(self):
        pass

    # |-- ELEMENT FUNCTIONALITY --|

    # -- LAYOUT METHODS --

    # Many of the element methods have a public private pair. This saves on boilerplate.
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
        if child in self._children or child is self:
            return False
        self._children.append(child)
        self.__add_child__(child)

        child.add_to_tree(self._tree, self._depth + 1)

        self._has_changed_layout = True
        return True
    
    def __add_child__(self, child: Element):
        pass
    
    def add_children(self, children: Iterable[Element]) -> bool:
        return all(self.add_child(child) for child in children)

    def remove_child(self, child: Element) -> bool:
        if child not in self._children:
            return False
        self._children.remove(child)
        self.__remove_child__(child)

        child.add_to_tree(None, 0) # Makes the child the root of it's own tree.

        self._has_changed_layout = True
        return True
    
    def __remove_child__(self, child: Element):
        pass
    
    def remove_children(self, children: Iterable[Element]) -> bool:
        return all(self.remove_child(child) for child in children)

    def move_child(self, child: Element, idx: int) -> bool:
        if child not in self._children:
            return False
        if -len(self._children) <= idx < len(self._children):
            old = self._children.index(child)
            self._children[idx], self._children[old] = self._children[old], self._children[idx]
            self.__move_child__(child, idx)
            self._has_changed_layout = True
            return True
        return False
    
    def __move_child__(self, child: Element, idx: int):
        pass

    def insert_child(self, child: Element, idx: int) -> bool:
        if child in self._children:
            return False
        self._children.insert(idx, child)
        self.__insert_child__(child, idx)

        child.add_to_tree(self._tree, self.depth + 1)

        self._has_changed_layout = True
        return True
    
    def __insert_child__(self, child: Element, idx: int):
        self.__add_child__(child)

    def get_child_idx(self, child: Element) -> int:
        return self._children.index(child)

    def has_child(self, child: Element) -> bool:
        return child in self._children
    

def debug_draw_element(element: Element, *, waterfall: bool = True, bounds: bool = False, rect: bool = True, anchors: bool = True):
    if element._has_changed_layout:
        element.recompute_layout(waterfall=True)

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