from pathlib import Path

from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QTextEdit, QPushButton
from PySide6.QtCore import Qt

from models import Song
from music_service.database import Database


class TrackInfoWindow(QDialog):
    def __init__(self, song: Song, database: Database):
        super().__init__()
        self.song = song
        self.database = database

        self.setWindowTitle("Track Info")
        self.setMinimumSize(400, 300)

        layout = QVBoxLayout(self)

        # Info text
        info_text = QTextEdit()
        info_text.setReadOnly(True)

        album = database.get_album(song.album)
        genre = database.get_genre(song.genre)

        info = f"""
<b>Title:</b> {song.title}<br>
<b>Artist:</b> {song.artist}<br>
<b>Album:</b> {album.title if album else 'Unknown'}<br>
<b>Genre:</b> {genre.name if genre else 'Unknown'}<br>
<b>Duration:</b> {song.get_duration_formatted()}<br>
<b>File:</b> {song.filename}
        """

        info_text.setHtml(info.strip())
        layout.addWidget(info_text)

        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn, alignment=Qt.AlignCenter)
