import time
import re
import platform
from enum import Enum, auto

import cv2
import numpy as np
from utils.image import ImageAssets
from utils.general import hex_to_rgb, find_largest_leq_sorted
from utils.image import ImageAssets


class BaseTransform:
    def __init__(self):
        pass

    def __call__(self, **kwargs):
        raise NotImplementedError('Transform __call__ method must be implemented.')


class Compose(BaseTransform):
    def __init__(self, transforms):
        super().__init__()

        self.transforms = transforms

    def __call__(self, **kwargs):
        input = kwargs
        for _, t in self.transforms.items():
            input = t(**input)

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
        input = kwargs['input']
        height, width = input.shape[:2]
        w_factor, h_factor = self.aspect_ratio

        if w_factor is None or h_factor is None:
            kwargs['video_width'] = width
            kwargs['video_height'] = height
            kwargs['frame_width'] = width
            kwargs['frame_height'] = height
            return kwargs

        ratio = w_factor / h_factor

        if width / ratio >= height:
            new_width = width
            new_height = int(width / ratio)
        else:
            new_width = int(height * ratio)
            new_height = height

        kwargs['video_width'] = new_width
        kwargs['video_height'] = new_height
        kwargs['frame_width'] = width
        kwargs['frame_height'] = height

        return kwargs


