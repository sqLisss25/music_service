from typing import Optional
from dataclasses import dataclass


@dataclass
class Song:
    id: str
    title: str
    artist: str
    album: str
    genre: str
    duration: int  # секунды
    filename: str

    def __str__(self) -> str:
        return f"{self.artist} - {self.title}"

    def __repr__(self) -> str:
        return self.__str__()

    def get_duration_formatted(self) -> str:
        # время в формате ММ:СС
        minutes = self.duration // 60
        seconds = self.duration % 60
        return f"{minutes}:{seconds:02d}"
