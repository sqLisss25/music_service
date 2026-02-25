from typing import List, Optional
import secrets

from models import Playlist, Song, Library
from music_service.database import Database


class PlaylistService:
    """сервис управляющий плейлистами"""

    def __init__(self, database: Database):
        self.database = database

    def create_playlist(self, title: str, description: str, author: str, song_ids: List[str]) -> Playlist:
        playlist_id = secrets.token_hex(8)

        playlist = Playlist(
            id=playlist_id,
            title=title,
            description=description,
            author=author,
            songs=song_ids
        )

        self.database.add_playlist(playlist)

        return playlist

    def add_song_to_playlist(self, playlist: Playlist, song_id: str) -> None:
        if song_id not in playlist.songs:
            playlist.songs.append(song_id)
            self.database.update_playlist(playlist)

    def remove_song_from_playlist(self, playlist: Playlist, song_id: str) -> None:
        if song_id in playlist.songs:
            playlist.songs.remove(song_id)
            self.database.update_playlist(playlist)

    def delete_playlist(self, playlist_id: str, library: Library) -> None:
        # убрать из библиотеки
        if playlist_id in library.playlists:
            library.playlists.remove(playlist_id)
            self.database.update_library(library)

        # удалить плейлист
        self.database.delete_playlist(playlist_id)

    def get_playlist_songs(self, playlist: Playlist) -> List[Song]:
        songs = []
        for song_id in playlist.songs:
            song = self.database.get_song(song_id)
            if song:
                songs.append(song)
        return songs

    def get_user_playlists(self, library: Library) -> List[Playlist]:
        playlists = []
        for playlist_id in library.playlists:
            playlist = self.database.get_playlist(playlist_id)
            if playlist:
                playlists.append(playlist)
        return playlists

    def add_playlist_to_library(self, library: Library, playlist_id: str) -> None:
        if playlist_id not in library.playlists:
            library.playlists.append(playlist_id)
            self.database.update_library(library)
