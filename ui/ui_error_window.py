from PySide6.QtWidgets import QDialog, QWidget, QVBoxLayout, QLabel, QPushButton
from PySide6.QtCore import QSize, Qt


class Ui_ErrorWindow(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("ErrorWindow")
        Dialog.setWindowTitle("Error")
        Dialog.setMinimumSize(QSize(280, 140))

        self.layout = QVBoxLayout(Dialog)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(10)

        self.layout.addStretch(1)

        self.label = QLabel("Error")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setWordWrap(True)
        self.layout.addWidget(self.label, alignment=Qt.AlignHCenter)

        self.pushButton = QPushButton("OK")
        self.pushButton.setFixedSize(100, 32)
        self.layout.addWidget(self.pushButton, alignment=Qt.AlignHCenter)

        self.pushButton.setDefault(True)

        self.layout.addStretch(1)


class ErrorWindow(QDialog, Ui_ErrorWindow):
    def __init__(self, message: str):
        super().__init__()
        self.setupUi(self)
        self.label.setText(message)
        self.pushButton.clicked.connect(self.accept)
