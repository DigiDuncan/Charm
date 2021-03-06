from functools import wraps
from typing import Callable, Iterable, Tuple, Iterator, TypeVar, Optional


def nice_time(seconds: float, milliseconds = False):
    ms = seconds % 1
    ms = int(ms * 1000)
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    h, m, s = int(h), int(m), int(s)
    o = f'{h:}:{m:02}:{s:02d}'
    if milliseconds:
        o += f'.{ms:03d}'
    return o


def clamp(minVal, val, maxVal):
    if minVal is None:
        minVal = float("-inf")
    if maxVal is None:
        maxVal = float("inf")
    return max(minVal, min(maxVal, val))


def default_itemgetter(name, default=None):
    def getter(o):
        return getattr(o, name, default)
    return getter


def maxTuple(d: dict, absolute = False) -> Tuple:
    rev = {v: k for k, v in d.items()}
    absmap = {abs(v): v for v in d.values()}
    if absolute:
        values = []
        for v in d.values():
            values.append(abs(v))
        maxv = max(values)
        return (rev[absmap[maxv]], absmap[maxv])
    else:
        values = []
        for v in d.values():
            values.append(v)
        maxv = max(values)
        return (rev[maxv], maxv)


def degreesToXY(degrees: int) -> dict:
    # TODO: Genericize this.
    degmap = {
        0:   {"x": 0,  "y": -1},
        90:  {"x": 1,  "y": 0},
        180: {"x": 0,  "y": 1},
        270: {"x": -1, "y": 0}
    }

    degrees = degrees % 360
    if degrees not in degmap.keys():
        raise ValueError(f"{degrees} is not a supported degree.")

    return degmap[degrees]


def cache_on(*attrs):
    oldvals = ()
    cached_result = None

    def wrapper(fn):
        @wraps(fn)
        def wrapped(self, *args, **kwargs):
            nonlocal oldvals
            nonlocal cached_result
            newvals = tuple(getattr(self, name) for name in attrs)
            if oldvals != newvals:
                oldvals = newvals
                cached_result = fn(self, *args, **kwargs)
            return cached_result
        return wrapped
    return wrapper


T = TypeVar("T")


def getone(items: Iterator[T]) -> Optional[T]:
    try:
        return next(items)
    except StopIteration:
        return None


def findone(items: Iterator[T], predicate: Callable[[T], bool]) -> Optional[T]:
    try:
        return next(filter(predicate, items))
    except StopIteration:
        return None


def denumerate(fn: Callable):
    def wrapped(args):
        i, item = args
        return fn(item)
    return wrapped


def findindex(items: Iterator[T], predicate: Callable[[T], bool]) -> Optional[T]:
    try:
        i, _ = next(filter(denumerate(predicate), enumerate(items)))
        return i
    except StopIteration:
        return None


def onoff(state: bool):
    return "ON" if state else "OFF"


def linear_one_to_zero(start, duration, current):
    end = start + duration
    if current < start:
        return 1
    if current > end:
        return 0
    return -(1 / duration) * current + (end / duration)


def truncate(s, amount) -> str:
    if len(s) > amount:
        return s[:amount - 3] + "..."
    return s
