from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QFrame, QPushButton
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap

from views.widgets.custom_tabview import CustomTabView
from views.widgets.custom_slider import CustomSlider
from views.widgets.custom_scrollarea import CustomScrollArea
from views.widgets.custom_button import IconButton
from utils.image import ImageAssets
from utils.context import AppContext


class SideBar(QFrame):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setObjectName('sidebar')

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
        sidebar_content_layout.setContentsMargins(0, 30, 0, 0)
        sidebar_content_layout.setSpacing(50)  # Adjust spacing for content

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
            #sidebar {
                background-color: #131519;
                border-radius: 20px;
            }
        """)


class BackgroundSetting(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        # main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(20)

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
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

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
        self.reset_button.clicked.connect(self.reset_slider_value)

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

        # Slider layout
        slider_layout = QHBoxLayout()
        slider_layout.setContentsMargins(0, 0, 0, 0)
        slider_layout.setSpacing(5)

        self.slider = CustomSlider()
        self.slider.setMaximum(self.slider_max)
        self.slider.setMinimum(self.slider_min)
        self.slider.setValue(self.slider_value)
        slider_layout.addWidget(self.slider)

        # Value Label
        self.value_label = QLabel(str(self.slider_value))
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.value_label.setFixedWidth(30)
        self.value_label.setStyleSheet('color: darkgray;')
        slider_layout.addWidget(self.value_label)

        # Reset Button
        self.reset_button = IconButton(
            icon_path=ImageAssets.file('images/ui_controls/reset.svg'),
            icon_size=(24, 24)
        )
        slider_layout.addWidget(self.reset_button)

        main_layout.addLayout(slider_layout)
        self.setLayout(main_layout)

    def on_value_changed(self, value):
        self.value_label.setText(str(value))

    def reset_slider_value(self):
        self.slider.setValue(self.slider_value)


class PaddingSetting(BaseShapeSetting):
    def __init__(self):
        super().__init__('Padding', ImageAssets.file('images/ui_controls/padding.svg'), 500, 0, 50)

    def on_value_changed(self, value):
        super().on_value_changed(value)

        # Update model
        AppContext.get('model').set_padding(value)

        # Display frame
        frame = AppContext.get('model').current_frame
        AppContext.get('video_toolbar').display_frame(frame)


class InsetSetting(BaseShapeSetting):
    def __init__(self):
        super().__init__('Inset', ImageAssets.file('images/ui_controls/padding.svg'), 200, 0, 0)

    def on_value_changed(self, value):
        super().on_value_changed(value)

        # Update model
        AppContext.get('model').set_inset(value)

        # Display frame
        frame = AppContext.get('model').current_frame
        AppContext.get('video_toolbar').display_frame(frame)


class RoundnessSetting(BaseShapeSetting):
    def __init__(self):
        super().__init__('Roundness', ImageAssets.file('images/ui_controls/border.svg'), 100, 0, 10)

    def on_value_changed(self, value):
        super().on_value_changed(value)

        # Update model
        AppContext.get('model').set_roundness(value)

        # Display frame
        frame = AppContext.get('model').current_frame
        AppContext.get('video_toolbar').display_frame(frame)