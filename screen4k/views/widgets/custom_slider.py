from PySide6.QtCore import Qt
from PySide6.QtWidgets import QSlider
from PySide6.QtGui import QWheelEvent


class CustomSlider(QSlider):
    def __init__(
        self,
        orientation=Qt.Orientation.Horizontal,
        color='white',
        handle_color='#363062',
        parent=None
    ):
        super().__init__(orientation, parent)

        self.color = color
        self.handle_color = handle_color

        self.init_ui()

        self.setMinimumHeight(50)

    def init_ui(self):
        self.setStyleSheet(f"""
            QSlider::groove:horizontal {{
                border: 1px solid #4d5057;
                height: 2px;
                background: #4d5057;
                border-radius: 2px;
            }}

            QSlider::sub-page:horizontal {{
                background: {self.handle_color};
                border: 1px solid {self.handle_color};
                height: 2px;
                border-radius: 2px;
            }}

            QSlider::handle:horizontal {{
                background: {self.color};
                border: 1px solid {self.color};
                width: 24px;
                height: 24px;
                margin: -12px 0;
                border-radius: 12px;
            }}

            QSlider::handle:horizontal:pressed {{
                background-color: white;
            }}
        """)

    def wheelEvent(self, event: QWheelEvent):
        event.ignore()