class Padding(BaseTransform):
    def __init__(self, padding):
        super().__init__()

        self.padding = padding

    def __call__(self, **kwargs):
        input = kwargs['input']
        video_width = kwargs['video_width']
        video_height = kwargs['video_height']

        frame_height, frame_width = input.shape[:2]
        gap_x, gap_y = max(0, (video_width - frame_width) // 2), max(0, (video_height - frame_height) // 2)
        pad_x, pad_y = 0, 0

        if isinstance(self.padding, (list, tuple)):
            if len(self.padding) == 2:
                pad_x, pad_y = self.padding[0]
            else:
                raise Exception('Invalid padding format.')
        elif isinstance(self.padding, int):
            if gap_x > gap_y:
                pad_y = self.padding
                new_height = video_height - 2 * pad_y
                new_width = int(new_height * frame_width / frame_height)
                pad_x = max(0, (video_width - new_width) // 2)
            else:
                pad_x = self.padding
                new_width = video_width - 2 * pad_x
                new_height = int(new_width * frame_height / frame_width)
                pad_y = max(0, (video_height - new_height) // 2)
        else:
            raise Exception('Invalid padding format.')

        new_width = max(1, video_width - 2 * pad_x)
        new_height = max(1, video_height - 2 * pad_y)

        kwargs['frame_width'] = new_width
        kwargs['frame_height'] = new_height

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
        zoom_factor = kwargs.get('zoom_factor', 1)

        height, width = input.shape[:2]
        rounded_corners = {'top_left': True, 'top_right': True, 'bottom_right': True, 'bottom_left': True}

        if 'mask_rounded_corners' in kwargs:
            rounded_corners = kwargs['mask_rounded_corners']

        r = int(zoom_factor * self.radius) if zoom_factor > 1 else self.radius
        if r > 0:
            # Create a mask
            mask = np.zeros(shape=(height, width), dtype=np.uint8)
            rect_w, rect_h = width - 2 * r, height - 2 * r
            cv2.rectangle(mask, (r, 0), (r + rect_w, height), 255, -1)
            cv2.rectangle(mask, (0, r), (width - 1, r + rect_h), 255, -1)

            # Draw ellipses instead of circles
            if rounded_corners['top_left']:
                cv2.ellipse(mask, (r, r), (r, r), 180, 0, 90, 255, -1)  # Top-left corner
            else:
                cv2.rectangle(mask, (0, 0), (r, r), 255, -1)

            if rounded_corners['top_right']:
                cv2.ellipse(mask, (width - r, r), (r, r), 270, 0, 90, 255, -1)  # Top-right corner
            else:
                cv2.rectangle(mask, (width - r, 0), (width, r), 255, -1)

            if rounded_corners['bottom_right']:
                cv2.ellipse(mask, (width - r, height - r), (r, r), 0, 0, 90, 255, -1)  # Bottom-right corner
            else:
                cv2.rectangle(mask, (width - r, height - r), (width, height), 255, -1)

            if rounded_corners['bottom_left']:
                cv2.ellipse(mask, (r, height - r), (r, r), 90, 0, 90, 255, -1)  # Bottom-left corner
            else:
                cv2.rectangle(mask, (0, height - r), (r, height), 255, -1)
        else:
            mask = np.full(shape=(height, width), fill_value=255, dtype=np.uint8)

        kwargs['mask'] = mask
        return kwargs


class ZoomPosition(Enum):
    TOP_LEFT = auto()
    TOP = auto()
    TOP_RIGHT = auto()
    RIGHT = auto()
    BOTTOM_RIGHT = auto()
    BOTTOM = auto()
    BOTTOM_LEFT = auto()
    LEFT = auto()
    CENTER = auto()


class Zoom(BaseTransform):
    def __init__(
        self,
        click_data,
        fps,
        zoom_in_duration=1.0,
        zoom_out_duration=1.0,
        zoom_factor=2.0
    ):
        super().__init__()

        self.click_data = click_data
        self.move_data = None
        self.clicked_indices = [click[2] for click in click_data]
        self.zoom_in_duration = zoom_in_duration
        self.zoom_out_duration = zoom_out_duration
        self.zoom_factor = zoom_factor
        self.fps = fps

        self.corner_ratio = 0.3

    def ease_in_out_quad(self, t):
        """Easing function for smooth zoom transitions."""
        if t < 0.5:
            return 2 * t * t
        return -1 + (4 - 2 * t) * t

    def _calculate_zoom_position(self, click_x, click_y):
        corner_ratio = self.corner_ratio

        if click_y < corner_ratio:
            # top area
            if click_x < corner_ratio:
                return ZoomPosition.TOP_LEFT
            elif click_x < 1 - corner_ratio:
                return ZoomPosition.TOP
            else:
                return ZoomPosition.TOP_RIGHT
        elif click_y < 1 - corner_ratio:
            # Center area
            if click_x < corner_ratio:
                return ZoomPosition.LEFT
            elif click_x < 1 - corner_ratio:
                return ZoomPosition.CENTER
            else:
                return ZoomPosition.RIGHT
        else:
            if click_x < corner_ratio:
                return ZoomPosition.BOTTOM_LEFT
            elif click_x < 1 - corner_ratio:
                return ZoomPosition.BOTTOM
            else:
                return ZoomPosition.BOTTOM_RIGHT

    def __call__(self, **kwargs):
        input = kwargs['input']
        video_width = kwargs['video_width']
        video_height = kwargs['video_height']
        frame_width = kwargs['frame_width']
        frame_height = kwargs['frame_height']
        frame_index = kwargs['frame_index']

        shift_x = 0
        shift_y = 0

        # Find the largest less equal click frame index than the current index
        index = find_largest_leq_sorted(self.clicked_indices, frame_index)

        if index >= 0:
            click = self.click_data[index]

            # If the current frame is within the valid range of the click
            rel_clicked_x, rel_clicked_y, clicked_frame_index, duration = click
            duration_in_frames = int(duration * self.fps)

            if clicked_frame_index <= frame_index < clicked_frame_index + duration_in_frames:
                # Calculate the elapsed time and the stage of zoom
                elapsed_time = (frame_index - clicked_frame_index) / self.fps
                if elapsed_time <= self.zoom_in_duration:
                    # Zooming in
                    progress = elapsed_time / self.zoom_in_duration
                    factor = self.ease_in_out_quad(progress)
                    zoom_factor = 1 + (self.zoom_factor - 1) * factor
                elif elapsed_time >= duration - self.zoom_out_duration:
                    # Zooming out
                    progress = (elapsed_time - (duration - self.zoom_out_duration)) / self.zoom_out_duration
                    zoom_factor = self.zoom_factor - (self.zoom_factor - 1) * self.ease_in_out_quad(progress)
                else:
                    # Maintain zoom
                    zoom_factor = self.zoom_factor
            else:
                zoom_factor = 1

            new_frame_width = int(zoom_factor * frame_width)
            new_frame_height = int(zoom_factor * frame_height)

            left_half_new_frame_width = new_frame_width // 2
            right_half_new_frame_width = new_frame_width - left_half_new_frame_width
            top_half_new_frame_height = new_frame_height // 2
            bottom_half_new_frame_height = new_frame_height - top_half_new_frame_height

            left_half_frame_width = frame_width // 2
            right_half_frame_width = frame_width - left_half_frame_width
            top_half_frame_height = frame_height // 2
            bottom_half_frame_height = frame_height - top_half_frame_height

            position = self._calculate_zoom_position(rel_clicked_x, rel_clicked_y)

            if position == ZoomPosition.TOP_LEFT:
                shift_x = left_half_new_frame_width - left_half_frame_width
                shift_y = top_half_new_frame_height - top_half_frame_height
            elif position == ZoomPosition.TOP:
                shift_x = 0
                shift_y = top_half_new_frame_height - top_half_frame_height
            elif position == ZoomPosition.TOP_RIGHT:
                shift_x = right_half_frame_width - right_half_new_frame_width
                shift_y = top_half_new_frame_height - top_half_frame_height
            elif position == ZoomPosition.RIGHT:
                shift_x = right_half_frame_width - right_half_new_frame_width
                shift_y = 0
            elif position == ZoomPosition.BOTTOM_RIGHT:
                shift_x = right_half_frame_width - right_half_new_frame_width
                shift_y = bottom_half_frame_height - bottom_half_new_frame_height
            elif position == ZoomPosition.BOTTOM:
                shift_x = 0
                shift_y = bottom_half_frame_height - bottom_half_new_frame_height
            elif position == ZoomPosition.BOTTOM_LEFT:
                shift_x = left_half_new_frame_width - left_half_frame_width
                shift_y = bottom_half_frame_height - bottom_half_new_frame_height
            elif position == ZoomPosition.LEFT:
                shift_x = left_half_new_frame_width - left_half_frame_width
                shift_y = 0
            else:
                # center
                shift_x = 0
                shift_y = 0
        else:
            shift_x = 0
            shift_y = 0
            new_frame_width = frame_width
            new_frame_height = frame_height
            zoom_factor = 1

        resized_frame = cv2.resize(input, (new_frame_width, new_frame_height))

        video_cx, video_cy = video_width // 2, video_height // 2
        frame_x1 = video_cx + shift_x - new_frame_width // 2
        frame_y1 = video_cy + shift_y - new_frame_height // 2

        x1 = max(0, frame_x1)
        y1 = max(0, frame_y1)
        x2 = min(video_width, frame_x1 + new_frame_width)
        y2 = min(video_height, frame_y1 + new_frame_height)

        crop_xmin = max(0, new_frame_width // 2 - video_cx - shift_x)
        crop_ymin = max(0, new_frame_height // 2 - video_cy - shift_y)
        crop_width = x2 - x1
        crop_height = y2 - y1
        cropped_frame = resized_frame[crop_ymin:crop_ymin+crop_height, crop_xmin:crop_xmin+crop_width, :]

        # Modify the rounded border mask
        rounded_corners = {'top_left': True, 'top_right': True, 'bottom_right': True, 'bottom_left': True}
        if frame_x1 < 0:
            rounded_corners['top_left'] = False
            rounded_corners['bottom_left'] = False

        if frame_y1 < 0:
            rounded_corners['top_left'] = False
            rounded_corners['top_right'] = False

        if frame_x1 + new_frame_width > video_width:
            rounded_corners['top_right'] = False
            rounded_corners['bottom_right'] = False

        if frame_y1 + new_frame_height > video_height:
            rounded_corners['bottom_right'] = False
            rounded_corners['bottom_left'] = False

        kwargs['mask_rounded_corners'] = rounded_corners

        kwargs['input'] = cropped_frame
        kwargs['frame_width'] = crop_width
        kwargs['frame_height'] = crop_height
        kwargs['x_offset'] = x1
        kwargs['y_offset'] = y1
        kwargs['zoom_factor'] = zoom_factor

        return kwargs


class Cursor(BaseTransform):
    def __init__(self, move_data, size=64):
        super().__init__()

        self.size = size
        self.move_data = move_data
        self.cursors = self._load()

    def _load(self):
        system = platform.system().lower()

        if system == 'windows':
            sub_folder = 'windows'
        elif system == 'darwin':
            sub_folder = 'macos'
        elif system == 'linux':
            sub_folder = 'linux'
        else:
            raise Exception()

        arrow_image = cv2.imread(ImageAssets.file(f'images/ui_controls/cursor/{sub_folder}/cursor.png'), cv2.IMREAD_UNCHANGED)
        height, width = arrow_image.shape[:2]
        if height > width:
            new_height = self.size
            new_width = int(self.size * width / height)
        else:
            new_width = self.size
            new_height = int(self.size * height / width)

        arrow_image = cv2.resize(arrow_image, (new_width, new_height))

        pointing_hand = cv2.imread(ImageAssets.file(f'images/ui_controls/cursor/{sub_folder}/pointinghand.png'), cv2.IMREAD_UNCHANGED)
        pointing_hand = cv2.resize(pointing_hand, (self.size, self.size))

        return {'arrow': arrow_image, 'pointing_hand': pointing_hand}

    def _blend(self, image, x, y):
        if x is None or y is None:
            return image

        height, width = image.shape[:2]

        x, y = int(x * width), int(y * height)

        if x < 0 or y < 0:
            return image

        arrow_image = self.cursors['arrow']
        arrow_h, arrow_w = arrow_image.shape[:2]
        arrow_bgr = arrow_image[:, :, :3]
        arrow_mask = arrow_image[:, :, 3]

        # Ensure the ROI is within the frame boundaries
        if y + arrow_h > height:
            arrow_h = height - y
        if x + arrow_w > width:
            arrow_w = width - x

        # Get the region of interest from the input frame
        roi = image[y:y+arrow_h, x:x+arrow_w]

        # Use the mask to blend the arrow image with the input frame
        arrow_bgr_resized = arrow_bgr[:arrow_h, :arrow_w]
        arrow_mask_resized = arrow_mask[:arrow_h, :arrow_w]

        masked_arrow = cv2.bitwise_and(arrow_bgr_resized, arrow_bgr_resized, mask=arrow_mask_resized)
        masked_roi = cv2.bitwise_and(roi, roi, mask=cv2.bitwise_not(arrow_mask_resized))

        blended = cv2.add(masked_arrow, masked_roi)

        # Update the input frame with the blended result
        image[y:y+arrow_h, x:x+arrow_w] = blended
        return image

    def __call__(self, **kwargs):
        input = kwargs['input']
        frame_index = kwargs['frame_index']

        if frame_index < len(self.move_data):
            relative_mouse_x, relative_mouse_y, _ = self.move_data[frame_index]
            kwargs['input'] = self._blend(input, relative_mouse_x, relative_mouse_y)

        return kwargs


class Shadow(BaseTransform):
    def __init__(self):
        super().__init__()

    def __call__(self, **kwargs):
        x1 = kwargs['x_offset']
        y1 = kwargs['y_offset']
        x2 = x1 + kwargs['frame_width']
        y2 = y1 + kwargs['frame_height']
        return kwargs

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
            r, g, b = hex_to_rgb(hex_color)
            background_image = np.full(shape=(height, width, 3), fill_value=(b, g, r), dtype=np.uint8)

        return background_image

    def __call__(self, **kwargs):
        input = kwargs['input']
        width = kwargs['video_width']
        height = kwargs['video_height']

        if self.background_image is None or self.background_image.shape[0] != height or self.background_image.shape[1] != width:
            self.background_image = self._create_background_image(self.background, width, height)

        output = self.background_image.copy()

        x1 = kwargs['x_offset']
        y1 = kwargs['y_offset']
        x2 = x1 + kwargs['frame_width']
        y2 = y1 + kwargs['frame_height']

        if 'mask' in kwargs:
            mask = kwargs['mask']
            inv_mask = cv2.bitwise_not(mask)

            cropped_background = self.background_image[y1:y2, x1:x2, :].copy()
            cropped_background = cv2.bitwise_and(cropped_background, cropped_background, mask=inv_mask)

            rounded_input = cv2.bitwise_and(input, input, mask=mask)
            blended = cv2.add(cropped_background, rounded_input)

            output[y1:y2, x1:x2, :] = blended
        else:
            output[y1:y2, x1:x2, :] = input

        if 'shadow_mask' in kwargs:
            pass

        kwargs['input'] = output
        return kwargs