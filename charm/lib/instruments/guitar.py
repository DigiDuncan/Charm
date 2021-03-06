from typing import Literal, Tuple
from charm.lib.utils import onoff
from nygame import Coord
from .instrument import Instrument, InstrumentEvent

Tristate = Literal[-1, 0, 1]

arrows = " ←→↑↓↖↗↘↙"
dir2arrow = {
    (-1, 1): arrows[5],
    (0, 1): arrows[3],
    (1, 1): arrows[6],
    (-1, 0): arrows[1],
    (0, 0): arrows[0],
    (1, 0): arrows[2],
    (-1, -1): arrows[8],
    (0, -1): arrows[4],
    (1, -1): arrows[7]
}


def num2bar(num, token, w=20):
    hardnum = int(num * (w - 1))
    left = hardnum + 1
    right = w - left
    return format(token, f">{left}") + (right * " ")


class Guitar(Instrument):
    def __init__(self, joydev):
        super().__init__(joydev)
        self._frets = [False] * 5
        self._star = False
        self._start = False
        self._joy = Coord(0, 0)
        self._whammy = False
        self._whammy_pos = 0

    @property
    def fret1(self) -> bool:
        return self._frets[0]

    green = fret1

    @property
    def fret2(self) -> bool:
        return self._frets[1]

    red = fret2

    @property
    def fret3(self) -> bool:
        return self._frets[2]

    yellow = fret3

    @property
    def fret4(self) -> bool:
        return self._frets[3]

    blue = fret4

    @property
    def fret5(self) -> bool:
        return self._frets[4]

    orange = fret5

    @property
    def shape(self):
        return (self.fret1, self.fret2, self.fret3, self.fret4, self.fret5)

    @property
    def star(self) -> bool:
        return self._star

    @property
    def start(self) -> bool:
        return self._start

    @property
    def strumbar(self) -> Tristate:
        return self._joy[1]

    @property
    def strumup(self) -> bool:
        return self.strumbar == 1

    @property
    def strumdown(self) -> bool:
        return self.strumbar == -1

    @property
    def joy(self) -> Coord:
        return self._joy

    @property
    def whammy(self) -> bool:
        return self._whammy

    @property
    def whammy_pos(self):
        return self._whammy_pos

    @property
    def debug(self):
        fretstr = ''.join(str(int(f)) for f in self._frets)
        btnstr = f"{int(self._select)}{int(self._start)}"
        joystr = dir2arrow[tuple(self._joy)]
        tiltstr = num2bar(self._tilt, "o")
        whamstr = num2bar(self._whammy, "/")
        return f"[ {fretstr} {btnstr} ]   [ {joystr} ]   [{tiltstr}]   [{whamstr}]"


class ToggleEvent(InstrumentEvent):
    def __init__(self, tracktime: float, state: bool):
        name = f"{self._prefix}_{onoff(state)}"
        super().__init__(name, tracktime)


class FretEvent(ToggleEvent):
    _prefix = "FRET"

    def __init__(self, tracktime: float, state: bool, fretnum: int, shape: Tuple[bool]):
        super().__init__(tracktime, state)
        self.fretnum = fretnum
        self.shape = shape

    @property
    def fretcolor(self) -> str:
        return ["green", "red", "yellow", "blue", "orange"][self.fretnum - 1]

    def __str__(self):
        return f"{self.name}({self.fretnum}, {self.fretcolor})"


class WhammyEvent(ToggleEvent):
    _prefix = "WHAMMY"


class StarEvent(ToggleEvent):
    _prefix = "STAR"


class StartEvent(ToggleEvent):
    _prefix = "START"


class StrumEvent(ToggleEvent):
    _prefix = "STRUM"

    def __init__(self, tracktime: float, state: bool, shape: Tuple[bool]):
        super().__init__(tracktime, state)
        self.shape = shape


class JoyEvent(ToggleEvent):
    _prefix = "JOY"

    def __init__(self, tracktime: float, state: bool, direction: Literal["UP", "DOWN", "LEFT", "RIGHT"]):
        super().__init__(tracktime, state)
        self.direction = direction

    def __str__(self):
        return f"{self.name}({self.direction})"


class WhammyMotion(InstrumentEvent):
    def __init__(self, tracktime: float, position: float):
        super().__init__("WHAMMY_MOTION", tracktime)
        self.position = position

    def __str__(self):
        return f"{self.name}({self.position})"
