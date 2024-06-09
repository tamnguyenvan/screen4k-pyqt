import sys
from PySide6.QtWidgets import QApplication

from views.startup import StartupWindow
from views.studio import Studio
from model import Model


if __name__ == "__main__":
    app = QApplication(sys.argv)

    model = Model()
    app.model = model

    # window = StartupWindow()
    window = Studio()
    window.show()

    sys.exit(app.exec())



# import sys
# import cv2
# from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QSlider, QLabel
# from PySide6.QtCore import Qt, QTimer, QSize
# from PySide6.QtGui import QPixmap, QImage

# class VideoPlayer(QMainWindow):
#     def __init__(self):
#         super().__init__()

#         self.setWindowTitle("Video Player with Red Rectangle")
#         self.setGeometry(100, 100, 800, 600)

#         # Main widget and layout
#         main_widget = QWidget()
#         main_layout = QVBoxLayout()
#         main_widget.setLayout(main_layout)

#         # Create video display label
#         self.video_label = QLabel()
#         self.video_label.setFixedSize(800, 450)
#         main_layout.addWidget(self.video_label)

#         # Create control buttons
#         control_layout = QHBoxLayout()

#         self.play_button = QPushButton("Play")
#         self.pause_button = QPushButton("Pause")
#         self.previous_button = QPushButton("Previous")
#         self.next_button = QPushButton("Next")

#         control_layout.addWidget(self.previous_button)
#         control_layout.addWidget(self.play_button)
#         control_layout.addWidget(self.pause_button)
#         control_layout.addWidget(self.next_button)

#         # Create slider and label
#         self.slider = QSlider(Qt.Orientation.Horizontal)
#         self.slider.setRange(0, 100)
#         self.slider.sliderMoved.connect(self.set_position)

#         self.label_duration = QLabel("00:00 / 00:00")
#         self.label_duration.setAlignment(Qt.AlignmentFlag.AlignCenter)

#         # Add widgets to the main layout
#         main_layout.addLayout(control_layout)
#         main_layout.addWidget(self.slider)
#         main_layout.addWidget(self.label_duration)

#         # Set main widget
#         self.setCentralWidget(main_widget)

#         # Connect buttons to methods
#         self.play_button.clicked.connect(self.play)
#         self.pause_button.clicked.connect(self.pause)
#         self.previous_button.clicked.connect(self.previous_frame)
#         self.next_button.clicked.connect(self.next_frame)

#         # Video capture and timer
#         self.cap = cv2.VideoCapture("/home/tamnv/Downloads/19 phone 768x432.MP4")
#         self.timer = QTimer()
#         self.timer.timeout.connect(self.next_frame)

#         self.is_paused = True

#         # Update duration label and slider range
#         self.update_duration_label()
#         self.slider.setRange(0, int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT)))

#     def play(self):
#         self.is_paused = False
#         self.timer.start(30)  # Adjust the interval as needed

#     def pause(self):
#         self.is_paused = True
#         self.timer.stop()

#     def previous_frame(self):
#         self.cap.set(cv2.CAP_PROP_POS_FRAMES, max(0, self.cap.get(cv2.CAP_PROP_POS_FRAMES) - 2))
#         self.next_frame()

#     def next_frame(self):
#         if self.is_paused:
#             return

#         ret, frame = self.cap.read()
#         if ret:
#             # Draw red rectangle on the frame
#             cv2.rectangle(frame, (100, 100), (200, 200), (0, 0, 255), 2)  # Red rectangle

#             # Convert frame to QImage
#             frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#             height, width, channel = frame_rgb.shape
#             bytes_per_line = 3 * width
#             q_img = QImage(frame_rgb.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)

#             # Display QImage in the QLabel
#             self.video_label.setPixmap(QPixmap.fromImage(q_img))

#             # Update slider and duration label
#             self.slider.setValue(int(self.cap.get(cv2.CAP_PROP_POS_FRAMES)))
#             self.update_duration_label()

#     def set_position(self, position):
#         self.cap.set(cv2.CAP_PROP_POS_FRAMES, position)
#         self.next_frame()

#     def update_duration_label(self):
#         position = self.cap.get(cv2.CAP_PROP_POS_FRAMES)
#         duration = self.cap.get(cv2.CAP_PROP_FRAME_COUNT)
#         self.label_duration.setText(f"{self.format_time(position)} / {self.format_time(duration)}")

#     @staticmethod
#     def format_time(frame_count, fps=30):
#         total_seconds = frame_count / fps
#         minutes = int(total_seconds // 60)
#         seconds = int(total_seconds % 60)
#         return f"{minutes:02}:{seconds:02}"

#     def closeEvent(self, event):
#         self.cap.release()
#         event.accept()

# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     window = VideoPlayer()
#     window.show()
#     sys.exit(app.exec())
