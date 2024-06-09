import time
import math
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QFrame
from PySide6.QtGui import QColor, QPainter, QPixmap, QMouseEvent
from PySide6.QtCore import Qt, QSize, QPoint, Signal

from utils.context import AppContext
from utils.image import ImageAssets


class VideoEdit(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        model = AppContext.get('model')
        self.duration = model.duration

        self.init_ui()

    def init_ui(self):
        duration_int = math.ceil(self.duration)
        pix_per_sec = AppContext.get('pix_per_sec')

        self.timeline = Timeline(duration=duration_int, item_width=pix_per_sec, parent=self)
        self.clip_track = ClipTrack(duration=self.duration, parent=self)

        zoom_data = [1]
        self.zoom_tracks = []
        for item in zoom_data:
            zoom_track = ZoomTrack(duration=3, parent=self)
            zoom_track.setFixedSize(3 * pix_per_sec, 60)
            zoom_track.move(0, 150)
            self.zoom_tracks.append(zoom_track)

        self.timeline_slider = TimelineSlider(parent=self)
        AppContext.set('timeline_slider', self.timeline_slider)

        clip_track_width = int(self.duration * pix_per_sec)
        self.clip_track.setFixedSize(clip_track_width, 60)

        self.timeline.move(0, 0)
        self.clip_track.move(0, 80)
        self.timeline_slider.move(0, 0)

        self.dragging = False
        self.offset = QPoint()

        # Connect Timeline's custom signal to TimelineSlider's slot
        self.timeline.timeline_clicked.connect(self.move_timeline_slider)

        # Connect ClipTrack's custom signal to TimelineSlider's slot
        self.clip_track.clip_clicked.connect(self.move_timeline_slider)

        self.setFixedWidth(duration_int * pix_per_sec + 100)

    def move_timeline_slider(self, x_pos):
        width = self.timeline_slider.width()
        self.timeline_slider.move(x_pos - width // 2, self.timeline_slider.y())


class Timeline(QWidget):
    # Custom signal to emit mouse press event
    timeline_clicked = Signal(int)

    def __init__(self, duration, item_width=200, parent=None):
        super().__init__(parent=parent)

        self.duration = duration
        self.item_width = item_width
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout()
        for i in range(self.duration + 1):
            time_frame_widget = self.create_time_frame(i)
            layout.addWidget(time_frame_widget)

        self.setLayout(layout)

    def create_time_frame(self, timestamp):
        frame = QWidget()
        frame.setFixedWidth(self.item_width)

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        time_layout = QVBoxLayout()
        time_layout.setContentsMargins(0, 0, 0, 0)
        time_layout.setSpacing(0)

        time_layout.addStretch(1)
        time_layout.addWidget(QLabel(f'{timestamp}s'))
        time_layout.addWidget(QLabel('.'))
        time_layout.addStretch(1)
        layout.addLayout(time_layout)

        frame.setLayout(layout)
        return frame

    def mousePressEvent(self, event: QMouseEvent):
        if event.buttons() & Qt.LeftButton:
            self.timeline_clicked.emit(event.pos().x())


class TimelineSlider(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.init_ui()

        self.dragging = False
        self.offset = QPoint()

    def init_ui(self):
        width = 16
        height = 250
        self.setFixedSize(width, height)

        top_label = QLabel(self)
        top_label.setFixedSize(width, width)
        top_label.setStyleSheet('border-radius: 8px; background-color: #4229F0;')
        top_label.move(0, 0)

        vertical_bar_width = 2
        vertical_bar = QLabel(self)
        vertical_bar.setFixedSize(vertical_bar_width, height)
        vertical_bar.move((width - vertical_bar_width) // 2, 0)
        vertical_bar.setStyleSheet('background-color: #4229F0;')

    def mousePressEvent(self, event: QMouseEvent):
        if event.buttons() & Qt.LeftButton:
            self.dragging = True
            self.offset = event.pos()

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.dragging:
            new_x = self.mapToParent(event.pos()).x() - self.width() / 2
            if new_x < 0:
                new_x = 0
            elif new_x > self.parent().width() - self.width():
                new_x = self.parent().width() - self.width()
            self.move(new_x, self.y())

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.dragging = False


class ClipTrack(QWidget):
    # Custom signal to emit mouse press event
    clip_clicked = Signal(int)

    def __init__(self, duration, parent=None):
        super().__init__(parent=parent)

        self.duration = duration

        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        track_widget = QFrame()
        track_widget.setStyleSheet('background-color: #865A0E; border-radius: 10px;')

        track_widget_layout = QHBoxLayout(self)
        track_widget_layout.setContentsMargins(0, 0, 0, 0)

        # Left strip
        left_strip = QFrame()
        left_strip.setFixedWidth(10)
        left_strip.setStyleSheet("background-color: #b37606; border-top-left-radius: 10px;")
        track_widget_layout.addWidget(left_strip)

        # Center
        center_layout = QVBoxLayout()
        center_layout.setAlignment(Qt.AlignCenter)

        # 1st row
        top_row = QHBoxLayout()
        top_row.setContentsMargins(0, 0, 0, 0)
        top_row.setSpacing(4)

        clip_label = QLabel()
        clip_image_path = ImageAssets.file('images/ui_controls/clip.svg')
        clip_image = QPixmap(clip_image_path)
        clip_label.setPixmap(clip_image)
        top_row.addStretch(1)
        top_row.addWidget(clip_label)

        top_row.addWidget(QLabel('Clip'))
        top_row.addStretch(1)

        # 2nd row
        bottom_row = QHBoxLayout()
        bottom_row.setContentsMargins(0, 0, 0, 0)
        bottom_row.setSpacing(4)

        bottom_row.addStretch(1)

        duration_label = f'{self.duration:.1f}s'
        bottom_row.addWidget(QLabel(duration_label))

        mouse_image = QPixmap(ImageAssets.file('images/ui_controls/clock.svg'))

        mouse_label = QLabel()
        mouse_label.setPixmap(mouse_image)
        bottom_row.addWidget(mouse_label)

        bottom_row.addWidget(QLabel('2x'))

        bottom_row.addStretch(1)

        center_layout.addLayout(top_row)
        center_layout.addLayout(bottom_row)

        track_widget_layout.addLayout(center_layout)

        # Right strip
        right_strip = QLabel()
        right_strip.setFixedWidth(10)
        right_strip.setStyleSheet("background-color: #b37606; border-top-right-radius: 10px;")
        track_widget_layout.addWidget(right_strip)

        track_widget.setLayout(track_widget_layout)

        main_layout.addWidget(track_widget)
        self.setLayout(main_layout)

    def mousePressEvent(self, event: QMouseEvent):
        if event.buttons() & Qt.LeftButton:
            self.clip_clicked.emit(event.pos().x())


class ZoomTrack(QWidget):
    def __init__(self, duration, parent=None):
        super().__init__(parent=parent)

        self.duration = duration

        self.init_ui()

        self.dragging = False
        self.offset = QPoint()

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        track_widget = QFrame()
        track_widget.setStyleSheet('background-color: #4229F0; border-radius: 10px;')

        track_widget_layout = QHBoxLayout(self)
        track_widget_layout.setContentsMargins(0, 0, 0, 0)

        # Left strip
        left_strip = QFrame()
        left_strip.setFixedWidth(10)
        left_strip.setStyleSheet("background-color: #6049F5; border-top-left-radius: 10px;")
        track_widget_layout.addWidget(left_strip)

        # Center
        center_layout = QVBoxLayout()
        center_layout.setAlignment(Qt.AlignCenter)

        # 1st row
        top_row = QHBoxLayout()
        top_row.setContentsMargins(0, 0, 0, 0)
        top_row.setSpacing(4)

        clip_label = QLabel()
        clip_image_path = ImageAssets.file('images/ui_controls/cursor.svg')
        clip_image = QPixmap(clip_image_path)
        clip_label.setPixmap(clip_image)
        top_row.addStretch(1)
        top_row.addWidget(clip_label)

        top_row.addWidget(QLabel('Zoom'))
        top_row.addStretch(1)

        # 2nd row
        bottom_row = QHBoxLayout()
        bottom_row.setContentsMargins(0, 0, 0, 0)
        bottom_row.setSpacing(4)

        bottom_row.addStretch(1)

        zoom_image = QPixmap(ImageAssets.file('images/ui_controls/zoom.svg'))
        zoom_label = QLabel()
        zoom_label.setPixmap(zoom_image)
        bottom_row.addWidget(zoom_label)

        bottom_row.addWidget(QLabel('2x'))

        mouse_image = QPixmap(ImageAssets.file('images/ui_controls/mouse.svg'))
        mouse_label = QLabel()
        mouse_label.setPixmap(mouse_image)
        bottom_row.addWidget(mouse_label)

        bottom_row.addWidget(QLabel('Auto'))
        bottom_row.addStretch(1)

        center_layout.addLayout(top_row)
        center_layout.addLayout(bottom_row)

        track_widget_layout.addLayout(center_layout)

        # Right strip
        right_strip = QLabel()
        right_strip.setFixedWidth(10)
        right_strip.setStyleSheet("background-color: #6049F5; border-top-right-radius: 10px;")
        track_widget_layout.addWidget(right_strip)

        track_widget.setLayout(track_widget_layout)

        main_layout.addWidget(track_widget)
        self.setLayout(main_layout)

    def mousePressEvent(self, event: QMouseEvent):
        if event.buttons() & Qt.LeftButton:
            self.dragging = True
            self.offset = event.pos()

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.dragging:
            new_x = self.mapToParent(event.pos()).x() - self.width() / 2
            if new_x < 0:
                new_x = 0
            elif new_x > self.parent().width() - self.width():
                new_x = self.parent().width() - self.width()
            self.move(new_x, self.y())

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.dragging = False