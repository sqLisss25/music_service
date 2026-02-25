from typing import List
from dataclasses import dataclass


@dataclass
class Album:
    id: str
    title: str
    artist: str
    cover: str
    songs: List[str]
    release_date: str

    def __str__(self) -> str:
        return f"{self.artist} - {self.title}"

    def __repr__(self) -> str:
        return self.__str__()
