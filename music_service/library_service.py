from typing import List

from models import Library, Song, Album
from music_service.database import Database


class LibraryService:
    """здравствуйте, дайте мне красивую книгу"""

    def __init__(self, database: Database):
        self.database = database

    def add_song_to_library(self, library: Library, song_id: str) -> None:
        if song_id not in library.songs:
            library.songs.append(song_id)
            self.database.update_library(library)

    def remove_song_from_library(self, library: Library, song_id: str) -> None:
        if song_id in library.songs:
            library.songs.remove(song_id)
            self.database.update_library(library)

    def is_song_in_library(self, library: Library, song_id: str) -> bool:
        return song_id in library.songs

    def get_library_songs(self, library: Library) -> List[Song]:
        songs = []
        for song_id in library.songs:
            song = self.database.get_song(song_id)
            if song:
                songs.append(song)
        return songs

    def get_library_albums(self, library: Library) -> List[Album]:
        albums = []
        album_ids = set()

        for song_id in library.songs:
            song = self.database.get_song(song_id)
            if song and song.album not in album_ids:
                album = self.database.get_album(song.album)
                if album:
                    albums.append(album)
                    album_ids.add(song.album)

        return albums

    def get_library_artists(self, library: Library) -> List[str]:
        artists = set()

        for song_id in library.songs:
            song = self.database.get_song(song_id)
            if song:
                artists.add(song.artist)

        return sorted(list(artists))

    def get_library_genres(self, library: Library) -> List[str]:
        genres = set()

        for song_id in library.songs:
            song = self.database.get_song(song_id)
            if song:
                genres.add(song.genre)

        return sorted(list(genres))
