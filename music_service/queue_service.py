from typing import List, Optional
import random

from PySide6.QtCore import QObject, Signal

from models import Song


class RepeatMode:
    """варианты повторения """
    OFF = 0
    ONE = 1
    ALL = 2


class QueueService(QObject):
    """сервис для управления очередью воспроизведения"""

    # Signals
    queue_changed = Signal()
    current_changed = Signal(int)  # new index

    def __init__(self):
        super().__init__()
        self.queue: List[Song] = []
        self.original_queue: List[Song] = []  # for shuffle
        self.current_index: int = -1
        self.shuffle_enabled: bool = False
        self.repeat_mode: int = RepeatMode.OFF

    def clear(self) -> None:
        self.queue = []
        self.original_queue = []
        self.current_index = -1
        self.queue_changed.emit()

    def set_queue(self, songs: List[Song], start_index: int = 0) -> None:
        self.queue = songs.copy()
        self.original_queue = songs.copy()
        self.current_index = start_index

        if self.shuffle_enabled:
            self._apply_shuffle()

        self.queue_changed.emit()
        self.current_changed.emit(self.current_index)

    def enqueue(self, song: Song, pos: Optional[int] = None) -> None:
        # добавить песню в очередь
        if pos is None:
            self.queue.append(song)
            self.original_queue.append(song)
        else:
            self.queue.insert(pos, song)
            self.original_queue.insert(pos, song)

        self.queue_changed.emit()

    def enqueue_after_current(self, song: Song) -> None:
        # play next
        if self.current_index >= 0:
            self.enqueue(song, self.current_index + 1)
        else:
            self.enqueue(song, 0)

    def dequeue(self, index: int) -> None:
        # удалить песню из очереди
        if 0 <= index < len(self.queue):
            removed_song = self.queue.pop(index)

            # удаляем из исходной очереди
            if removed_song in self.original_queue:
                self.original_queue.remove(removed_song)

            # обновляем индекс
            if index < self.current_index:
                self.current_index -= 1
            elif index == self.current_index:
                # если удалили текущую песню
                if self.current_index >= len(self.queue):
                    self.current_index = len(self.queue) - 1

            self.queue_changed.emit()
            self.current_changed.emit(self.current_index)

    def move_up(self, index: int) -> None:
        if 1 <= index < len(self.queue):
            self.queue[index], self.queue[index - 1] = self.queue[index - 1], self.queue[index]

            if index == self.current_index:
                self.current_index -= 1
            elif index - 1 == self.current_index:
                self.current_index += 1

            self.queue_changed.emit()
            self.current_changed.emit(self.current_index)

    def move_down(self, index: int) -> None:
        if 0 <= index < len(self.queue) - 1:
            self.queue[index], self.queue[index + 1] = self.queue[index + 1], self.queue[index]

            if index == self.current_index:
                self.current_index += 1
            elif index + 1 == self.current_index:
                self.current_index -= 1

            self.queue_changed.emit()
            self.current_changed.emit(self.current_index)

    def next(self) -> Optional[Song]:
        if not self.queue:
            return None

        if self.repeat_mode == RepeatMode.ONE:
            return self.current_song()

        self.current_index += 1

        if self.current_index >= len(self.queue):
            if self.repeat_mode == RepeatMode.ALL:
                # на начало
                self.current_index = 0
            else:
                # не повторять, начать сначала, но не воспроизводить
                self.current_index = 0
                self.current_changed.emit(self.current_index)
                return None

        self.current_changed.emit(self.current_index)
        return self.current_song()

    def previous(self) -> Optional[Song]:
        if not self.queue:
            return None

        self.current_index -= 1

        if self.current_index < 0:
            self.current_index = len(self.queue) - 1

        self.current_changed.emit(self.current_index)
        return self.current_song()

    def current_song(self) -> Optional[Song]:
        if 0 <= self.current_index < len(self.queue):
            return self.queue[self.current_index]
        return None

    def toggle_shuffle(self) -> None:
        # переключение перемешивания
        self.shuffle_enabled = not self.shuffle_enabled

        if self.shuffle_enabled:
            self._apply_shuffle()
        else:
            self._remove_shuffle()

        self.queue_changed.emit()

    def cycle_repeat_mode(self) -> None:
        # переключение повтора
        self.repeat_mode = (self.repeat_mode + 1) % 3

    def _apply_shuffle(self) -> None:
        if not self.queue:
            return

        # сохраняем текущую
        current_song = self.current_song()

        # перемешкиваем всё кроме текущей
        songs_to_shuffle = self.queue.copy()
        if current_song:
            songs_to_shuffle.remove(current_song)

        random.shuffle(songs_to_shuffle)

        # обновляем, текущая 1
        if current_song:
            self.queue = [current_song] + songs_to_shuffle
            self.current_index = 0
        else:
            self.queue = songs_to_shuffle

    def _remove_shuffle(self) -> None:
        if not self.queue:
            return

        current_song = self.current_song()

        # востанавливаем исходную очередь
        self.queue = self.original_queue.copy()

        # находим текущий трек в исходной
        if current_song and current_song in self.queue:
            self.current_index = self.queue.index(current_song)
        else:
            self.current_index = 0

    def get_queue(self) -> List[Song]:
        return self.queue.copy()
