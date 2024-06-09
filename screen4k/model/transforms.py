import time
import re

import cv2
import numpy as np
from utils.image import ImageAssets
from utils.general import hex_to_rgb


class BaseTransform:
    def __init__(self):
        pass

    def __call__(self, *args):
        raise NotImplementedError('Transform __call__ method must be implemented.')


class Compose(BaseTransform):
    def __init__(self, transforms):
        super().__init__()

        self.transforms = transforms

    def __call__(self, **kwargs):
        input = kwargs
        for _, transform in self.transforms.items():
            input = transform(**input)

        return input

    def __getitem__(self, key):
        return self.transforms.get(key)

    def __setitem__(self, key, value):
        self.transforms[key] = value


class AspectRatio(BaseTransform):
    def __init__(self, aspect_ratio):
        super().__init__()

        self.aspect_ratio = self._get_aspect_ratio(aspect_ratio)

    def _get_aspect_ratio(self, aspect_ratio):
        width, height = None, None

        if isinstance(aspect_ratio, str):
            aspect_ratio = re.sub(r'\s+', '', aspect_ratio)
            match = re.match(r'(\d+):(\d+)', aspect_ratio)
            if match:
                width = float(match.group(1))
                height = float(match.group(2))
                return width, height

        elif isinstance(aspect_ratio, (tuple, list)):
            if len(aspect_ratio) == 2:
                width, height = aspect_ratio[:2]
                return width, height

        return width, height

    def __call__(self, **kwargs):
        if len(kwargs) > 0:
            input = kwargs['input']
            w_factor, h_factor = self.aspect_ratio
            ratio = w_factor / h_factor
            height, width = input.shape[:2]

            if width / ratio >= height:
                new_width = width
                new_height = int(width / ratio)
            else:
                new_width = int(height * ratio)
                new_height = height

            kwargs['width'] = new_width
            kwargs['height'] = new_height

            return kwargs


class Padding(BaseTransform):
    def __init__(self, padding):
        super().__init__()

        self.padding = padding

    def __call__(self, **kwargs):
        if len(kwargs) >= 3:
            input, width, height = kwargs['input'], kwargs['width'], kwargs['height']

            pad_left, pad_top, pad_right, pad_bottom = 0, 0, 0, 0

            if isinstance(self.padding, (list, tuple)):
                if len(self.padding) == 2:
                    pad_left, pad_right = self.padding[0]
                    pad_top, pad_bottom = self.padding[1]
                elif len(self.padding) == 4:
                    pad_left, pad_top, pad_right, pad_bottom = self.padding
                else:
                    raise Exception('Invalid padding format.')
            elif isinstance(self.padding, int):
                pad_top, pad_bottom = self.padding, self.padding
                pad_left = int(pad_top * width / height)
                pad_right = pad_left
            else:
                raise Exception('Invalid padding format.')

            new_width = max(1, width - pad_left - pad_right)
            new_height = max(1, height - pad_top - pad_bottom)

            padded_frame = cv2.resize(input, (new_width, new_height))

            kwargs['input'] = padded_frame
            kwargs['pad_x'] = pad_left
            kwargs['pad_y'] = pad_top

            return kwargs


