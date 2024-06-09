import time
from PySide6.QtWidgets import QLabel, QSizePolicy
from PySide6.QtGui import QPainter
from PySide6.QtCore import QRect


class AspectRatioLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.aspect_ratio = 1.0  # Default aspect ratio
        self.pixmap = None
        self.pixmap_rect = QRect()  # Store the pixmap rectangle

    def setPixmapWithAspectRatio(self, pixmap):
        self.aspect_ratio = pixmap.width() / pixmap.height()
        self.pixmap = pixmap
        self.update()  # Trigger a repaint

    def resizeEvent(self, event):
        self.updatePixmapRect()  # Update the pixmap rectangle on resize
        super().resizeEvent(event)

    def updatePixmapRect(self):
        # Calculate the dimensions of the scaled pixmap rectangle
        label_width = self.width()
        label_height = self.height()

        if label_width / self.aspect_ratio <= label_height:
            pixmap_width = label_width
            pixmap_height = int(label_width / self.aspect_ratio)
        else:
            pixmap_width = int(label_height * self.aspect_ratio)
            pixmap_height = label_height

        # Center the pixmap rectangle within the label
        pixmap_rect = QRect(0, 0, pixmap_width, pixmap_height)
        pixmap_rect.moveCenter(self.rect().center())
        self.pixmap_rect = pixmap_rect

    def paintEvent(self, event):
        if self.pixmap is None or self.pixmap.isNull():
            return

        # Update the pixmap rectangle if necessary
        if self.pixmap_rect.isNull() or self.pixmap_rect.size() != self.size():
            self.updatePixmapRect()

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw the scaled pixmap within the label
        painter.drawPixmap(self.pixmap_rect, self.pixmap)
        t1 = time.time()