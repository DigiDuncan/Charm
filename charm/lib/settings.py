from dataclasses import dataclass


@dataclass
class Settings:
    width: int = 1280
    height: int = 720
    fps: int = 240
    volume: float = 1
