from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QListWidget,
    QPushButton, QLabel, QListWidgetItem
)
from PySide6.QtCore import Qt

from music_service.queue_service import QueueService


class QueueWindow(QDialog):
    def __init__(self, queue_service: QueueService):
        super().__init__()
        self.queue_service = queue_service

        self.setWindowTitle("Queue")
        self.setMinimumSize(400, 500)

        layout = QVBoxLayout(self)

        # Title
        title = QLabel("Playback Queue")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Queue list
        self.queue_list = QListWidget()
        layout.addWidget(self.queue_list)

        # Buttons
        btn_layout = QHBoxLayout()

        self.remove_btn = QPushButton("Remove (−)")
        self.remove_btn.clicked.connect(self._on_remove)
        btn_layout.addWidget(self.remove_btn)

        self.up_btn = QPushButton("Move Up (⬆)")
        self.up_btn.clicked.connect(self._on_move_up)
        btn_layout.addWidget(self.up_btn)

        self.down_btn = QPushButton("Move Down (⬇)")
        self.down_btn.clicked.connect(self._on_move_down)
        btn_layout.addWidget(self.down_btn)

        layout.addLayout(btn_layout)

        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn, alignment=Qt.AlignCenter)

        # Load queue
        self._load_queue()

        # Connect signals
        self.queue_service.queue_changed.connect(self._load_queue)
        self.queue_service.current_changed.connect(self._on_current_changed)

    def _load_queue(self):
        """Load queue into list"""
        self.queue_list.clear()

        queue = self.queue_service.get_queue()
        current_index = self.queue_service.current_index

        for i, song in enumerate(queue):
            text = f"{song.artist} - {song.title}"
            if i == current_index:
                text = f"▶ {text}"

            item = QListWidgetItem(text)
            self.queue_list.addItem(item)

        if 0 <= current_index < self.queue_list.count():
            self.queue_list.setCurrentRow(current_index)

    def _on_current_changed(self, index: int):
        """Handle current song changed"""
        self._load_queue()

    def _on_remove(self):
        """Remove selected song from queue"""
        current_row = self.queue_list.currentRow()
        if current_row >= 0:
            self.queue_service.dequeue(current_row)

    def _on_move_up(self):
        """Move selected song up"""
        current_row = self.queue_list.currentRow()
        if current_row > 0:
            self.queue_service.move_up(current_row)
            self.queue_list.setCurrentRow(current_row - 1)

    def _on_move_down(self):
        """Move selected song down"""
        current_row = self.queue_list.currentRow()
        if current_row >= 0 and current_row < self.queue_list.count() - 1:
            self.queue_service.move_down(current_row)
            self.queue_list.setCurrentRow(current_row + 1)
