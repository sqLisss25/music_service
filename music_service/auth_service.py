import hashlib
from typing import Optional, Tuple
import secrets

from models import User, Library
from music_service.database import Database
from is_email import is_email


class AuthService:
    """логин/регистрация/удаление аккаунта"""

    def __init__(self, database: Database):
        self.database = database

    @staticmethod
    def hash_password(password: str) -> str:
        return hashlib.md5(password.encode()).hexdigest()

    def login(self, email: str, password: str) -> Tuple[bool, Optional[User], str]:
        """Return: success, user, error_message"""
        # Validate email format
        if not is_email(email):
            return False, None, "Неверный формат почты"

        # Check if user exists
        user = self.database.get_user(email)
        if user is None:
            return False, None, "Пользователь не найден"

        # Check password
        password_hash = self.hash_password(password)
        if user.password_hash != password_hash:
            return False, None, "Неверный пароль"

        return True, user, ""

    def register(self, email: str, username: str, password: str, repeat_password: str) -> Tuple[bool, Optional[User], str]:
        """Return: success, user, error_message"""
        if not is_email(email):
            return False, None, "неверный формат почты"

        if self.database.get_user(email) is not None:
            return False, None, "данная почта уже занята"

        if not username.strip():
            return False, None, "имя пользователя не может быть пустым"

        if password != repeat_password:
            return False, None, "пароли не совпадают"

        if len(password) < 4:
            return False, None, "Пароль должен быть длиннее 4 символов"

        # создаем новую библиотеку для пользователя
        library_id = secrets.token_hex(8)
        library = Library(
            id=library_id,
            songs=[],
            albums=[],
            playlists=[]
        )
        self.database.libraries[library_id] = library
        self.database.save_libraries()

        # создаем нового пользователя
        user = User(
            email=email,
            username=username,
            password_hash=self.hash_password(password),
            library_id=library_id
        )

        self.database.add_user(user)

        return True, user, ""

    def delete_account(self, email: str) -> None:
        """удаление аккаунта"""
        self.database.delete_user(email)
