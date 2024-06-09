import os
from pathlib import Path
from datetime import datetime
import tempfile

def str2bool(x: str) -> bool:
    x = x.lower()
    return x == 'true' or x == '1'

def generate_video_path(prefix: str = 'ScreenSpace', extension: str = '.mp4'):
    # Use the system's temporary directory
    root = Path(tempfile.gettempdir())

    # Create a unique file name using current datetime
    time_str = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    file_name = f'{prefix}_{time_str}{extension}'

    # Generate the full path
    return str(root / file_name)


def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return r, g, b