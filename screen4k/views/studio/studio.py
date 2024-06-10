from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QSizePolicy
)
from PySide6.QtCore import Qt, QRect
from PySide6.QtGui import QColor, QPainter, QPixmap

from views.widgets.custom_scrollarea import CustomScrollArea
from views.studio.video_preview import VideoPreview
from views.studio.sidebar import SideBar
from views.studio.video_edit import VideoEdit
from utils.context import AppContext


class Studio(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setWindowTitle("Screen4k Studio")
        self.setGeometry(0, 0, 1200, 800)
        self.center_window()
        self.setMinimumSize(900, 600)
        self.showMaximized()

        # Set background color
        self.setStyleSheet("background-color: #242424;")

        pix_per_sec = 200
        AppContext.set('pix_per_sec', pix_per_sec)

        # Main layout
        margin = 10
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(margin, margin, margin, margin)

        # Top toolbar
        top_toolbar_layout = QHBoxLayout()
        top_toolbar_layout.setContentsMargins(0, 0, 0, 0)
        top_toolbar_layout.setSpacing(0)

        top_toolbar_widget = QWidget()
        top_toolbar_widget.setFixedHeight(50)
        top_toolbar_widget.setLayout(top_toolbar_layout)

        export_button = QPushButton('Export', self)
        top_toolbar_layout.addStretch()
        top_toolbar_layout.addWidget(export_button)

        main_layout.addWidget(top_toolbar_widget)

        # Video preview and sidebar
        center_layout = QHBoxLayout()
        center_layout.setContentsMargins(0, 0, 0, 0)
        center_layout.setSpacing(0)

        # Video preview (left side)
        video_preview = VideoPreview()
        video_preview.setMinimumWidth(500)
        center_layout.addWidget(video_preview)

        # Sidebar (right side)
        sidebar = SideBar()
        sidebar.setFixedWidth(400)
        center_layout.addWidget(sidebar)

        main_layout.addLayout(center_layout)

        # Video edit area with horizontal scroll
        video_edit_scroll_area = CustomScrollArea()
        video_edit_scroll_area.setWidgetResizable(True)
        video_edit_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        video_edit_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        video_edit_widget = VideoEdit()

        video_edit_scroll_area.setWidget(video_edit_widget)
        video_edit_scroll_area.setFixedHeight(230)

        main_layout.addWidget(video_edit_scroll_area)

        self.setLayout(main_layout)

    def center_window(self):
        screen_geometry = QApplication.primaryScreen().availableGeometry()
        screen_width = screen_geometry.width()
        screen_height = screen_geometry.height()

        window_width = self.width()
        window_height = self.height()

        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2

        self.setGeometry(QRect(x, y, window_width, window_height))

    def closeEvent(self, event):
        QApplication.quit()