from dataclasses import dataclass

@dataclass
class Song:
    """Very much a stub."""
    title: str
    artist: str = "Unknown Artist"
    album: str = "Unknown Album"
    grade: str = None
