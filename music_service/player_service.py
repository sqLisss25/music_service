from typing import Optional
from pathlib import Path

from PySide6.QtCore import QObject, Signal, QUrl, QTimer
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput

from models import Song


class PlayerService(QObject):
    """сервис управляющий воспроизведением музыки"""

    # Signals
    position_changed = Signal(int)  # milliseconds
    duration_changed = Signal(int)  # milliseconds
    state_changed = Signal(QMediaPlayer.PlaybackState)
    track_finished = Signal()

    def __init__(self, songs_dir: str = "data/songs"):
        super().__init__()
        self.songs_dir = Path(songs_dir)

        # Media player
        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)

        # Current song
        self.current_song: Optional[Song] = None

        # Connect signals
        self.player.positionChanged.connect(self._on_position_changed)
        self.player.durationChanged.connect(self._on_duration_changed)
        self.player.playbackStateChanged.connect(self._on_state_changed)
        self.player.mediaStatusChanged.connect(self._on_media_status_changed)

    def load(self, song: Song) -> None:
        self.current_song = song
        song_path = self.songs_dir / song.filename

        if not song_path.exists():
            raise FileNotFoundError(f"Song file not found: {song_path}")

        url = QUrl.fromLocalFile(str(song_path.absolute()))
        self.player.setSource(url)

    def play(self) -> None:
        self.player.play()

    def pause(self) -> None:
        self.player.pause()

    def toggle_play_pause(self) -> None:
        if self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.pause()
        else:
            self.play()

    def stop(self) -> None:
        self.player.stop()

    def seek(self, ms: int) -> None:
        """Seek to position in milliseconds"""
        self.player.setPosition(ms)

    def current_position_ms(self) -> int:
        """Get current position in milliseconds"""
        return self.player.position()

    def duration_ms(self) -> int:
        """Get duration in milliseconds"""
        return self.player.duration()

    def set_volume(self, volume: float) -> None:
        """Set volume (0.0 - 1.0)"""
        self.audio_output.setVolume(volume)

    def _on_position_changed(self, position: int) -> None:
        """Handle position changed"""
        self.position_changed.emit(position)

    def _on_duration_changed(self, duration: int) -> None:
        """Handle duration changed"""
        self.duration_changed.emit(duration)

    def _on_state_changed(self, state: QMediaPlayer.PlaybackState) -> None:
        """Handle state changed"""
        self.state_changed.emit(state)

    def _on_media_status_changed(self, status: QMediaPlayer.MediaStatus) -> None:
        """Handle media status changed"""
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            self.track_finished.emit()
