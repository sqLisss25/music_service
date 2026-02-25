from typing import TYPE_CHECKING, List, Optional
from pathlib import Path

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QTreeWidget, QTreeWidgetItem,
    QListWidget, QListWidgetItem,
    QSlider, QMenu
)
from PySide6.QtCore import Qt, QSize, QTimer
from PySide6.QtGui import QPixmap, QAction
from PySide6.QtMultimedia import QMediaPlayer

from models import User, Library, Song, Album, Playlist
from ui.ui_track_info_window import TrackInfoWindow
from ui.ui_queue_window import QueueWindow
from ui.ui_create_playlist_window import CreatePlaylistWindow
from ui.ui_text_window import TextWindow

if TYPE_CHECKING:
    from music_service.music_service import MusicService


class SongListItem(QWidget):
    """Custom widget for song list item."""

    def __init__(self, song: Song, in_library: bool, album_title: str = "", genre_name: str = "", parent=None):
        super().__init__(parent)
        self.song = song

        layout = QHBoxLayout()
        layout.setContentsMargins(5, 4, 5, 4)
        layout.setSpacing(8)

        # Song info label with all details
        duration_str = song.get_duration_formatted()

        # Build display text: Artist - Title | Album | Genre | Duration
        info_parts = []
        info_parts.append(f"<b>{song.artist}</b> — {song.title}")

        details = []
        if album_title:
            details.append(album_title)
        if genre_name:
            details.append(genre_name)
        details.append(duration_str)

        if details:
            info_parts.append(f"<span style='color: gray;'>{' • '.join(details)}</span>")

        text = " &nbsp; ".join(info_parts)

        self.label = QLabel(text)
        self.label.setTextFormat(Qt.RichText)
        layout.addWidget(self.label, 1)

        # Library button
        self.lib_button = QPushButton("✓" if in_library else "+")
        self.lib_button.setFixedSize(30, 25)
        self.lib_button.setEnabled(not in_library)
        self.lib_button.setToolTip("Already in library" if in_library else "Add to library")
        layout.addWidget(self.lib_button)

        # Menu button
        self.menu_button = QPushButton("...")
        self.menu_button.setFixedSize(30, 25)
        self.menu_button.setToolTip("More actions")
        layout.addWidget(self.menu_button)

        self.setLayout(layout)

    def update_library_status(self, in_library: bool):
        """Update the library button status."""
        self.lib_button.setText("✓" if in_library else "+")
        self.lib_button.setEnabled(not in_library)
        self.lib_button.setToolTip("Already in library" if in_library else "Add to library")


