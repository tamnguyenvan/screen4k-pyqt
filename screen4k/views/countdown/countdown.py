from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QSystemTrayIcon, QMenu
from PySide6.QtGui import QPainter, QColor, QPen, QFont, QIcon
from PySide6.QtCore import Qt, QRect, QTimer

from model.recorder import ScreenRecorder
from views.studio import Studio
from utils.context import AppContext
from utils.image import ImageAssets
from utils.general import generate_video_path


class Countdown(QWidget):
    def __init__(self, countdown_time=3):
        super().__init__()

        # Remove window decorations and enable transparent background
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Set window size and title
        self.setFixedSize(500, 500)

        # Main layout
        self.main_layout = QVBoxLayout()
        self.main_layout.setAlignment(Qt.AlignCenter)
        self.setLayout(self.main_layout)

        # Countdown label
        self.countdown_label = QLabel()
        self.countdown_label.setFont(QFont('Arial', 80, QFont.Bold))
        self.countdown_label.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(self.countdown_label)

        # Initialize countdown time
        self.countdown_time = countdown_time
        self.update_countdown()

        # Timer to update countdown
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_countdown)
        self.timer.start(1000)  # Update every second

        self.center_window()

        self.studio = None

    def paintEvent(self, event):
        # Draw circle border
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        brush = QColor(40, 40, 40, 255)  # Semi-transparent black background
        pen = QPen(QColor(255, 255, 255), 5)  # White border with width 5

        center = self.rect().center()
        radius = min(self.rect().width(), self.rect().height()) // 2 - pen.width()

        painter.setBrush(brush)
        painter.setPen(pen)
        painter.drawEllipse(center, radius, radius)

    def center_window(self):
        screen_geometry = QApplication.primaryScreen().availableGeometry()
        screen_width = screen_geometry.width()
        screen_height = screen_geometry.height()

        window_width = self.width()
        window_height = self.height()

        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2

        self.setGeometry(QRect(x, y, window_width, window_height))

    def update_countdown(self):
        if self.countdown_time <= 0:
            self.timer.stop()

            AppContext.get('model').start_recording()

            self.create_tray_icon()
            self.hide()

        time_format = f'{self.countdown_time}'
        self.countdown_label.setText(time_format)
        self.countdown_time -= 1

    def create_tray_icon(self):
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon(ImageAssets.file('images/ui_controls/record.png')))

        menu = QMenu()
        stop_action = menu.addAction('Stop')
        exit_action = menu.addAction('Cancel')

        stop_action.triggered.connect(self.show_studio)
        exit_action.triggered.connect(self.exit_application)

        self.tray_icon.setContextMenu(menu)
        self.tray_icon.show()

    def show_studio(self):
        # Stop recording
        AppContext.get('model').stop_recording()

        # Set up model

        # Show studio
        self.studio = Studio()
        self.studio.show()

        # Hide the tray icon
        self.tray_icon.hide()

    def exit_application(self):
        AppContext.get('model').cancel_recording()
        QApplication.quit()