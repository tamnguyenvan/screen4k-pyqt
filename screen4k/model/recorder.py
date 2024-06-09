import os
import time
from threading import Thread, Event
import cv2
from vidgear.gears import ScreenGear
from pynput.mouse import Listener
from loguru import logger


class ScreenRecorder:
    def __init__(self, output_path: str = None, start_delay: float = 0.5):
        self._output_path = output_path
        self._start_delay = start_delay
        self._record_thread = None
        self._mouse_track_thread = None
        self._moues_events = {'move': [], 'click': []}
        self._writer = None
        self._frame_index = 0
        self._frame_width = None
        self._frame_height = None
        self._is_stopped = Event()
        self._is_stopped.set()
        self._fps = 25
        self._maximum_fps = 200
        self._stream = ScreenGear().start()  # Initialize the screen capture stream

    def set_output(self, output_path: str):
        """Sets the output path for the recording."""
        self._output_path = output_path

    def start_recording(self):
        """Starts the recording and mouse tracking in separate threads."""
        if not self._output_path:
            raise ValueError("Output path is not specified")

        self._is_stopped.clear()
        self._record_thread = Thread(target=self._recording)
        self._record_thread.start()

        self._mouse_track_thread = Thread(target=self._mouse_track)
        self._mouse_track_thread.start()

    def stop_recording(self):
        """Stops the recording and mouse tracking."""
        self._is_stopped.set()
        if self._record_thread is not None:
            self._record_thread.join()

        if self._mouse_track_thread is not None:
            self._mouse_track_thread.join()

    def cancel_recording(self):
        """Stops the recording and removes the output file if it exists."""
        self.stop_recording()
        if self._output_path and os.path.exists(self._output_path):
            os.remove(self._output_path)
            logger.info(f"Cancelled recording and removed file: {self._output_path}")

    @property
    def mouse_events(self):
        """Returns the mouse events data."""
        return self._moues_events

    def _recording(self):
        """Handles the recording of the screen."""
        try:
            time.sleep(self._start_delay)  # Delay before starting the recording

            interval = 1 / self._fps
            self._frame_index = 0
            while not self._is_stopped.is_set():
                t0 = time.time()
                frame = self._stream.read()
                if frame is None:
                    break

                frame_height, frame_width = frame.shape[:2]
                if self._writer is None:
                    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                    self._writer = cv2.VideoWriter(self._output_path, fourcc, self._fps, (frame_width, frame_height))
                    self._frame_width = frame_width
                    self._frame_height = frame_height

                self._frame_index += 1
                self._writer.write(frame)
                t1 = time.time()

                read_time = t1 - t0
                sleep_duration = max(0, interval - read_time)
                time.sleep(sleep_duration)

            logger.info(f"Recording saved as {self._output_path}")
        except Exception as e:
            logger.error(f"An error occurred during recording: {e}")
        finally:
            if self._writer is not None:
                self._writer.release()
                self._writer = None
            self._stream.stop()
            logger.info("Recording stopped")

    def _mouse_track(self):
        """Tracks mouse movements and clicks."""
        def on_move(x, y):
            """Handles mouse move events."""
            if self._frame_width is not None and self._frame_height is not None:
                relative_x = x / self._frame_width
                relative_y = y / self._frame_height
                self._moues_events['move'].append((relative_x, relative_y, self._frame_index))

        def on_click(x, y, button, pressed):
            """Handles mouse click events."""
            if pressed and self._frame_width is not None and self._frame_height is not None:
                relative_x = x / self._frame_width
                relative_y = y / self._frame_height
                self._moues_events['click'].append((relative_x, relative_y, self._frame_index))

        with Listener(on_move=on_move, on_click=on_click) as listener:
            while not self._is_stopped.is_set():
                self._is_stopped.wait()
            listener.stop()
            logger.info("Mouse listener stopped")
