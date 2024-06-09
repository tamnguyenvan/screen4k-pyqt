from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap

from views.widgets.custom_tabview import CustomTabView
from views.widgets.custom_slider import CustomSlider
from views.widgets.custom_scrollarea import CustomScrollArea
from utils.image import ImageAssets
from utils.context import AppContext


class SideBar(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        # main layout
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(0)

        # scroll area
        sidebar_scroll_area = CustomScrollArea()
        sidebar_scroll_area.setWidgetResizable(True)
        sidebar_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        sidebar_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        sidebar_content_widget = QWidget()
        sidebar_content_layout = QVBoxLayout(sidebar_content_widget)
        sidebar_content_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_content_layout.setSpacing(10)  # Adjust spacing for content

        # Background settings
        self.background_setting_widget = BackgroundSetting()
        sidebar_content_layout.addWidget(self.background_setting_widget)

        # Shape settings
        self.shape_setting_widget = ShapeSetting()
        sidebar_content_layout.addWidget(self.shape_setting_widget)

        # Add content to sidebar
        sidebar_scroll_area.setWidget(sidebar_content_widget)

        layout.addWidget(sidebar_scroll_area)

        self.setLayout(layout)

        self.update_stylesheet()

    def update_stylesheet(self):
        self.setStyleSheet("""
            SideBar {
                background-color: #f0f0f0;
            }
        """)


class BackgroundSetting(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        # main layout
        main_layout = QVBoxLayout()

        title_layout = QHBoxLayout()
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(8)

        # Label
        icon_label = QLabel()
        icon_path = ImageAssets.file('images/ui_controls/background.svg')
        pixmap = QPixmap(icon_path)
        icon_label.setPixmap(pixmap)
        title_layout.addWidget(icon_label)

        label = QLabel('Background')
        title_layout.addWidget(label)

        title_layout.addStretch(1)

        # custom tabview
        tabview = CustomTabView()

        main_layout.addLayout(title_layout)
        main_layout.addWidget(tabview)

        self.setLayout(main_layout)
        self.update_stylesheet()

    def update_stylesheet(self):
        self.setStyleSheet("""
            QLabel {
                font-size: 12pt;
            }
        """)


class ShapeSetting(QWidget):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        # main layout
        main_layout = QVBoxLayout()

        # Label
        label = QLabel('Shape')
        label.setStyleSheet('color: #888;')

        main_layout.addWidget(label)

        main_layout.addWidget(PaddingSetting())

        main_layout.addWidget(InsetSetting())
        main_layout.addWidget(RoundnessSetting())

        self.setLayout(main_layout)
        self.update_stylesheet()

    def update_stylesheet(self):
        self.setStyleSheet("""
            QLabel {
                font-size: 12pt;
            }
        """)


class BaseShapeSetting(QWidget):
    def __init__(self, label_text, icon_path, slider_max, slider_min, slider_value):
        super().__init__()

        self.label_text = label_text
        self.icon_path = icon_path
        self.slider_max = slider_max
        self.slider_min = slider_min
        self.slider_value = slider_value

        self.init_ui()

        self.slider.valueChanged.connect(self.on_value_changed)

    def init_ui(self):
        # main layout
        main_layout = QVBoxLayout()

        title_layout = QHBoxLayout()
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(8)

        # Label
        icon_label = QLabel()
        pixmap = QPixmap(self.icon_path)
        icon_label.setPixmap(pixmap)
        title_layout.addWidget(icon_label)

        label = QLabel(self.label_text)
        title_layout.addWidget(label)
        title_layout.addStretch(1)

        main_layout.addLayout(title_layout)

        # Slider
        self.slider = CustomSlider()
        self.slider.setMaximum(self.slider_max)
        self.slider.setMinimum(self.slider_min)
        self.slider.setValue(self.slider_value)
        main_layout.addWidget(self.slider)

        self.setLayout(main_layout)

    def on_value_changed(self, value):
        pass


class PaddingSetting(BaseShapeSetting):
    def __init__(self):
        super().__init__('Padding', ImageAssets.file('images/ui_controls/padding.svg'), 500, 0, 50)

    def on_value_changed(self, value):
        # Update model
        AppContext.get('model').set_padding(value)

        # Display frame
        frame = AppContext.get('model').current_frame
        AppContext.get('video_toolbar').display_frame(frame)


class InsetSetting(BaseShapeSetting):
    def __init__(self):
        super().__init__('Inset', ImageAssets.file('images/ui_controls/padding.svg'), 200, 0, 0)

    def on_value_changed(self, value):
        # Update model
        AppContext.get('model').set_inset(value)

        # Display frame
        frame = AppContext.get('model').current_frame
        AppContext.get('video_toolbar').display_frame(frame)


class RoundnessSetting(BaseShapeSetting):
    def __init__(self):
        super().__init__('Roundness', ImageAssets.file('images/ui_controls/padding.svg'), 100, 0, 10)

    def on_value_changed(self, value):
        # Update model
        AppContext.get('model').set_roundness(value)

        # Display frame
        frame = AppContext.get('model').current_frame
        AppContext.get('video_toolbar').display_frame(frame)