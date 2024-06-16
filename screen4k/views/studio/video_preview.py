import time
import cv2
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QSizePolicy
)
from PySide6.QtCore import Qt, QRect, QTimer, Signal
from PySide6.QtGui import QColor, QPainter, QPixmap, QIcon, QImage

from views.widgets.custom_button import IconButton
from views.widgets.custom_label import AspectRatioLabel
from views.widgets.custom_dropdown import DropDown
from utils.image import ImageAssets
from utils.context import AppContext


class VideoPreview(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.top_toolbar = VideoTopToolBar(parent=self)
        self.top_toolbar.setFixedHeight(40)

        self.frame_label = AspectRatioLabel(parent=self)
        self.frame_label.setAlignment(Qt.AlignCenter)

        self.toolbar = VideoToolBar(parent=self)
        self.toolbar.setFixedHeight(40)
        self.toolbar.frame_changed.connect(self.on_frame_changed)
        AppContext.set('video_toolbar', self.toolbar)

        layout.addWidget(self.top_toolbar)
        layout.addWidget(self.frame_label, 1)
        layout.addWidget(self.toolbar)

        self.setLayout(layout)

        self.toolbar.next_frame()

    def on_frame_changed(self, pixmap):
        self.frame_label.setPixmapWithAspectRatio(pixmap)


class VideoTopToolBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.setAlignment(Qt.AlignCenter)

        items = [
            'Auto',
            '16:9',
            '9:16',
            '4:3',
            '1:1',
            '3:4',
        ]
        self.drop_down = DropDown(items=items, parent=self)
        self.drop_down.clicked.connect(self.drop_down.show_menu)
        self.drop_down.value_changed.connect(self.change_aspect_ratio)

        layout.addWidget(self.drop_down)
        self.setLayout(layout)

    def change_aspect_ratio(self, aspect_ratio):
        model = AppContext.get('model')
        model.set_aspect_ratio(aspect_ratio)
        frame = model.current_frame

        AppContext.get('video_toolbar').display_frame(frame)


class VideoToolBar(QWidget):
    frame_changed = Signal(QPixmap)

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.timer = QTimer()
        self.timer.timeout.connect(self.next_frame)
        self.is_paused = True

        self.init_ui()

    def init_ui(self):
        # Create the main layout
        layout = QHBoxLayout()
        layout.setContentsMargins(50, 0, 50, 0)  # Set horizontal margins to 50
        layout.setSpacing(200)  # Set spacing between widgets to 50

        # Group 1: Three buttons
        group1_layout = QHBoxLayout()
        group1_layout.setContentsMargins(0, 0, 0, 0)
        group1_layout.setSpacing(20)

        group1_layout.addStretch(1)
        # button1 = IconButton('images/ui_controls/add.svg')
        # button2 = IconButton('images/ui_controls/add.svg')
        # button3 = IconButton('images/ui_controls/add.svg')

        # group1_layout.addWidget(button1)
        # group1_layout.addWidget(button2)
        # group1_layout.addWidget(button3)
        group1_layout.addWidget(QWidget())
        group1_layout.addStretch(1)

        # Group 2: Three buttons
        group2_layout = QHBoxLayout()
        group2_layout.setContentsMargins(0, 0, 0, 0)
        group2_layout.setSpacing(15)

        skip_backward_button = IconButton('images/ui_controls/prev.svg')
        self.play_button = IconButton('images/ui_controls/play.svg')
        skip_forward_button = IconButton('images/ui_controls/next.svg')
        skip_backward_button.clicked.connect(self.skip_backward)
        self.play_button.clicked.connect(self.toggle_play_pause)
        skip_forward_button.clicked.connect(self.skip_forward)

        group2_layout.addWidget(skip_backward_button)
        group2_layout.addWidget(self.play_button)
        group2_layout.addWidget(skip_forward_button)

        # Group 3: Three buttons
        group3_layout = QHBoxLayout()
        group3_layout.setContentsMargins(0, 0, 0, 0)
        group3_layout.setSpacing(15)

        button7 = IconButton('images/ui_controls/cut.svg')
        button8 = IconButton('images/ui_controls/scale.svg')

        group3_layout.addWidget(button7)
        group3_layout.addWidget(button8)

        # Add groups to the main layout
        layout.addStretch(1)
        layout.addLayout(group1_layout)
        layout.addLayout(group2_layout)
        layout.addLayout(group3_layout)
        layout.addStretch(1)

        # Set the layout for the widget
        self.setLayout(layout)

        # Set size policy to expand horizontally
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

    def toggle_play_pause(self):
        if self.is_paused:
            self.play()
        else:
            self.pause()

    def play(self):
        self.is_paused = False
        self.play_button.setIcon(QIcon(ImageAssets.file('images/ui_controls/pause.svg')))
        self.timer.start(30)

    def pause(self):
        self.is_paused = True
        self.play_button.setIcon(QIcon(ImageAssets.file('images/ui_controls/play.svg')))
        self.timer.stop()

    def skip_backward(self):
        self.pause()
        frame_index = AppContext.get('model').current_frame_index
        prev_frame_index = max(0, frame_index - 1)
        AppContext.get('model').current_frame_index = prev_frame_index
        self.next_frame()

    def skip_forward(self):
        self.pause()
        self.next_frame()

    def next_frame(self):
        frame = AppContext.get('model').next_frame()

        if frame is None:
            self.timer.stop()
            self.is_paused = True
            return

        self.display_frame(frame)

        # Update slider
        frame_index = AppContext.get('model').current_frame_index
        fps = AppContext.get('model').fps
        pix_per_sec = AppContext.get('pix_per_sec')

        x_pos = int(frame_index / fps * pix_per_sec)
        timeline_slider = AppContext.get('timeline_slider')
        if timeline_slider is not None:
            timeline_slider.move(x_pos, timeline_slider.y())

    def display_frame(self, frame):
        # Convert frame to QImage
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        height, width, channel = frame_rgb.shape
        bytes_per_line = 3 * width
        q_img = QImage(frame_rgb.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)

        self.frame_changed.emit(QPixmap.fromImage(q_img))