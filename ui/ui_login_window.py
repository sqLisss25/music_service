from typing import TYPE_CHECKING

from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton
from PySide6.QtCore import QSize, Qt

if TYPE_CHECKING:
    from music_service.music_service import MusicService


class Ui_LoginWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("LoginWindow")
        MainWindow.setWindowTitle("Login")
        MainWindow.setMinimumSize(QSize(280, 280))

        self.centralwidget = QWidget(MainWindow)
        MainWindow.setCentralWidget(self.centralwidget)

        self.layout = QVBoxLayout(self.centralwidget)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(10)
        self.layout.addStretch(1)

        # email
        self.label_email = QLabel("Email")
        self.layout.addWidget(self.label_email, alignment=Qt.AlignHCenter)
        self.line_email = QLineEdit()
        self.line_email.setFixedWidth(200)
        self.layout.addWidget(self.line_email, alignment=Qt.AlignHCenter)

        # password
        self.label_password = QLabel("Password")
        self.layout.addWidget(self.label_password, alignment=Qt.AlignHCenter)
        self.line_password = QLineEdit()
        self.line_password.setEchoMode(QLineEdit.Password)
        self.line_password.setFixedWidth(200)
        self.layout.addWidget(self.line_password, alignment=Qt.AlignHCenter)

        # buttons
        self.push_login = QPushButton("Log in")
        self.push_login.setFixedSize(100, 32)
        self.layout.addWidget(self.push_login, alignment=Qt.AlignHCenter)
        self.push_login.setDefault(True)

        self.push_create = QPushButton("Create new")
        self.push_create.setFixedSize(100, 32)
        self.layout.addWidget(self.push_create, alignment=Qt.AlignHCenter)

        self.layout.addStretch(1)


class LoginWindow(QMainWindow, Ui_LoginWindow):
    def __init__(self, music_service: 'MusicService'):
        super().__init__()
        self.music_service = music_service
        self.setupUi(self)

        # Connect signals
        self.push_login.clicked.connect(self._on_login)
        self.push_create.clicked.connect(self._on_create)
        self.line_password.returnPressed.connect(self._on_login)

    def _on_login(self) -> None:
        """Handle login button click"""
        email = self.line_email.text().strip()
        password = self.line_password.text()
        self.music_service.handle_login(email, password)

    def _on_create(self) -> None:
        """Handle create account button click"""
        self.music_service.show_registration_from_login()
