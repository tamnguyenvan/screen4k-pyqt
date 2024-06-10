from PySide6.QtWidgets import QWidget, QScrollArea
from PySide6.QtCore import Qt, QEvent


class CustomScrollArea(QScrollArea):
    def __init__(self):
        super().__init__()

        self.customize_scroll_bars()
        self.verticalScrollBar().installEventFilter(self)
        self.horizontalScrollBar().installEventFilter(self)

    def customize_scroll_bars(self):
        self.verticalScrollBar().setStyleSheet("""
            QScrollBar:vertical {
                background: #242424;
                border: none;
                width: 8px;
                margin: 0px 0px 0px 0px;
            }
            QScrollBar::handle:vertical {
                background: #666;
                min-height: 20px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical:hover {
                background: #555;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
            }
        """)
        self.horizontalScrollBar().setStyleSheet("""
            QScrollBar:horizontal {
                background: #242424;
                border: none;
                height: 8px;
                margin: 0px 0px 0px 0px;
            }
            QScrollBar::handle:horizontal {
                background: #666;
                min-width: 20px;
                border-radius: 4px;
            }
            QScrollBar::handle:horizontal:hover {
                background: #555;
            }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                border: none;
                background: none;
            }
        """)

    def eventFilter(self, source, event):
        if source == self:
            if event.type() == QEvent.Enter:
                self.showScrollBars()
            elif event.type() == QEvent.Leave:
                self.hideScrollBars()
        return super().eventFilter(source, event)

    def showScrollBars(self):
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)

    def hideScrollBars(self):
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)