class MainWindow(QMainWindow):
    def __init__(self, music_service: 'MusicService', user: User, library: Library):
        super().__init__()
        self.music_service = music_service
        self.user = user
        self.library = library

        # Current display state
        self.current_songs: List[Song] = []
        self._base_songs: List[Song] = []  # Full song list for filtering in Artists/Genres views
        self.current_category = "library/songs"

        self.setupUi()
        self.connect_signals()
        self.load_initial_data()

    def setupUi(self):
        """Setup UI"""
        self.setWindowTitle("Music Service")
        self.setMinimumSize(QSize(900, 600))

        # Central widget
        central = QWidget()
        self.setCentralWidget(central)

        # Main layout
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Left panel
        left_panel = self._create_left_panel()
        main_layout.addWidget(left_panel)

        # Center panel
        center_panel = self._create_center_panel()
        main_layout.addWidget(center_panel, 1)

        # Right panel (player)
        right_panel = self._create_right_panel()
        main_layout.addWidget(right_panel)

    def _create_left_panel(self) -> QWidget:
        """Create left navigation panel"""
        panel = QWidget()
        panel.setFixedWidth(200)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(5, 5, 5, 5)

        # Search
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search...")
        layout.addWidget(self.search_input)

        # Menu tree
        self.menu_tree = QTreeWidget()
        self.menu_tree.setHeaderHidden(True)

        # General
        general = QTreeWidgetItem(self.menu_tree, ["General"])
        QTreeWidgetItem(general, ["Artists"])
        QTreeWidgetItem(general, ["Albums"])
        QTreeWidgetItem(general, ["Songs"])
        QTreeWidgetItem(general, ["Genres"])

        # Library
        library_item = QTreeWidgetItem(self.menu_tree, ["Library"])
        QTreeWidgetItem(library_item, ["Artists"])
        QTreeWidgetItem(library_item, ["Albums"])
        QTreeWidgetItem(library_item, ["Songs"])
        QTreeWidgetItem(library_item, ["Genres"])

        # Playlists
        self.playlists_root = QTreeWidgetItem(self.menu_tree, ["Playlists"])
        QTreeWidgetItem(self.playlists_root, ["Create playlist"])

        self.menu_tree.expandAll()
        layout.addWidget(self.menu_tree)

        # Username and settings
        bottom_layout = QHBoxLayout()
        self.username_label = QLabel(self.user.username)
        bottom_layout.addWidget(self.username_label)

        self.settings_btn = QPushButton("...")
        self.settings_btn.setFixedWidth(30)
        bottom_layout.addWidget(self.settings_btn)

        layout.addLayout(bottom_layout)

        return panel

    def _create_center_panel(self) -> QWidget:
        """Create center content panel"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(5, 5, 5, 5)

        # Info label
        self.info_label = QLabel("Library / Songs")
        self.info_label.setFixedHeight(30)
        layout.addWidget(self.info_label)

        # Horizontal layout for extra content and main content
        content_layout = QHBoxLayout()

        # Extra content (artists/albums/genres list)
        self.extra_content = QListWidget()
        self.extra_content.setFixedWidth(150)
        self.extra_content.hide()
        content_layout.addWidget(self.extra_content)

        # Main content list (using QListWidget with custom SongListItem widgets)
        self.content_list = QListWidget()
        self.content_list.setAlternatingRowColors(True)
        self.content_list.setSpacing(1)
        content_layout.addWidget(self.content_list)

        layout.addLayout(content_layout)

        return panel

    def _create_right_panel(self) -> QWidget:
        """Create right player panel"""
        panel = QWidget()
        panel.setFixedWidth(200)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(5, 5, 5, 5)

        # Cover
        self.cover_label = QLabel()
        self.cover_label.setFixedSize(190, 190)
        self.cover_label.setScaledContents(True)
        self._set_default_cover()
        layout.addWidget(self.cover_label)

        # Title
        self.title_label = QLabel("No track")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setWordWrap(True)
        layout.addWidget(self.title_label)

        # Artist
        self.artist_label = QLabel("")
        self.artist_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.artist_label)

        # Slider
        self.position_slider = QSlider(Qt.Horizontal)
        self.position_slider.setMinimum(0)
        self.position_slider.setMaximum(1000)
        layout.addWidget(self.position_slider)

        # Time labels
        time_layout = QHBoxLayout()
        self.current_time_label = QLabel("0:00")
        self.duration_label = QLabel("0:00")
        time_layout.addWidget(self.current_time_label)
        time_layout.addStretch()
        time_layout.addWidget(self.duration_label)
        layout.addLayout(time_layout)

        # Playback controls
        controls_layout = QHBoxLayout()
        self.prev_btn = QPushButton("⏮")
        self.play_pause_btn = QPushButton("▶")
        self.next_btn = QPushButton("⏭")
        controls_layout.addWidget(self.prev_btn)
        controls_layout.addWidget(self.play_pause_btn)
        controls_layout.addWidget(self.next_btn)
        layout.addLayout(controls_layout)

        # Shuffle and repeat
        modes_layout = QHBoxLayout()
        self.shuffle_btn = QPushButton("🔀")
        self.repeat_btn = QPushButton("🔁")
        modes_layout.addWidget(self.shuffle_btn)
        modes_layout.addWidget(self.repeat_btn)
        layout.addLayout(modes_layout)

        # Info, text, queue buttons
        actions_layout = QHBoxLayout()
        self.info_btn = QPushButton("ℹ")
        self.text_btn = QPushButton("📄")
        self.queue_btn = QPushButton("📋")
        actions_layout.addWidget(self.info_btn)
        actions_layout.addWidget(self.text_btn)
        actions_layout.addWidget(self.queue_btn)
        layout.addLayout(actions_layout)

        layout.addStretch()

        return panel

    def connect_signals(self):
        """Connect signals and slots"""
        # Search
        self.search_input.textChanged.connect(self._on_search)

        # Menu
        self.menu_tree.itemClicked.connect(self._on_menu_clicked)

        # Content list double click
        self.content_list.itemDoubleClicked.connect(self._on_song_double_clicked)

        # Extra content
        self.extra_content.itemClicked.connect(self._on_extra_content_clicked)

        # Settings
        self.settings_btn.clicked.connect(self._on_settings_clicked)

        # Player controls
        self.play_pause_btn.clicked.connect(self._on_play_pause)
        self.prev_btn.clicked.connect(self._on_previous)
        self.next_btn.clicked.connect(self._on_next)
        self.shuffle_btn.clicked.connect(self._on_shuffle)
        self.repeat_btn.clicked.connect(self._on_repeat)

        # Player actions
        self.info_btn.clicked.connect(self._on_info)
        self.text_btn.clicked.connect(self._on_text)
        self.queue_btn.clicked.connect(self._on_queue)

        # Slider
        self.position_slider.sliderPressed.connect(self._on_slider_pressed)
        self.position_slider.sliderReleased.connect(self._on_slider_released)

        # Player service signals
        self.music_service.player_service.position_changed.connect(self._on_position_changed)
        self.music_service.player_service.duration_changed.connect(self._on_duration_changed)
        self.music_service.player_service.state_changed.connect(self._on_playback_state_changed)
        self.music_service.player_service.track_finished.connect(self._on_track_finished)

        # Queue service signals
        self.music_service.queue_service.current_changed.connect(self._on_queue_current_changed)

        # Position update timer
        self.position_timer = QTimer()
        self.position_timer.setInterval(500)
        self.position_timer.timeout.connect(self._update_position)
        self.position_timer.start()

        self.slider_pressed = False

    def load_initial_data(self):
        """Load initial data (library songs)"""
        self._load_library_songs()
        self._load_user_playlists()

    def _load_library_songs(self):
        """Load library songs into list"""
        self.current_category = "library/songs"
        self.info_label.setText("Library / Songs")
        self.extra_content.hide()

        songs = self.music_service.library_service.get_library_songs(self.library)
        songs.sort(key=lambda s: (s.artist, s.title))

        self._display_songs(songs)

    def _display_songs(self, songs: List[Song]):
        """Display songs in list using SongListItem widgets"""
        self.current_songs = songs
        self.content_list.clear()

        for song in songs:
            # Get album and genre info
            album = self.music_service.database.get_album(song.album)
            album_title = album.title if album else ""

            genre = self.music_service.database.get_genre(song.genre)
            genre_name = genre.name if genre else ""

            # Check if song is in library
            in_library = self.music_service.library_service.is_song_in_library(self.library, song.id)

            # Create custom widget
            item_widget = SongListItem(song, in_library, album_title, genre_name)

            # Connect signals
            item_widget.lib_button.clicked.connect(
                lambda checked, s=song, w=item_widget: self._on_add_to_library(s, w)
            )
            item_widget.menu_button.clicked.connect(
                lambda checked, s=song, w=item_widget: self._on_more_actions(s, w)
            )

            # Create list item and set widget
            list_item = QListWidgetItem()
            list_item.setSizeHint(item_widget.sizeHint())
            self.content_list.addItem(list_item)
            self.content_list.setItemWidget(list_item, item_widget)

    def _get_song_from_list_item(self, item: QListWidgetItem) -> Optional[Song]:
        """Get Song object from QListWidgetItem"""
        widget = self.content_list.itemWidget(item)
        if widget and isinstance(widget, SongListItem):
            return widget.song
        return None

    def _on_search(self, text: str):
        """Handle search"""
        if text.strip():
            songs = self.music_service.search_service.search_songs(text)
            songs.sort(key=lambda s: (s.artist, s.title))
            self.info_label.setText(f"Search results for: {text}")
            self.extra_content.hide()
            self._display_songs(songs)
        else:
            # Return to previous view
            self._load_library_songs()

    def _on_menu_clicked(self, item: QTreeWidgetItem, column: int):
        """Handle menu item click"""
        parent = item.parent()

        if parent is None:
            return

        parent_text = parent.text(0)
        item_text = item.text(0)

        if parent_text == "General":
            if item_text == "Artists":
                self._show_general_artists()
            elif item_text == "Albums":
                self._show_general_albums()
            elif item_text == "Songs":
                self._show_general_songs()
            elif item_text == "Genres":
                self._show_general_genres()

        elif parent_text == "Library":
            if item_text == "Artists":
                self._show_library_artists()
            elif item_text == "Albums":
                self._show_library_albums()
            elif item_text == "Songs":
                self._load_library_songs()
            elif item_text == "Genres":
                self._show_library_genres()

        elif parent_text == "Playlists":
            if item_text == "Create playlist":
                self._on_create_playlist()
            else:
                self._show_playlist(item_text)

    def _show_general_artists(self):
        """Show all artists"""
        self.info_label.setText("General / Artists")
        self.extra_content.show()
        self.extra_content.clear()

        artists = self.music_service.database.get_all_artists()
        artists.sort(key=lambda a: a.name)

        for artist in artists:
            self.extra_content.addItem(artist.name)

        # Store full song list for filtering, but don't display yet
        songs = self.music_service.database.get_all_songs()
        songs.sort(key=lambda s: (s.artist, s.title))
        self._base_songs = songs
        self.current_songs = []
        self.content_list.clear()

    def _show_general_albums(self):
        """Show all albums"""
        self.info_label.setText("General / Albums")
        self.extra_content.show()
        self.extra_content.clear()

        albums = self.music_service.database.get_all_albums()
        albums.sort(key=lambda a: (a.artist, a.title))

        for album in albums:
            self.extra_content.addItem(f"{album.artist} - {album.title}")

        # Don't display songs until an album is selected
        self.current_songs = []
        self.content_list.clear()

    def _show_general_songs(self):
        """Show all songs"""
        self.info_label.setText("General / Songs")
        self.extra_content.hide()

        songs = self.music_service.database.get_all_songs()
        songs.sort(key=lambda s: (s.artist, s.title))
        self._display_songs(songs)

    def _show_general_genres(self):
        """Show all genres"""
        self.info_label.setText("General / Genres")
        self.extra_content.show()
        self.extra_content.clear()

        genres = self.music_service.database.get_all_genres()
        genres.sort(key=lambda g: g.name)

        for genre in genres:
            self.extra_content.addItem(genre.name)

        # Store full song list for filtering, but don't display yet
        songs = self.music_service.database.get_all_songs()
        songs.sort(key=lambda s: (s.artist, s.title))
        self._base_songs = songs
        self.current_songs = []
        self.content_list.clear()

    def _show_library_artists(self):
        """Show library artists"""
        self.info_label.setText("Library / Artists")
        self.extra_content.show()
        self.extra_content.clear()

        artist_names = self.music_service.library_service.get_library_artists(self.library)

        for name in artist_names:
            self.extra_content.addItem(name)

        # Store library songs for filtering, but don't display yet
        songs = self.music_service.library_service.get_library_songs(self.library)
        songs.sort(key=lambda s: (s.artist, s.title))
        self._base_songs = songs
        self.current_songs = []
        self.content_list.clear()

    def _show_library_albums(self):
        """Show library albums"""
        self.info_label.setText("Library / Albums")
        self.extra_content.show()
        self.extra_content.clear()

        albums = self.music_service.library_service.get_library_albums(self.library)
        albums.sort(key=lambda a: (a.artist, a.title))

        for album in albums:
            self.extra_content.addItem(f"{album.artist} - {album.title}")

        # Don't display songs until an album is selected
        self.current_songs = []
        self.content_list.clear()

    def _show_library_genres(self):
        """Show library genres"""
        self.info_label.setText("Library / Genres")
        self.extra_content.show()
        self.extra_content.clear()

        genre_ids = self.music_service.library_service.get_library_genres(self.library)

        for genre_id in genre_ids:
            genre = self.music_service.database.get_genre(genre_id)
            if genre:
                self.extra_content.addItem(genre.name)

        # Store library songs for filtering, but don't display yet
        songs = self.music_service.library_service.get_library_songs(self.library)
        songs.sort(key=lambda s: (s.artist, s.title))
        self._base_songs = songs
        self.current_songs = []
        self.content_list.clear()

    def _show_playlist(self, playlist_title: str):
        """Show playlist songs"""
        # Find playlist by title
        playlist = None
        for p in self.music_service.playlist_service.get_user_playlists(self.library):
            if p.title == playlist_title:
                playlist = p
                break

        if playlist:
            self.info_label.setText(f"Playlist / {playlist.title}")
            self.extra_content.hide()

            songs = self.music_service.playlist_service.get_playlist_songs(playlist)
            self._display_songs(songs)

    def _on_extra_content_clicked(self, item: QListWidgetItem):
        """Handle extra content item click"""
        text = item.text()

        if "Artists" in self.info_label.text():
            # Filter by artist from base song list
            songs = [s for s in self._base_songs if s.artist == text]
            self._display_songs(songs)

        elif "Albums" in self.info_label.text():
            # Filter by album
            # Extract album title from "Artist - Album" format
            if " - " in text:
                artist, album_title = text.split(" - ", 1)
                # Find album
                album = None
                for a in self.music_service.database.get_all_albums():
                    if a.artist == artist and a.title == album_title:
                        album = a
                        break

                if album:
                    songs = []
                    for song_id in album.songs:
                        song = self.music_service.database.get_song(song_id)
                        if song:
                            songs.append(song)
                    self._display_songs(songs)

        elif "Genres" in self.info_label.text():
            # Filter by genre from base song list
            genre = None
            for g in self.music_service.database.get_all_genres():
                if g.name == text:
                    genre = g
                    break

            if genre:
                songs = [s for s in self._base_songs if s.genre == genre.id]
                self._display_songs(songs)

    def _on_song_double_clicked(self, item: QListWidgetItem):
        """Handle song double click - play song"""
        song = self._get_song_from_list_item(item)
        if song:
            try:
                index = self.current_songs.index(song)
                self._play_song_list(self.current_songs, index)
            except ValueError:
                # Song not in current list, just play it
                self._play_song_list([song], 0)

    def _play_song_list(self, songs: List[Song], index: int):
        """Play song from list"""
        self.music_service.queue_service.set_queue(songs, index)
        song = songs[index]
        self._play_song(song)

    def _play_song(self, song: Song):
        """Play a song"""
        try:
            self.music_service.player_service.load(song)
            self.music_service.player_service.play()
            self._update_player_display(song)
        except Exception as e:
            from ui.ui_error_window import ErrorWindow
            ErrorWindow(f"Failed to play song: {e}").exec()

    def _update_player_display(self, song: Song):
        """Update player display with song info"""
        self.title_label.setText(song.title)
        self.artist_label.setText(song.artist)

        # Load cover
        album = self.music_service.database.get_album(song.album)
        if album:
            cover_path = Path("data/covers") / f"cover_{album.cover}.jpg"
            if cover_path.exists():
                pixmap = QPixmap(str(cover_path))
                self.cover_label.setPixmap(pixmap)
            else:
                self._set_default_cover()
        else:
            self._set_default_cover()

    def _set_default_cover(self):
        """Set default cover image"""
        cover_path = Path("data/covers/cover_0.jpg")
        if cover_path.exists():
            pixmap = QPixmap(str(cover_path))
            self.cover_label.setPixmap(pixmap)

    def _on_add_to_library(self, song: Song, widget: SongListItem = None):
        """Add song to library"""
        self.music_service.library_service.add_song_to_library(self.library, song.id)
        # Update widget if provided
        if widget:
            widget.update_library_status(True)
        else:
            # Refresh entire display
            self._display_songs(self.current_songs)

    def _on_more_actions(self, song: Song, widget: SongListItem):
        """Show more actions menu"""
        menu = QMenu(self)

        in_library = self.music_service.library_service.is_song_in_library(self.library, song.id)

        if in_library:
            remove_lib = QAction("Remove from library", self)
            remove_lib.triggered.connect(lambda: self._remove_from_library(song))
            menu.addAction(remove_lib)
        else:
            add_lib = QAction("Add to library", self)
            add_lib.triggered.connect(lambda: self._on_add_to_library(song, widget))
            menu.addAction(add_lib)

        add_playlist = QAction("Add to playlist", self)
        add_playlist.triggered.connect(lambda: self._add_to_playlist(song))
        menu.addAction(add_playlist)

        menu.addSeparator()

        play = QAction("Play", self)
        play.triggered.connect(lambda: self._play_song_from_current(song))
        menu.addAction(play)

        play_next = QAction("Play next", self)
        play_next.triggered.connect(lambda: self._play_next(song))
        menu.addAction(play_next)

        add_queue = QAction("Add to end of queue", self)
        add_queue.triggered.connect(lambda: self._add_to_queue(song))
        menu.addAction(add_queue)

        menu.addSeparator()

        info = QAction("Info", self)
        info.triggered.connect(lambda: self._show_track_info(song))
        menu.addAction(info)

        # Show menu at button position
        menu.exec(widget.menu_button.mapToGlobal(widget.menu_button.rect().bottomLeft()))

    def _play_song_from_current(self, song: Song):
        """Play song from current list"""
        try:
            index = self.current_songs.index(song)
            self._play_song_list(self.current_songs, index)
        except ValueError:
            self._play_song_list([song], 0)

    def _remove_from_library(self, song: Song):
        """Remove song from library"""
        self.music_service.library_service.remove_song_from_library(self.library, song.id)
        # Refresh display
        self._display_songs(self.current_songs)

    def _add_to_playlist(self, song: Song):
        """Show add to playlist dialog"""
        playlists = self.music_service.playlist_service.get_user_playlists(self.library)

        if not playlists:
            from ui.ui_error_window import ErrorWindow
            ErrorWindow("You don't have any playlists. Create one first!").exec()
            return

        menu = QMenu(self)
        for playlist in playlists:
            action = QAction(playlist.title, self)
            action.triggered.connect(lambda checked, p=playlist, s=song: self._do_add_to_playlist(p, s))
            menu.addAction(action)

        menu.exec(self.mapToGlobal(self.content_list.viewport().mapToGlobal(
            self.content_list.visualItemRect(self.content_list.currentItem()).center())))

    def _do_add_to_playlist(self, playlist: Playlist, song: Song):
        """Add song to playlist"""
        self.music_service.playlist_service.add_song_to_playlist(playlist, song.id)

    def _play_next(self, song: Song):
        """Add song to play next in queue"""
        self.music_service.queue_service.enqueue_after_current(song)

    def _add_to_queue(self, song: Song):
        """Add song to end of queue"""
        self.music_service.queue_service.enqueue(song)

    def _show_track_info(self, song: Song):
        """Show track info window"""
        window = TrackInfoWindow(song, self.music_service.database)
        window.exec()

    def _on_settings_clicked(self):
        """Show settings menu"""
        menu = QMenu(self)

        logout = QAction("Logout", self)
        logout.triggered.connect(self._on_logout)
        menu.addAction(logout)

        delete = QAction("Delete account", self)
        delete.triggered.connect(self._on_delete_account)
        menu.addAction(delete)

        menu.exec(self.settings_btn.mapToGlobal(self.settings_btn.rect().bottomLeft()))

    def _on_logout(self):
        """Handle logout"""
        self.music_service.handle_logout()

    def _on_delete_account(self):
        """Handle delete account"""
        from PySide6.QtWidgets import QMessageBox
        reply = QMessageBox.question(
            self,
            "Delete Account",
            "Are you sure you want to delete your account? This action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.music_service.handle_delete_account()

    def _on_play_pause(self):
        """Handle play/pause button"""
        self.music_service.player_service.toggle_play_pause()

    def _on_playback_state_changed(self, state: QMediaPlayer.PlaybackState):
        """Handle playback state changes — update play/pause button icon"""
        if state == QMediaPlayer.PlaybackState.PlayingState:
            self.play_pause_btn.setText("⏸")
        else:
            self.play_pause_btn.setText("▶")

    def _on_previous(self):
        """Handle previous button"""
        song = self.music_service.queue_service.previous()
        if song:
            self._play_song(song)

    def _on_next(self):
        """Handle next button"""
        song = self.music_service.queue_service.next()
        if song:
            self._play_song(song)

    def _on_shuffle(self):
        """Handle shuffle button"""
        self.music_service.queue_service.toggle_shuffle()

        # Update button appearance
        if self.music_service.queue_service.shuffle_enabled:
            self.shuffle_btn.setStyleSheet("background-color: lightblue;")
        else:
            self.shuffle_btn.setStyleSheet("")

    def _on_repeat(self):
        """Handle repeat button"""
        self.music_service.queue_service.cycle_repeat_mode()

        # Update button text
        from music_service.queue_service import RepeatMode
        if self.music_service.queue_service.repeat_mode == RepeatMode.OFF:
            self.repeat_btn.setText("🔁")
            self.repeat_btn.setStyleSheet("")
        elif self.music_service.queue_service.repeat_mode == RepeatMode.ONE:
            self.repeat_btn.setText("🔂")
            self.repeat_btn.setStyleSheet("background-color: lightblue;")
        else:  # RepeatMode.ALL
            self.repeat_btn.setText("🔁")
            self.repeat_btn.setStyleSheet("background-color: lightgreen;")

    def _on_info(self):
        """Show info for current song"""
        song = self.music_service.queue_service.current_song()
        if song:
            self._show_track_info(song)

    def _on_text(self):
        """Show text for current song"""
        song = self.music_service.queue_service.current_song()
        if song:
            text_path = Path("data/text") / f"{song.filename.rsplit('.', 1)[0]}.txt"
            window = TextWindow(song, text_path)
            window.exec()
            # if text_path.exists():
            #     window = TextWindow(song, text_path)
            #     window.exec()
            # else:
            #     from ui.ui_error_window import ErrorWindow
            #     ErrorWindow("Lyrics not available for this song").exec()

    def _on_queue(self):
        """Show queue window"""
        window = QueueWindow(self.music_service.queue_service)
        window.exec()

    def _on_create_playlist(self):
        """Show create playlist window"""
        window = CreatePlaylistWindow(
            self.music_service,
            self.user.email,
            self.library
        )
        if window.exec():
            self._load_user_playlists()

    def _load_user_playlists(self):
        """Load user playlists into menu"""
        # Remove old playlist items
        while self.playlists_root.childCount() > 1:
            self.playlists_root.removeChild(self.playlists_root.child(1))

        # Add playlists
        playlists = self.music_service.playlist_service.get_user_playlists(self.library)
        for playlist in playlists:
            QTreeWidgetItem(self.playlists_root, [playlist.title])

    def _on_position_changed(self, position: int):
        """Handle position changed from player"""
        pass  # Handled by timer

    def _on_duration_changed(self, duration: int):
        """Handle duration changed from player"""
        self.position_slider.setMaximum(duration)
        minutes = duration // 60000
        seconds = (duration % 60000) // 1000
        self.duration_label.setText(f"{minutes}:{seconds:02d}")

    def _on_track_finished(self):
        """Handle track finished"""
        self._on_next()

    def _on_queue_current_changed(self, index: int):
        """Handle queue current song changed"""
        pass

    def _update_position(self):
        """Update position slider and label"""
        if not self.slider_pressed:
            position = self.music_service.player_service.current_position_ms()
            self.position_slider.blockSignals(True)
            self.position_slider.setValue(position)
            self.position_slider.blockSignals(False)

            minutes = position // 60000
            seconds = (position % 60000) // 1000
            self.current_time_label.setText(f"{minutes}:{seconds:02d}")

    def _on_slider_pressed(self):
        """Handle slider pressed"""
        self.slider_pressed = True

    def _on_slider_released(self):
        """Handle slider released"""
        self.slider_pressed = False
        position = self.position_slider.value()
        self.music_service.player_service.seek(position)