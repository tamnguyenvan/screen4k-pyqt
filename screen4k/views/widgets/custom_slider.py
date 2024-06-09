from PySide6.QtCore import Qt
from PySide6.QtWidgets import QSlider
from PySide6.QtGui import QWheelEvent


class CustomSlider(QSlider):
    def __init__(
        self,
        orientation=Qt.Orientation.Horizontal,
        color='#4229f1',
        parent=None
    ):
        super().__init__(orientation, parent)

        self.color = color

        self.init_ui()

        self.setMinimumHeight(50)

    def init_ui(self):
        self.setStyleSheet(f"""
            QSlider::groove:horizontal {{
                border: 1px solid #4d5057;
                height: 4px;
                background: #4d5057;
                border-radius: 2px;
                margin: 0 13px;
            }}

            QSlider::sub-page:horizontal {{
                background: {self.color};
                border: 1px solid {self.color};
                height: 4px;
                border-radius: 2px;
                margin: 0 13px;
            }}

            QSlider::handle:horizontal {{
                background: {self.color};
                border: 1px solid {self.color};
                width: 26px;
                height: 26px;
                margin: -11px 0;
                border-radius: 13px;
            }}

            QSlider::handle:horizontal:pressed {{
                background: {self.color};
            }}
        """)

    def wheelEvent(self, event: QWheelEvent):
        event.ignore()