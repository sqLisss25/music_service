from typing import List
from dataclasses import dataclass


@dataclass
class Library:
    id: str
    songs: List[str]
    albums: List[str]
    playlists: List[str]

    def __str__(self) -> str:
        return f"Library({self.id})"

    def __repr__(self) -> str:
        return self.__str__()
