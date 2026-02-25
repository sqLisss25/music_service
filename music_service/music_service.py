import sys
from typing import Optional

from PySide6.QtWidgets import QApplication

from models import User, Library
from music_service.database import Database
from music_service.auth_service import AuthService
from music_service.player_service import PlayerService
from music_service.queue_service import QueueService
from music_service.library_service import LibraryService
from music_service.playlist_service import PlaylistService
from music_service.search_service import SearchService

from ui.ui_login_window import LoginWindow
from ui.ui_registration_window import RegistrationWindow
from ui.ui_main_window import MainWindow
from ui.ui_error_window import ErrorWindow


class MusicService:
    """мьюзик сервис запускатор 3000"""

    def __init__(self):
        self.app = QApplication(sys.argv)

        # database
        try:
            self.database = Database()
        except Exception as e:
            self._show_error(f"ошибка инициализации database: {e}")
            sys.exit(1)

        # services
        self.auth_service = AuthService(self.database)
        self.player_service = PlayerService()
        self.queue_service = QueueService()
        self.library_service = LibraryService(self.database)
        self.playlist_service = PlaylistService(self.database)
        self.search_service = SearchService(self.database)

        # current user
        self.current_user: Optional[User] = None
        self.current_library: Optional[Library] = None

        # windows
        self.login_window: Optional[LoginWindow] = None
        self.registration_window: Optional[RegistrationWindow] = None
        self.main_window: Optional[MainWindow] = None

    def run(self) -> int:
        """запуск приложения"""
        self._show_login_window()
        return self.app.exec()

    def _show_login_window(self) -> None:
        """показать окно входа"""
        self.login_window = LoginWindow(self)
        self.login_window.show()

    def _show_registration_window(self) -> None:
        """показать окно ргеистрации"""
        self.registration_window = RegistrationWindow(self)
        self.registration_window.show()

    def _show_main_window(self) -> None:
        """показать главное окно"""
        if self.current_user and self.current_library:
            self.main_window = MainWindow(
                self,
                self.current_user,
                self.current_library
            )
            self.main_window.show()

    def handle_login(self, email: str, password: str) -> None:
        success, user, error = self.auth_service.login(email, password)

        if success and user:
            self.current_user = user
            self.current_library = self.database.get_library(user.library_id)

            if self.login_window:
                self.login_window.close()

            self._show_main_window()
        else:
            self._show_error(error)

    def handle_registration(self, email: str, username: str, password: str, repeat_password: str) -> None:
        success, user, error = self.auth_service.register(email, username, password, repeat_password)

        if success and user:
            self.current_user = user
            self.current_library = self.database.get_library(user.library_id)

            if self.registration_window:
                self.registration_window.close()

            self._show_main_window()
        else:
            self._show_error(error)

    def handle_logout(self) -> None:
        self.current_user = None
        self.current_library = None

        if self.main_window:
            self.main_window.close()

        self._show_login_window()

    def handle_delete_account(self) -> None:
        if self.current_user:
            self.auth_service.delete_account(self.current_user.email)
            self.handle_logout()

    def show_registration_from_login(self) -> None:
        if self.login_window:
            self.login_window.close()
        self._show_registration_window()

    def _show_error(self, message: str) -> None:
        error_window = ErrorWindow(message)
        error_window.exec()
