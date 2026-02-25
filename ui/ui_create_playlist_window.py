from typing import TYPE_CHECKING, List

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QTextEdit, QPushButton, QListWidget,
    QListWidgetItem, QAbstractItemView
)
from PySide6.QtCore import Qt

from models import Library

if TYPE_CHECKING:
    from music_service.music_service import MusicService


class CreatePlaylistWindow(QDialog):
    def __init__(self, music_service: 'MusicService', user_email: str, library: Library):
        super().__init__()
        self.music_service = music_service
        self.user_email = user_email
        self.library = library

        self.setWindowTitle("Create Playlist")
        self.setMinimumSize(500, 600)

        layout = QVBoxLayout(self)

        # Title
        title_label = QLabel("Playlist Title:")
        layout.addWidget(title_label)

        self.title_input = QLineEdit()
        layout.addWidget(self.title_input)

        # Description
        desc_label = QLabel("Description:")
        layout.addWidget(desc_label)

        self.desc_input = QTextEdit()
        self.desc_input.setMaximumHeight(80)
        layout.addWidget(self.desc_input)

        # Songs
        songs_label = QLabel("Select Songs:")
        layout.addWidget(songs_label)

        self.songs_list = QListWidget()
        self.songs_list.setSelectionMode(QAbstractItemView.MultiSelection)
        layout.addWidget(self.songs_list)

        # Load available songs
        self._load_songs()

        # Buttons
        btn_layout = QHBoxLayout()

        create_btn = QPushButton("Create")
        create_btn.clicked.connect(self._on_create)
        btn_layout.addWidget(create_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        layout.addLayout(btn_layout)

    def _load_songs(self):
        """Load available songs"""
        # Get all songs from database
        songs = self.music_service.database.get_all_songs()
        songs.sort(key=lambda s: (s.artist, s.title))

        for song in songs:
            item = QListWidgetItem(f"{song.artist} - {song.title}")
            item.setData(Qt.UserRole, song.id)
            self.songs_list.addItem(item)

    def _on_create(self):
        """Create playlist"""
        title = self.title_input.text().strip()
        description = self.desc_input.toPlainText().strip()

        if not title:
            from ui.ui_error_window import ErrorWindow
            ErrorWindow("Playlist title cannot be empty").exec()
            return

        # Get selected songs
        selected_song_ids = []
        for i in range(self.songs_list.count()):
            item = self.songs_list.item(i)
            if item.isSelected():
                selected_song_ids.append(item.data(Qt.UserRole))

        # Create playlist
        playlist = self.music_service.playlist_service.create_playlist(
            title=title,
            description=description,
            author=self.user_email,
            song_ids=selected_song_ids
        )

        # Add to library
        self.music_service.playlist_service.add_playlist_to_library(self.library, playlist.id)

        self.accept()
