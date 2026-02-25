from typing import List

from models import Song
from music_service.database import Database


class SearchService:
    """поисковый сервис"""

    def __init__(self, database: Database):
        self.database = database

    def search_songs(self, query: str) -> List[Song]:
        # поиск по названию и исполнителю
        if not query.strip():
            return []

        query_lower = query.lower()
        results = []

        for song in self.database.get_all_songs():
            if (query_lower in song.title.lower() or
                query_lower in song.artist.lower()):
                results.append(song)

        return results
