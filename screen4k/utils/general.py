import os
from pathlib import Path
from datetime import datetime
import tempfile

import numpy as np


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


def find_largest_leq_sorted(arr, x):
    if len(arr) == 0:
        return -1

    idx = np.searchsorted(arr, x, side='right') - 1

    if idx >= 0 and arr[idx] <= x:
        return idx
    else:
        return -1


def find_smallest_geq_sorted(arr, x):
    if len(arr) == 0:
        return -1

    idx = np.searchsorted(arr, x, side='left')

    if idx < len(arr) and arr[idx] >= x:
        return idx
    else:
        return -1