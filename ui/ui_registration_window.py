from typing import TYPE_CHECKING

from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton
from PySide6.QtCore import QSize, Qt

if TYPE_CHECKING:
    from music_service.music_service import MusicService


class Ui_RegistrationWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("RegistrationWindow")
        MainWindow.setWindowTitle("Registration")
        MainWindow.setMinimumSize(QSize(280, 420))

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

        # username
        self.label_username = QLabel("Username")
        self.layout.addWidget(self.label_username, alignment=Qt.AlignHCenter)
        self.line_username = QLineEdit()
        self.line_username.setFixedWidth(200)
        self.layout.addWidget(self.line_username, alignment=Qt.AlignHCenter)

        # password
        self.label_password = QLabel("Password")
        self.layout.addWidget(self.label_password, alignment=Qt.AlignHCenter)
        self.line_password = QLineEdit()
        self.line_password.setEchoMode(QLineEdit.Password)
        self.line_password.setFixedWidth(200)
        self.layout.addWidget(self.line_password, alignment=Qt.AlignHCenter)

        # repeat password
        self.label_repeat = QLabel("Repeat password")
        self.layout.addWidget(self.label_repeat, alignment=Qt.AlignHCenter)
        self.line_repeat = QLineEdit()
        self.line_repeat.setEchoMode(QLineEdit.Password)
        self.line_repeat.setFixedWidth(200)
        self.layout.addWidget(self.line_repeat, alignment=Qt.AlignHCenter)

        # button
        self.push_create = QPushButton("Create")
        self.push_create.setFixedSize(100, 32)
        self.layout.addWidget(self.push_create, alignment=Qt.AlignHCenter)
        self.push_create.setDefault(True)

        self.layout.addStretch(1)


class RegistrationWindow(QMainWindow, Ui_RegistrationWindow):
    def __init__(self, music_service: 'MusicService'):
        super().__init__()
        self.music_service = music_service
        self.setupUi(self)

        # Connect signals
        self.push_create.clicked.connect(self._on_create)
        self.line_repeat.returnPressed.connect(self._on_create)

    def _on_create(self) -> None:
        """Handle create button click"""
        email = self.line_email.text().strip()
        username = self.line_username.text().strip()
        password = self.line_password.text()
        repeat = self.line_repeat.text()

        self.music_service.handle_registration(email, username, password, repeat)
