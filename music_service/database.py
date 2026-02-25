import json
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Optional

from models import User, Song, Album, Artist, Genre, Playlist, Library


class Database:
    """Класс для управления JSON и XML данными"""

    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)

        # Data storage
        self.users: Dict[str, User] = {}
        self.songs: Dict[str, Song] = {}
        self.albums: Dict[str, Album] = {}
        self.artists: Dict[str, Artist] = {}
        self.genres: Dict[str, Genre] = {}
        self.playlists: Dict[str, Playlist] = {}
        self.libraries: Dict[str, Library] = {}

        # Load all data
        self.load_all()

    def load_all(self) -> None:
        """подгружает ВСЕ данные"""
        try:
            self.load_genres()
            self.load_users()
            self.load_albums()
            self.load_songs()
            self.load_playlists()
            self.load_libraries()
            self.extract_artists()
        except Exception as e:
            raise RuntimeError(f"Ошибка загрузки Database: {e}")

    def load_genres(self) -> None:
        xml_path = self.data_dir / "genres.xml"
        try:
            tree = ET.parse(xml_path)
            root = tree.getroot()

            for genre_elem in root.findall('genre'):
                genre_id = genre_elem.get('id')
                name = genre_elem.find('name').text
                description = genre_elem.find('description').text

                self.genres[genre_id] = Genre(
                    id=genre_id,
                    name=name,
                    description=description
                )
        except FileNotFoundError:
            raise FileNotFoundError(f"XML файл жанров не найден: {xml_path}")
        except ET.ParseError as e:
            raise ValueError(f"ошибка чтения XML: {e}")

    def load_users(self) -> None:
        json_path = self.data_dir / "users.json"
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            for email, user_data in data.items():
                self.users[email] = User(
                    email=email,
                    username=user_data['username'],
                    password_hash=user_data['password_hash'],
                    library_id=user_data['library_id']
                )
        except FileNotFoundError:
            # создаем пустой если что
            self.save_users()
        except json.JSONDecodeError as e:
            raise ValueError(f"Ошибка чтения JSON: {e}")

    def load_songs(self) -> None:
        json_path = self.data_dir / "songs.json"
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            for song_id, song_data in data.items():
                self.songs[song_id] = Song(
                    id=song_id,
                    title=song_data['title'],
                    artist=song_data['artist'],
                    album=song_data['album'],
                    genre=song_data['genre'],
                    duration=song_data['duration'],
                    filename=song_data['filename']
                )
        except FileNotFoundError:
            raise FileNotFoundError(f"JSON файл songs не найден: {json_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"ошибка чтения songs.JSON: {e}")

    def load_albums(self) -> None:
        """Load albums from JSON file"""
        json_path = self.data_dir / "albums.json"
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            for album_id, album_data in data.items():
                self.albums[album_id] = Album(
                    id=album_id,
                    title=album_data['title'],
                    artist=album_data['artist'],
                    cover=album_data['cover'],
                    songs=album_data['songs'],
                    release_date=album_data['release_date']
                )
        except FileNotFoundError:
            raise FileNotFoundError(f"Albums.json не найден: {json_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"ошибка чтения albums.json: {e}")

    def load_playlists(self) -> None:
        json_path = self.data_dir / "playlists.json"
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            for playlist_id, playlist_data in data.items():
                self.playlists[playlist_id] = Playlist(
                    id=playlist_id,
                    title=playlist_data['title'],
                    description=playlist_data['description'],
                    author=playlist_data['author'],
                    songs=playlist_data['songs']
                )
        except FileNotFoundError:
            self.save_playlists()
        except json.JSONDecodeError as e:
            raise ValueError(f"ошибка чтения playlists.json: {e}")

    def load_libraries(self) -> None:
        json_path = self.data_dir / "libraries.json"
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            for library_id, library_data in data.items():
                self.libraries[library_id] = Library(
                    id=library_id,
                    songs=library_data['songs'],
                    albums=library_data['albums'],
                    playlists=library_data['playlists']
                )
        except FileNotFoundError:
            self.save_libraries()
        except json.JSONDecodeError as e:
            raise ValueError(f"ошибка чтения libraries.json: {e}")

    def extract_artists(self) -> None:
        """получить ВСЕХ исполнителей из songs"""
        artist_names = set()
        for song in self.songs.values():
            artist_names.add(song.artist)
        for album in self.albums.values():
            artist_names.add(album.artist)

        for name in artist_names:
            self.artists[name] = Artist(name=name)

    def save_users(self) -> None:
        """сохранить users в JSON"""
        json_path = self.data_dir / "users.json"
        data = {}
        for email, user in self.users.items():
            data[email] = {
                'username': user.username,
                'password_hash': user.password_hash,
                'library_id': user.library_id
            }

        try:
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except IOError as e:
            raise IOError(f"ошибка сохранения users: {e}")

    def save_playlists(self) -> None:
        """сохранить playlists в JSON"""
        json_path = self.data_dir / "playlists.json"
        data = {}
        for playlist_id, playlist in self.playlists.items():
            data[playlist_id] = {
                'title': playlist.title,
                'description': playlist.description,
                'author': playlist.author,
                'songs': playlist.songs
            }

        try:
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except IOError as e:
            raise IOError(f"ошибка сохранения playlists: {e}")

    def save_libraries(self) -> None:
        """сохраниьт libraries в JSON"""
        json_path = self.data_dir / "libraries.json"
        data = {}
        for library_id, library in self.libraries.items():
            data[library_id] = {
                'songs': library.songs,
                'albums': library.albums,
                'playlists': library.playlists
            }

        try:
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except IOError as e:
            raise IOError(f"ошибка сохранения libraries: {e}")

    def get_user(self, email: str) -> Optional[User]:
        """получить пользователя по почте))"""
        return self.users.get(email)

    def get_song(self, song_id: str) -> Optional[Song]:
        return self.songs.get(song_id)

    def get_album(self, album_id: str) -> Optional[Album]:
        return self.albums.get(album_id)

    def get_genre(self, genre_id: str) -> Optional[Genre]:
        return self.genres.get(genre_id)

    def get_playlist(self, playlist_id: str) -> Optional[Playlist]:
        return self.playlists.get(playlist_id)

    def get_library(self, library_id: str) -> Optional[Library]:
        return self.libraries.get(library_id)

    def add_user(self, user: User) -> None:
        self.users[user.email] = user
        self.save_users()

    def delete_user(self, email: str) -> None:
        if email in self.users:
            del self.users[email]
            self.save_users()

    def add_playlist(self, playlist: Playlist) -> None:
        self.playlists[playlist.id] = playlist
        self.save_playlists()

    def update_playlist(self, playlist: Playlist) -> None:
        self.playlists[playlist.id] = playlist
        self.save_playlists()

    def delete_playlist(self, playlist_id: str) -> None:
        if playlist_id in self.playlists:
            del self.playlists[playlist_id]
            self.save_playlists()

    def update_library(self, library: Library) -> None:
        self.libraries[library.id] = library
        self.save_libraries()

    def get_all_songs(self) -> List[Song]:
        return list(self.songs.values())

    def get_all_albums(self) -> List[Album]:
        return list(self.albums.values())

    def get_all_artists(self) -> List[Artist]:
        return list(self.artists.values())

    def get_all_genres(self) -> List[Genre]:
        return list(self.genres.values())

    def get_all_playlists(self) -> List[Playlist]:
        return list(self.playlists.values())
