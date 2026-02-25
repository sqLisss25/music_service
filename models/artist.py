from dataclasses import dataclass


@dataclass
class Artist:
    name: str

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return self.__str__()
