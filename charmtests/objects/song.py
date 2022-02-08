from dataclasses import dataclass


@dataclass
class Song:
    """Very much a stub."""
    title: str
    artist: str = "Unknown Artist"
    album: str = "Unknown Album"
    grade: str = None
    length: int = 180
    difficulty: int = 3
    best_score: int = 0
