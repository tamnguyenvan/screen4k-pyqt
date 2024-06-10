import time
import cv2

from model.recorder import ScreenRecorder
from model.transforms import Compose, AspectRatio, Padding, Inset, Roundness, Background
from utils.general import generate_video_path
from utils.image import ImageAssets


class Model:
    def __init__(self):
        self._input_video_path = None
        self._output_video_path = None
        self._screen_recorder = None

        self._video_capture = None
        self._frame_width = None
        self._frame_height = None
        self._num_frames = None
        self._frame_index = 0
        self._duration = 0

        self._input_video_path = '/home/tamnv/Downloads/upwork-contract-exporter.mp4'
        self._video_capture = cv2.VideoCapture(self._input_video_path)
        self._fps = 30
        self._frame_width = 1920
        self._frame_height = 1080
        self._num_frames = 750
        self._frame_index = 0
        self._duration = 25

        self._mouse_events = None
        self._mouse_events = {
            'click': [
                [0.5, 0.5, 100, 3],
                [0.3, 0.3, 200, 3],
                [0.3, 0.3, 400, 3],
            ],
            'move': []
        }
        self._transform = None

        background = {'type': 'wallpaper','value': 1}
        self._transform = Compose({
            'aspect_ratio': AspectRatio('16:9'),
            'padding': Padding(padding=50),
            'inset': Inset(inset=0),
            'roundness': Roundness(radius=20),
            'background': Background(background=background)
        })

    def _get(self, frame_index=None):
        if self._video_capture is None:
            print('Video capture is None')
            return

        self._frame_index = int(self._video_capture.get(cv2.CAP_PROP_POS_FRAMES))

        if frame_index is not None:
            self._video_capture.set(cv2.CAP_PROP_POS_FRAMES, frame_index)

        ret, frame = self._video_capture.read()
        if not ret:
            print('empty frame')
            return

        if self._transform is not None:
            result = self._transform(input=frame)
            frame = result['result']

        return frame

    def start_recording(self):
        if self._screen_recorder is None:
            self._input_video_path = generate_video_path()
            self._screen_recorder = ScreenRecorder(self._input_video_path)

        print('start recording', self._input_video_path)
        self._screen_recorder.start_recording()

    def stop_recording(self):
        print('stop recording')
        if self._screen_recorder is not None:
            self._screen_recorder.stop_recording()

            # Initialize video capture
            self._video_capture = cv2.VideoCapture(self._input_video_path)
            self._fps = int(self._video_capture.get(cv2.CAP_PROP_FPS))
            self._frame_width = int(self._video_capture.get(cv2.CAP_PROP_FRAME_WIDTH))
            self._frame_height = int(self._video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
            self._num_frames = int(self._video_capture.get(cv2.CAP_PROP_FRAME_COUNT))
            self._duration = self._num_frames / self._fps if self._fps > 0 else 0

            # Mouse events
            self._mouse_events = self._screen_recorder.mouse_events

            background_image = cv2.imread(ImageAssets.file('images/wallpapers/original/gradient-wallpaper-0001.png'))
            self._transform = Compose([
                AspectRatio('16:9'),
                Padding(padding=50),
                Inset(inset=0, color=(255, 255, 255)),
                Background(background_image=background_image)
            ])

    def cancel_recording(self):
        print('cancel recording')
        if self._screen_recorder is not None:
            self._screen_recorder.cancel_recording()

            # Remove

    @property
    def current_frame(self):
        frame_index = self.current_frame_index
        frame = self._get(self._frame_index)
        self.current_frame_index = frame_index
        return frame

    @property
    def current_frame_index(self):
        return int(self._video_capture.get(cv2.CAP_PROP_POS_FRAMES))

    @current_frame_index.setter
    def current_frame_index(self, value):
        self._video_capture.set(cv2.CAP_PROP_POS_FRAMES, value)

    @property
    def fps(self):
        return self._fps

    @property
    def num_frames(self):
        return self._num_frames

    @property
    def duration(self):
        return self._duration

    @property
    def mouse_events(self):
        return self._mouse_events

    def next_frame(self):
        return self._get()

    def get_frame(self, frame_index):
        return self._get(frame_index)

    def set_background(self, background):
        self._transform['background'] = Background(background=background)

    def set_padding(self, padding):
        self._transform['padding'] = Padding(padding=padding)

    def set_inset(self, inset):
        self._transform['inset'] = Inset(inset=inset)

    def set_roundness(self, radius):
        self._transform['roundness'] = Roundness(radius=radius)