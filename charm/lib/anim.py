import math

from .utils import clamp


def find_percent(start: float, end: float, time: float) -> float:
    """Convert a number to its progress through the range start -> end, from 0 to 1.

    https://www.desmos.com/calculator/d2qdk3lceh"""
    if end - start == 0:
        return 1
    y = ((1 / (end - start)) * time) - (start / (end - start))
    return clamp(0, y, 1)


def lerp(start: float, end: float, i: float) -> float:
    """Convert a number between 0 and 1 to be the progress within a range start -> end."""
    return start + (i * (end - start))


def bounce(n: float, m: float, bpm: float, x: float) -> float:
    """Create a bouncing motion between max(0, n) and m at bpm at time x."""
    return max(abs(math.sin(x * math.pi * (bpm / 60))) * m, n)


def ease_linear(minimum: float, maximum: float, start: float, end: float, x: float) -> float:
    """* `minimum: float`: the value returned by f(`x`) = `start`, often a position
       * `maximum: float`: the value returned by f(`x`) = `end`, often a position
       * `start: float`: the beginning of the transition, often a time
       * `end: float`: the end of the transition, often a time
       * `x: float`: the current x, often a time"""
    x = find_percent(start, end, x)
    return lerp(minimum, maximum, x)


def ease_quadinout(minimum: float, maximum: float, start: float, end: float, x: float) -> float:
    """https://easings.net/#easeInOutQuad"""
    x = find_percent(start, end, x)
    if x < 0.5:
        zo = 2 * x * x
    else:
        zo = 1 - math.pow(-2 * x + 2, 2) / 2
    return lerp(minimum, maximum, zo)


def ease_quartout(minimum: float, maximum: float, start: float, end: float, x: float) -> float:
    """https://easings.net/#easeOutQuart"""
    x = find_percent(start, end, x)
    zo = 1 - math.pow(1 - x, 4)
    return lerp(minimum, maximum, zo)


def ease_circout(minimum: float, maximum: float, start: float, end: float, x: float) -> float:
    """https://easings.net/#easeOutCirc"""
    x = find_percent(start, end, x)
    zo = math.sqrt(1 - math.pow(x - 1, 2))
    return lerp(minimum, maximum, zo)
