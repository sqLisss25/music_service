import sys
from music_service import MusicService

if __name__ == "__main__":
    app = MusicService()
    sys.exit(app.run())