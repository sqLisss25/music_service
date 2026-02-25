from dataclasses import dataclass


@dataclass
class Genre:
    id: str
    name: str
    description: str

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return self.__str__()
