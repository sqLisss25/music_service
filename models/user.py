from typing import Optional
from dataclasses import dataclass


@dataclass
class User:
    email: str
    username: str
    password_hash: str
    library_id: str

    def __str__(self) -> str:
        return f"User({self.email}, {self.username})"

    def __repr__(self) -> str:
        return self.__str__()
