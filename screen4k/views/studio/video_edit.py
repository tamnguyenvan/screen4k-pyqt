import math

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QFrame, QMenu
from PySide6.QtGui import QColor, QPainter, QPixmap, QMouseEvent, QAction, QIcon, QCursor
from PySide6.QtCore import Qt, QSize, QPoint, Signal, QEvent

from utils.context import AppContext
from utils.image import ImageAssets


class VideoEdit(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        model = AppContext.get('model')
        pix_per_sec = AppContext.get('pix_per_sec')

        self.duration = model.duration
        self.clip_width = int(self.duration * pix_per_sec)

        self.init_ui()

    def init_ui(self):
        duration_int = math.ceil(self.duration)
        pix_per_sec = AppContext.get('pix_per_sec')

        # Initialize a timeline widget
        self.timeline = Timeline(duration=duration_int, item_width=pix_per_sec, parent=self)
        self.timeline.move(0, 0)

        # Initialize a clip track widget
        self.clip_track = ClipTrack(duration=self.duration, parent=self)
        self.clip_track.setFixedSize(self.clip_width, 60)
        self.clip_track.move(0, 80)

        # Initialize zoom track widgets
        click_data = AppContext.get('model').mouse_events['click']
        fps = AppContext.get('model').fps
        self.zoom_tracks = []

        for i, (rel_x, rel_y, clicked_frame_index, duration) in enumerate(click_data):
            if i == 0:
                drag_minimum_x = 0
            else:
                prev_clicked_frame_index = click_data[i - 1][2]
                prev_track_width = int(click_data[i - 1][3] * pix_per_sec)
                prev_x_pos = int(prev_clicked_frame_index / fps * pix_per_sec) + prev_track_width
                drag_minimum_x = prev_x_pos

            if i == len(click_data) - 1:
                drag_maximum_x = self.clip_width
            else:
                next_clicked_frame_index = click_data[i + 1][2]
                next_x_pos = int(next_clicked_frame_index / fps * pix_per_sec)
                drag_maximum_x = next_x_pos

            # Instaniate
            drag_range_x = [drag_minimum_x, drag_maximum_x]
            zoom_track = ZoomTrack(index=i, duration=duration, drag_range_x=drag_range_x, parent=self)

            # Set size
            zoom_track.setFixedSize(duration * pix_per_sec, 60)

            # Set position
            x_pos = int(clicked_frame_index / AppContext.get('model').fps * pix_per_sec)
            zoom_track.move(x_pos, 150)

            # Connect zoom track to signal
            zoom_track.mouse_released.connect(self.update_zoom_track_drag_range_x)
            zoom_track.delete_clicked.connect(self.update_zoom_track_after_delete)

            self.zoom_tracks.append(zoom_track)

        # Initialize a timeline slider widget
        self.timeline_slider = TimelineSlider(parent=self)
        self.timeline_slider.move(0, 0)

        # Set timeliner slider as a global property, so that we can access from other widgets
        AppContext.set('timeline_slider', self.timeline_slider)

        # Connect Timeline's custom signal to TimelineSlider's slot
        self.timeline.timeline_clicked.connect(self.move_timeline_slider_and_update_frame)

        # Connect TimelineSlider's custom signal to TimelineSlider's slot
        self.timeline_slider.timeline_slider_released.connect(self.move_timeline_slider_and_update_frame)

        # Connect ClipTrack's custom signal to TimelineSlider's slot
        self.clip_track.clip_clicked.connect(self.move_timeline_slider_and_update_frame)

        self.setFixedWidth(duration_int * pix_per_sec + 100)

    def move_timeline_slider_and_update_frame(self, x_pos):
        # Move timeline sider
        width = self.timeline_slider.width()
        cx = x_pos - width // 2
        self.timeline_slider.move(cx, self.timeline_slider.y())

        # Update frame
        frame_index = int(cx / AppContext.get('pix_per_sec') * AppContext.get('model').fps)
        frame = AppContext.get('model').get_frame(frame_index)
        AppContext.get('video_toolbar').display_frame(frame)

    def update_zoom_track_drag_range_x(self, index):
        # Update the internal data of the zoom tracks
        if index - 1 >= 0 and index - 1 < len(self.zoom_tracks):
            zoom_track = self.zoom_tracks[index]
            zoom_track_x = zoom_track.x()
            self.zoom_tracks[index - 1].drag_range_x[1] = zoom_track_x

        if index + 1 < len(self.zoom_tracks):
            zoom_track = self.zoom_tracks[index]
            zoom_track_x = zoom_track.x()
            zoom_track_width = zoom_track.width()
            self.zoom_tracks[index + 1].drag_range_x[0] = zoom_track_x + zoom_track_width

        # TODO: Update the underlying data

    def update_zoom_track_after_delete(self, index):
        num_tracks = len(self.zoom_tracks)

        # Update the internal data of the zoom tracks
        if index - 1 >= 0 and index - 1 < num_tracks:
            prev_zoom_track = self.zoom_tracks[index - 1]

            if index + 1 < num_tracks:
                drag_maximum_x = self.zoom_tracks[index + 1].x()
            else:
                drag_maximum_x = self.clip_width

            prev_zoom_track.drag_range_x[1] = drag_maximum_x

        if index + 1 < num_tracks:
            next_zoom_track = self.zoom_tracks[index + 1]

            if index - 1 >= 0:
                drag_minimum_x = self.zoom_tracks[index - 1].x() + self.zoom_tracks[index - 1].width()
            else:
                drag_minimum_x = 0

            next_zoom_track.drag_range_x[0] = drag_minimum_x
            for i in range(index + 1, num_tracks):
                self.zoom_tracks[i].index = i - 1

        # Update the UI
        self.zoom_tracks[index].deleteLater()
        del self.zoom_tracks[index]

        # Update the underlying data
        AppContext.get('model').delete_click_event(index)


class Timeline(QWidget):
    # Custom signal to emit mouse press event
    timeline_clicked = Signal(int)

    def __init__(self, duration, item_width=200, parent=None):
        super().__init__(parent=parent)

        self.duration = duration
        self.item_width = item_width
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout()
        for i in range(self.duration + 1):
            time_frame_widget = self.create_time_frame(i)
            layout.addWidget(time_frame_widget)

        self.setLayout(layout)

    def create_time_frame(self, timestamp):
        frame = QWidget()
        frame.setFixedWidth(self.item_width)

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        time_layout = QVBoxLayout()
        time_layout.setContentsMargins(0, 0, 0, 0)
        time_layout.setSpacing(0)

        time_layout.addStretch(1)
        time_layout.addWidget(QLabel(f'{timestamp}s'))
        time_layout.addWidget(QLabel('.'))
        time_layout.addStretch(1)
        layout.addLayout(time_layout)

        frame.setLayout(layout)
        return frame

    def mousePressEvent(self, event: QMouseEvent):
        if event.buttons() & Qt.LeftButton:
            self.timeline_clicked.emit(event.pos().x())


class TimelineSlider(QWidget):
    # Custom signal to emit mouse release event
    timeline_slider_released = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.color = '#4D4C7D'

        self.init_ui()

        self.dragging = False
        self.offset = QPoint()

    def init_ui(self):
        width = 16
        height = 250
        self.setFixedSize(width, height)

        top_label = QLabel(self)
        top_label.setFixedSize(width, width)
        top_label.setStyleSheet(f"""
            border-radius: 8px;
            background-color: {self.color};
        """)
        top_label.move(0, 0)

        vertical_bar_width = 2
        vertical_bar = QLabel(self)
        vertical_bar.setFixedSize(vertical_bar_width, height)
        vertical_bar.move((width - vertical_bar_width) // 2, 0)
        vertical_bar.setStyleSheet(f'background-color: {self.color};')

    def mousePressEvent(self, event: QMouseEvent):
        if event.buttons() & Qt.LeftButton:
            self.dragging = True
            self.offset = event.pos()

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.dragging:
            new_x = self.mapToParent(event.pos()).x() - self.width() / 2
            if new_x < 0:
                new_x = 0
            elif new_x > self.parent().width() - self.width():
                new_x = self.parent().width() - self.width()
            self.move(new_x, self.y())

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.dragging = False
            x_pos = self.mapToParent(event.pos()).x()
            self.timeline_slider_released.emit(x_pos)


class ClipTrack(QWidget):
    # Custom signal to emit mouse press event
    clip_clicked = Signal(int)

    def __init__(self, duration, parent=None):
        super().__init__(parent=parent)

        self.duration = duration
        self.track_width = int(duration * AppContext.get('pix_per_sec'))

        self.color = '#373A40'
        self.strip_color = '#686D76'
        self.active_border_color = 'darkgray'
        self.active_border_width = 2
        self.border_radius = 6

        self.setFixedSize(self.track_width, 60)
        self.init_ui()
        self.update_style()

        self.installEventFilter(self)

    def init_ui(self):
        # Main layout
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Left strip
        self.left_strip = QLabel()
        self.left_strip.setFixedSize(10, 60)

        # Center widget
        self.center_widget = QFrame()
        self.center_widget.setObjectName('center_widget')
        center_layout = QVBoxLayout(self.center_widget)
        center_layout.setContentsMargins(0, 0, 0, 0)
        center_layout.setSpacing(0)
        center_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Top row
        top_row = QHBoxLayout()
        top_row.setSpacing(4)

        clip_label = QLabel()
        clip_image_path = ImageAssets.file('images/ui_controls/clip.svg')
        clip_label.setPixmap(QPixmap(clip_image_path))

        top_row.addStretch(1)
        top_row.addWidget(clip_label)
        top_row.addWidget(QLabel('Clip'))
        top_row.addStretch(1)

        # Bottom row
        bottom_row = QHBoxLayout()
        bottom_row.setSpacing(4)

        clock_label = QLabel()
        clock_label.setPixmap(QPixmap(ImageAssets.file('images/ui_controls/clock.svg')))

        bottom_row.addStretch(1)
        bottom_row.addWidget(QLabel(f'{self.duration:.1f}s'))
        bottom_row.addWidget(clock_label)
        bottom_row.addWidget(QLabel('2x'))
        bottom_row.addStretch(1)

        center_layout.addLayout(top_row)
        center_layout.addLayout(bottom_row)

        # Right strip
        self.right_strip = QLabel()
        self.right_strip.setFixedSize(10, 60)

        # Add widgets to main layout
        main_layout.addWidget(self.left_strip)
        main_layout.addWidget(self.center_widget)
        main_layout.addWidget(self.right_strip)

    def update_style(self, active=False):
        active_border_style = f'{self.active_border_width}px solid {self.active_border_color}' if active else 'none'

        self.center_widget.setStyleSheet(f"""
            QFrame#center_widget {{
                background-color: {self.color};
                border-top: {active_border_style};
                border-bottom: {active_border_style};
            }}
        """)

        strip_style = f"""
            background-color: {self.strip_color};
            border-top: {active_border_style};
            border-bottom: {active_border_style};
        """

        self.left_strip.setStyleSheet(f"""
            {strip_style}
            border-left: {active_border_style};
            border-top-left-radius: {self.border_radius}px;
            border-bottom-left-radius: {self.border_radius}px;
        """)

        self.right_strip.setStyleSheet(f"""
            {strip_style}
            border-right: {active_border_style};
            border-top-right-radius: {self.border_radius}px;
            border-bottom-right-radius: {self.border_radius}px;
        """)

    def mousePressEvent(self, event: QMouseEvent):
        if event.buttons() & Qt.LeftButton:
            self.clip_clicked.emit(event.pos().x())
            self.update_style(active=True)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.MouseButtonPress and not self.rect().contains(event.pos()):
            self.update_style(active=False)
        return super().eventFilter(obj, event)


class ZoomTrack(QWidget):
    mouse_released = Signal(int)
    delete_clicked = Signal(int)

    def __init__(self, index, duration, drag_range_x=None, parent=None):
        super().__init__(parent=parent)

        self.track_width = int(duration * AppContext.get('pix_per_sec'))

        self.index = index
        self.duration = duration
        self.drag_range_x = drag_range_x

        self.color = '#363062'
        self.strip_color = '#616094'
        self.active_border_color = 'darkgray'
        self.active_border_width = 2
        self.border_radius = 6

        self.setFixedSize(self.track_width, 60)
        self.init_ui()
        self.update_style()

        self.dragging = False
        self.offset = QPoint()

    def init_ui(self):
        # Main layout
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Left strip
        self.left_strip = QLabel()
        self.left_strip.setFixedSize(10, 60)

        # Center widget
        self.center_widget = QFrame()
        self.center_widget.setObjectName('center_widget')
        center_layout = QVBoxLayout(self.center_widget)
        center_layout.setContentsMargins(0, 0, 0, 0)
        center_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Top row
        top_row = QHBoxLayout()
        top_row.setContentsMargins(0, 0, 0, 0)
        top_row.setSpacing(4)

        clip_label = QLabel()
        clip_image_path = ImageAssets.file('images/ui_controls/cursor.svg')
        clip_image = QPixmap(clip_image_path)
        clip_label.setPixmap(clip_image)

        top_row.addStretch(1)
        top_row.addWidget(clip_label)
        top_row.addWidget(QLabel('Zoom'))
        top_row.addStretch(1)

        # Bottom row
        bottom_row = QHBoxLayout()
        bottom_row.setContentsMargins(0, 0, 0, 0)
        bottom_row.setSpacing(4)

        zoom_image = QPixmap(ImageAssets.file('images/ui_controls/zoom.svg'))
        zoom_label = QLabel()
        zoom_label.setPixmap(zoom_image)

        mouse_image = QPixmap(ImageAssets.file('images/ui_controls/mouse.svg'))
        mouse_label = QLabel()
        mouse_label.setPixmap(mouse_image)

        bottom_row.addStretch(1)
        bottom_row.addWidget(zoom_label)
        bottom_row.addWidget(QLabel('2x'))
        bottom_row.addWidget(mouse_label)
        bottom_row.addWidget(QLabel('Auto'))
        bottom_row.addStretch(1)

        center_layout.addLayout(top_row)
        center_layout.addLayout(bottom_row)

        # Right strip
        self.right_strip = QLabel()
        self.right_strip.setFixedSize(10, 60)

        main_layout.addWidget(self.left_strip)
        main_layout.addWidget(self.center_widget)
        main_layout.addWidget(self.right_strip)

        self.setLayout(main_layout)

    def update_style(self, active=False):
        active_border_style = f'{self.active_border_width}px solid {self.active_border_color}' if active else 'none'

        self.center_widget.setStyleSheet(f"""
            QFrame#center_widget {{
                background-color: {self.color};
                border-top: {active_border_style};
                border-bottom: {active_border_style};
            }}
        """)

        strip_style = f"""
            background-color: {self.strip_color};
            border-top: {active_border_style};
            border-bottom: {active_border_style};
        """

        self.left_strip.setStyleSheet(f"""
            {strip_style}
            border-left: {active_border_style};
            border-top-left-radius: {self.border_radius}px;
            border-bottom-left-radius: {self.border_radius}px;
        """)

        self.right_strip.setStyleSheet(f"""
            {strip_style}
            border-right: {active_border_style};
            border-top-right-radius: {self.border_radius}px;
            border-bottom-right-radius: {self.border_radius}px;
        """)

    def contextMenuEvent(self, event):
        context_menu = QMenu(self)
        context_menu.setStyleSheet("""
            QMenu {
                padding-top: 10px;
                padding-bottom: 10px;
                border-radius: 10px;
                background: red;
            }
            QMenu::item:selected {
                background-color: darkgray;
            }
        """)
        delete_action = QAction(QIcon(ImageAssets.file('images/ui_controls/trash.svg')), "Delete", self)
        delete_action.triggered.connect(self.delete_track)
        context_menu.addAction(delete_action)
        context_menu.exec(event.globalPos())

    def delete_track(self, event):
        # Update the left and the right zoom track's drag range of the current track
        self.delete_clicked.emit(self.index)

    def mousePressEvent(self, event: QMouseEvent):
        if event.buttons() & Qt.LeftButton:
            self.dragging = True
            self.offset = event.pos()

        # Set active style
        self.update_style(active=True)

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.dragging:
            diff = self.mapToParent(event.pos()).x() - self.mapToParent(self.offset).x()
            new_x = self.mapToParent(self.pos()).x() / 2 + diff

            drag_minimum_x = 0
            drag_maximum_x = 1e6

            if isinstance(self.drag_range_x, (list, tuple)) and len(self.drag_range_x) == 2:
                drag_minimum_x, drag_maximum_x = self.drag_range_x

            if new_x < drag_minimum_x:
                new_x = drag_minimum_x
            elif new_x + self.width() > drag_maximum_x:
                new_x = drag_maximum_x - self.width()

            self.move(new_x, self.y())

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.dragging = False

            # Update the current zoom track's starting frame index in the underlying model
            pix_per_sec = AppContext.get('pix_per_sec')
            fps = AppContext.get('model').fps
            click_data = AppContext.get('model').mouse_events['click']
            x_pos = self.mapToParent(event.pos()).x() - self.width() / 2

            if self.index < len(click_data):
                update_clicked_frame_index = int(x_pos / pix_per_sec * fps)
                click_item = click_data[self.index - 1]
                click_item[2] = update_clicked_frame_index

            # Update the left and the right zoom track's drag range of the current track
            self.mouse_released.emit(self.index)