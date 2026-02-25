from typing import List
from dataclasses import dataclass


@dataclass
class Playlist:
    id: str
    title: str
    description: str
    author: str
    songs: List[str]

    def __str__(self) -> str:
        return self.title

    def __repr__(self) -> str:
        return self.__str__()
