from dataclasses import dataclass

from charm.lib.generic.engine import Judge, NoteJudgement

@dataclass
class Results:
    judge: Judge
    note_judgements: list[NoteJudgement]
    score: int
    accuracy: float
    grade: str
    fc_type: str
    max_streak: int