class Inset(BaseTransform):
    def __init__(self, inset, color=(0, 122, 222)):
        super().__init__()

        self.inset = inset
        self.color = color
        self.inset_frame = None

    def __call__(self, **kwargs):
        if len(kwargs) >= 3:
            input = kwargs['input']
            height, width = input.shape[:2]

            inset_left, inset_top, inset_right, inset_bottom = 0, 0, 0, 0

            if isinstance(self.inset, (list, tuple)):
                if len(self.inset) == 2:
                    inset_left, inset_right = self.inset[0]
                    inset_top, inset_bottom = self.inset[1]
                elif len(self.inset) == 4:
                    inset_left, inset_top, inset_right, inset_bottom = self.inset
                else:
                    raise Exception()
            elif isinstance(self.inset, int):
                inset_top, inset_bottom = self.inset, self.inset
                inset_left = int(inset_top * width / height)
                inset_right = inset_left
            else:
                raise Exception()

            new_width = width - inset_left - inset_right
            new_height = height - inset_top - inset_bottom

            if self.inset_frame is None or self.inset_frame.shape[0] != height or self.inset_frame.shape[1] != width:
                self.inset_frame = np.full_like(input, fill_value=self.color)

            resized_frame = cv2.resize(input, (new_width, new_height))
            self.inset_frame[inset_top:inset_top+new_height, inset_left:inset_left+new_width, :] = resized_frame

            kwargs['input'] = self.inset_frame
            return kwargs


class Roundness(BaseTransform):
    def __init__(self, radius=10):
        super().__init__()

        self.radius = radius

    def __call__(self, **kwargs):
        input = kwargs['input']
        height, width = input.shape[:2]

        # Create a mask
        mask = np.zeros(shape=(height, width), dtype=np.uint8)

        r = self.radius
        rect_w, rect_h = width - 2 * r, height - 2 * r
        cv2.rectangle(mask, (r, 0), (r + rect_w, height - 1), 255, -1)
        cv2.rectangle(mask, (0, r), (width - 1, r + rect_h), 255, -1)
        cv2.circle(mask, (r, r), r, 255, -1)
        cv2.circle(mask, (width - r, r), r, 255, -1)
        cv2.circle(mask, (width - r, height - r), r, 255, -1)
        cv2.circle(mask, (r, height - r), r, 255, -1)

        kwargs['mask'] = mask
        return kwargs


class Zoom(BaseTransform):
    def __init__(self):
        super().__init__()

    def __call__(self, input):
        pass


class Focus(BaseTransform):
    def __init__(self):
        super().__init__()

    def __call__(self, input):
        pass


class Background(BaseTransform):
    def __init__(self, background):
        super().__init__()

        self.background = background
        self.background_image = None

    def _create_background_image(self, background, width, height):
        if background['type'] == 'wallpaper':
            index = background['value']
            background_path = ImageAssets.file(f'images/wallpapers/original/gradient-wallpaper-{index:04d}.png')
            background_image = cv2.imread(background_path)

            # Crop if needed
            background_height, background_width = background_image.shape[:2]
            cx, cy = background_width // 2, background_height // 2
            xmin, ymin = cx - width // 2, cy - height // 2
            xmax, ymax = xmin + width, ymin + height
            background_image = background_image[ymin:ymax, xmin:xmax, :]
        elif background['type'] == 'gradient':
            pass
        elif background['type'] == 'color':
            hex_color = background['value']
            color = hex_to_rgb(hex_color)
            background_image = np.full(shape=(height, width, 3), fill_value=color, dtype=np.uint8)

        return background_image

    def __call__(self, **kwargs):
        input, width, height, pad_x, pad_y = kwargs['input'], kwargs['width'], kwargs['height'], kwargs['pad_x'], kwargs['pad_y']

        if self.background_image is None:
            self.background_image = self._create_background_image(self.background, width, height)

        # background_h, background_w = self.background_image.shape[:2]

        input_height, input_width = input.shape[:2]
        result_frame = self.background_image.copy()

        # Create a rounded border if needed
        if 'mask' in kwargs:
            mask = kwargs['mask']

            fg = cv2.bitwise_and(input, input, mask=mask)

            inv_mask = cv2.bitwise_not(mask)
            cropped_frame = result_frame[pad_y:pad_y+input_height, pad_x:pad_x+input_width]
            bg = cv2.bitwise_and(cropped_frame, cropped_frame, mask=inv_mask)

            input = cv2.add(fg, bg)

        result_frame[pad_y:pad_y+input_height, pad_x:pad_x+input_width, :] = input

        kwargs['result'] = result_frame

        return kwargs
