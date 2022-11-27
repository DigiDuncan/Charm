from dataclasses import dataclass

from charm.lib.generic.engine import Judgement
from charm.lib.generic.song import Seconds

@dataclass
class Results:
    hit_window: Seconds
    judgements: list[Judgement]
    all_judgements: list[tuple[Seconds, Seconds, Judgement]]
    score: int
    hits: int
    misses: int
    accuracy: float
    grade: str
    fc_type: str
    streak: int
    max_streak: int