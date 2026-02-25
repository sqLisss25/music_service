from pathlib import Path

from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QTextEdit, QPushButton
from PySide6.QtCore import Qt

from models import Song


class TextWindow(QDialog):
    def __init__(self, song: Song, text_path: Path):
        super().__init__()
        self.song = song
        self.text_path = text_path

        self.setWindowTitle(f"Lyrics - {song.title}")
        self.setMinimumSize(500, 600)

        layout = QVBoxLayout(self)

        # Title
        title = QLabel(f"{song.artist} - {song.title}")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(title)

        # Lyrics
        lyrics_text = QTextEdit()
        lyrics_text.setReadOnly(True)

        try:
            with open(text_path, 'r', encoding='utf-8') as f:
                lyrics = f.read()
            lyrics_text.setPlainText(lyrics)
        except Exception as e:
            lyrics_text.setPlainText(f"Lyrics not found")

        layout.addWidget(lyrics_text)

        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn, alignment=Qt.AlignCenter)
