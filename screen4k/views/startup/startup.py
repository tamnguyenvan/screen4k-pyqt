from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
)
from PySide6.QtCore import Qt, QRect
from PySide6.QtGui import QPainter, QBrush, QPen, QColor

from views.widgets.custom_button import RecordingModeButton, RecordButton
from views.countdown import Countdown


class StartupWindow(QWidget):
    def __init__(self):
        super().__init__()

        # Remove window decorations and enable transparent background
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Set up the UI
        self.setFixedSize(300, 200)
        self.setWindowTitle('Frameless Window')

        # Main layout
        main_layout = QVBoxLayout()

        # First row with three square buttons
        row1_layout = QHBoxLayout()

        custom_button = RecordingModeButton(
           icon_path='images/ui_controls/custom.svg',
           text='Custom'
        )
        custom_button.setFixedSize(80, 80)
        row1_layout.addWidget(custom_button)

        screen_button = RecordingModeButton(
            icon_path='images/ui_controls/screen.svg',
            text='Screen'
        )
        screen_button.setFixedSize(80, 80)
        row1_layout.addWidget(screen_button)

        window_button = RecordingModeButton(
            icon_path='images/ui_controls/window.svg',
            text='Window'
        )
        window_button.setFixedSize(80, 80)
        row1_layout.addWidget(window_button)

        main_layout.addLayout(row1_layout)

        # Second row with one centered button
        row2_layout = QHBoxLayout()
        self.record_button = RecordButton()
        row2_layout.addStretch()
        row2_layout.addWidget(self.record_button)
        row2_layout.addStretch()

        main_layout.addLayout(row2_layout)

        self.setLayout(main_layout)

        self.record_button.clicked.connect(self.on_record_click)

        self.center_window()

        # Countdown
        self.countdown_window = None

    def paintEvent(self, event):
        # Draw rounded borders
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        brush = QBrush(QColor(28, 28, 28))
        pen = QPen(Qt.NoPen)

        rect = self.rect()
        rounded_rect = QRect(rect.left() + 10, rect.top() + 10, rect.width() - 20, rect.height() - 20)

        painter.setBrush(brush)
        painter.setPen(pen)
        painter.drawRoundedRect(rounded_rect, 20, 20)

    def center_window(self):
        screen_geometry = QApplication.primaryScreen().availableGeometry()
        screen_width = screen_geometry.width()
        screen_height = screen_geometry.height()

        window_width = self.width()
        window_height = self.height()

        x = (screen_width - window_width) // 2
        y = screen_height - window_height - 10

        self.setGeometry(QRect(x, y, window_width, window_height))

    def on_record_click(self):
        self.hide()

        self.countdown_window = Countdown()
        self.countdown_window.show()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()
