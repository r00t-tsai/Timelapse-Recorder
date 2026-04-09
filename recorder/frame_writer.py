import os
import cv2
import numpy as np
from typing import Optional

FRAMES_TEMP_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frames_temp")

class FrameWriter:

    def __init__(self, frames_dir: str = FRAMES_TEMP_DIR,
                 frame_format: str = "PNG",
                 jpeg_quality: int = 90,
                 resolution_scale: float = 1.0):
        self.frames_dir = frames_dir
        self.frame_format = frame_format.upper()
        self.jpeg_quality = jpeg_quality
        self.resolution_scale = resolution_scale
        self._frame_count = 0

        os.makedirs(self.frames_dir, exist_ok=True)

    @property
    def frame_count(self) -> int:
        return self._frame_count

    def _scale_frame(self, frame: np.ndarray) -> np.ndarray:
        if self.resolution_scale == 1.0:
            return frame
        h, w = frame.shape[:2]
        new_w = max(1, int(w * self.resolution_scale))
        new_h = max(1, int(h * self.resolution_scale))
        return cv2.resize(frame, (new_w, new_h), interpolation=cv2.INTER_AREA)

    def write_frame(self, frame: np.ndarray) -> str:

        self._frame_count += 1
        frame = self._scale_frame(frame)

        ext = "png" if self.frame_format == "PNG" else "jpg"
        filename = f"frame_{self._frame_count:06d}.{ext}"
        filepath = os.path.join(self.frames_dir, filename)

        if self.frame_format == "PNG":
            cv2.imwrite(filepath, frame)
        else:
            cv2.imwrite(filepath, frame, [cv2.IMWRITE_JPEG_QUALITY, self.jpeg_quality])

        return filepath

    def reset(self):

        self._frame_count = 0