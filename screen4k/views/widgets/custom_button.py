from PySide6.QtWidgets import QWidget, QVBoxLayout, QStackedLayout, QPushButton, QLabel, QSizePolicy
from PySide6.QtCore import Qt, QRect, QSize
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtSvgWidgets import QSvgWidget

from utils.image import ImageAssets


class RecordingModeButton(QPushButton):
    def __init__(
        self,
        icon_path,
        text,
        icon_size=30,
        border_radius=20,
        bg_color="#1c1c1c",
        hover_color=("#242424", "#101010"),
        active_color="#151515",
        font_size=12,
        parent=None
    ):
        super().__init__(parent)
        self.icon_path = ImageAssets.file(icon_path)
        self.text = text
        self.icon_size = icon_size
        self.border_radius = border_radius
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.active_color = active_color
        self.font_size = font_size

        self.active = False

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        layout.addStretch()

        # SVG Icon
        self.icon_widget = QSvgWidget(self.icon_path)
        self.icon_widget.setFixedSize(self.icon_size, self.icon_size)
        layout.addWidget(self.icon_widget, alignment=Qt.AlignCenter)

        layout.addStretch()

        # Text Label
        self.label = QLabel(self.text)
        self.label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label, alignment=Qt.AlignCenter)

        self.setLayout(layout)
        self.setFixedSize(self.icon_size, self.icon_size + 20)  # Adjust size for icon and text

        self.update_stylesheet(self.bg_color)

        self.clicked.connect(self.on_click)

    def on_click(self):
        self.active = True
        self.update_stylesheet(self.active_color)

    def update_stylesheet(self, color):
        self.setStyleSheet(f"""
            RecordingModeButton {{
                border-radius: {self.border_radius}px;
                background-color: {color};
            }}
            QLabel {{
                font-size: {self.font_size}px;
            }}
        """)

    def set_icon_path(self, icon_path):
        self.icon_path = icon_path
        self.svg_widget.load(icon_path)

    def set_text(self, text):
        self.text = text
        self.label.setText(text)

    def set_icon_size(self, icon_size):
        self.icon_size = icon_size
        self.svg_widget.setFixedSize(icon_size, icon_size)
        self.setFixedSize(icon_size, icon_size + 20)

    def set_border_radius(self, border_radius):
        self.border_radius = border_radius

    def set_bg_color(self, bg_color):
        self.bg_color = bg_color
        self.update_stylesheet(bg_color)

    def set_hover_color(self, hover_color):
        self.hover_color = hover_color

    def set_active_color(self, active_color):
        self.active_color = active_color

    def enterEvent(self, event):
        if self.active:
            self.update_stylesheet(self.hover_color[0])
        else:
            self.update_stylesheet(self.hover_color[1])

    def leaveEvent(self, event):
        if self.active:
            self.update_stylesheet(self.active_color)
        else:
            self.update_stylesheet(self.bg_color)


class RecordButton(QPushButton):
    def __init__(self, size=(50, 50), parent=None):
        super().__init__(parent=parent)

        self.icon_size = size
        self.init_ui()

    def init_ui(self):
        # Set the fixed size of the button
        self.setFixedSize(QSize(*self.icon_size))

        # Apply the stylesheet to create a white circle
        self.setStyleSheet(f"""
            QPushButton {{
                border: none;
                border-radius: {self.icon_size[0] // 2}px;
                background-color: white;
            }}
        """)


class IconButton(QPushButton):
    def __init__(self, icon_path, icon_size=(24, 24)):
        super().__init__()

        # Set the icon for the button
        icon_path = ImageAssets.file(icon_path)
        self.setIcon(QIcon(icon_path))
        self.setIconSize(QSize(*icon_size))  # Set the size of the icon

        # Set the size policy to keep the button at its preferred size
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)

        self.update_stylesheet()

    def update_stylesheet(self):
        self.setStyleSheet("""
            IconButton {
                border: none;
                background-color: transparent;
            }
        """)