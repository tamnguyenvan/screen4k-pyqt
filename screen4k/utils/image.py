import os
from pathlib import Path

class ImageAssets:
    @staticmethod
    def file(filename):
        root_dir = (Path(__file__).parent / '../..').resolve()
        return str(root_dir / filename)