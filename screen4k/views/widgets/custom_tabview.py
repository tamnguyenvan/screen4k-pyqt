from PySide6.QtWidgets import (
    QWidget, QTabWidget, QVBoxLayout, QLabel, QStackedLayout,
    QPushButton, QHBoxLayout, QGridLayout
)
from PySide6.QtGui import QPixmap
from utils.image import ImageAssets
from utils.context import AppContext


class CustomTabView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)

        # Create buttons to switch tabs
        self.buttons_layout = QHBoxLayout()
        self.buttons_layout.setContentsMargins(0, 0, 0, 0)
        self.buttons_layout.setSpacing(0)
        layout.addLayout(self.buttons_layout)

        self.wallpaper_button = CustomTabButton('Wallpaper')
        self.wallpaper_button.clicked.connect(lambda: self.switch_tab(0))
        self.wallpaper_button.update_stylesheet(color='#4229f1')
        self.buttons_layout.addWidget(self.wallpaper_button)

        self.gradient_button = CustomTabButton('Gradient')
        self.gradient_button.clicked.connect(lambda: self.switch_tab(1))
        self.buttons_layout.addWidget(self.gradient_button)

        self.color_button = CustomTabButton('Color')
        self.color_button.clicked.connect(lambda: self.switch_tab(2))
        self.buttons_layout.addWidget(self.color_button)

        self.image_button = CustomTabButton('Image')
        self.image_button.clicked.connect(lambda: self.switch_tab(3))
        self.buttons_layout.addWidget(self.image_button)

        self.buttons = [
            self.wallpaper_button,
            self.gradient_button,
            self.color_button,
            self.image_button,
        ]

        # Create the stacked layout to hold pages
        self.stacked_layout = QStackedLayout()
        self.stacked_layout.setContentsMargins(0, 0, 0, 0)
        self.stacked_layout.setSpacing(0)
        layout.addLayout(self.stacked_layout)

        # Create pages
        self.pages = [
            WallpaperPage(),
            QLabel('Gradient page'),
            ColorPage(),
            QLabel('Image page')
        ]

        # Add pages to the stacked layout
        for page in self.pages:
            self.stacked_layout.addWidget(page)

        self.setLayout(layout)

        self.apply_styles()

    def switch_tab(self, index):
        self.stacked_layout.setCurrentIndex(index)

        for i, button in enumerate(self.buttons):
            if i == index:
                self.buttons[i].set_active()
            else:
                self.buttons[i].update_stylesheet()

    def apply_styles(self):
        pass


class CustomTabButton(QPushButton):
    def __init__(self, text='', parent=None):
        super().__init__(text, parent)

        self.update_stylesheet()

    def update_stylesheet(self, color='darkgray', border_bottom='1px solid #ccc'):
        self.setStyleSheet(f'''
            CustomTabButton {{
                background-color: transparent;
                border: 1px solid {color};
                padding: 10px;
                min-width: auto;
                color: {color};
                border-bottom: {border_bottom};
            }}
        ''')

    def set_active(self):
        # Change the style
        self.update_stylesheet(color='#4229f1', border_bottom='2px solid #4229f1')


class WallpaperPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.init_ui()

    def init_ui(self):
        # layout
        main_layout = QGridLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setHorizontalSpacing(10)
        main_layout.setVerticalSpacing(10)

        items_per_row = 7
        for i in range(20):
            row = i // items_per_row
            col = i % items_per_row
            main_layout.addWidget(WallpaperThumbnail(index=i+1), row, col)

        self.setLayout(main_layout)


class WallpaperThumbnail(QPushButton):
    def __init__(self, index, parent=None):
        super().__init__(parent=parent)

        self.index = index
        self.wallpaper_path = ImageAssets.file(f'images/wallpapers/preview/gradient-wallpaper-{self.index:04d}.png')

        self.init_ui()

        self.clicked.connect(self.on_click)

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)  # Ensure no margins in thumbnail layout
        layout.setSpacing(0)  # Ensure no spacing in thumbnail layout

        self.thumbnail = QLabel(self)
        self.thumbnail.setPixmap(QPixmap(self.wallpaper_path))

        layout.addWidget(self.thumbnail)
        self.setLayout(layout)
        self.setFixedSize(50, 50)  # Ensure each thumbnail has a fixed size
        self.setStyleSheet('border: 1px solid darkgray; background-color: white;')

    def on_click(self):
        # Update model
        AppContext.get('model').set_background({'type': 'wallpaper', 'value': self.index})

        # Display
        frame = AppContext.get('model').current_frame
        AppContext.get('video_toolbar').display_frame(frame)


class GradientPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.init_ui()

    def init_ui(self):
        pass


class ColorPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.colors = [
            '#FF3131', '#FF5757', '#FF66C4', '#CB6CE6', '#8C52FF', '#5E17EB', '#0097B2',
            '#0CC0DF', '#5CE1E6', '#38B6FF', '#5271FF', '#004AAD', '#00BF63', '#7ED957',
            '#C1FF72', '#FFDE59', '#FFBD59', '#FF914D', '#FA7420', '#5E17EB',
        ]
        self.num_columns = 7

        self.init_ui()

    def init_ui(self):
        grid_layout = QGridLayout()
        grid_layout.setContentsMargins(0, 0, 0, 0)
        grid_layout.setSpacing(0)
        self.setLayout(grid_layout)

        for i, color in enumerate(self.colors):
            color_button = ColorButton(i, color)
            row = i // self.num_columns
            col = i % self.num_columns
            grid_layout.addWidget(color_button, row, col)


class ColorButton(QPushButton):
    def __init__(self, index, color, size=50, parent=None):
        super().__init__(parent=parent)

        self.index = index
        self.color = color
        self.size = size

        self.init_ui()

        self.clicked.connect(self.on_click)

    def init_ui(self):
        self.setStyleSheet(f'background-color: {self.color}; border: 1px solid darkgray;')
        self.setFixedSize(self.size, self.size)

    def on_click(self):
        # Update model
        AppContext.get('model').set_background({'type': 'color', 'value': self.color})

        # Display
        frame = AppContext.get('model').current_frame
        AppContext.get('video_toolbar').display_frame(frame)


class ImagePage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.init_ui()

    def init_ui(self):
        pass