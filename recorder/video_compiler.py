import os
import cv2
import glob
import re
from typing import Callable, Optional

class VideoCompiler:

    def __init__(self, frames_dir: str, output_path: str,
                 fps: int = 24, codec: str = "mp4v"):

        self.frames_dir = frames_dir
        self.output_path = output_path
        self.fps = fps
        self.codec = codec

    def _get_sorted_frames(self):
        patterns = [
            os.path.join(self.frames_dir, "frame_*.png"),
            os.path.join(self.frames_dir, "frame_*.jpg"),
        ]
        frames = []
        for pattern in patterns:
            frames.extend(glob.glob(pattern))

        def sort_key(p):
            match = re.search(r"frame_(\d+)", os.path.basename(p))
            return int(match.group(1)) if match else 0

        return sorted(frames, key=sort_key)

    def compile(self, progress_callback: Optional[Callable[[int, int], None]] = None) -> str:

        frames = self._get_sorted_frames()
        if not frames:
            raise RuntimeError(f"No frames found in: {self.frames_dir}")

        first = cv2.imread(frames[0])
        if first is None:
            raise RuntimeError(f"Failed to read frame: {frames[0]}")

        h, w = first.shape[:2]
        fourcc = cv2.VideoWriter_fourcc(*self.codec)

        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
        writer = cv2.VideoWriter(self.output_path, fourcc, self.fps, (w, h))

        if not writer.isOpened():
            raise RuntimeError(
                f"Failed to open VideoWriter. Codec '{self.codec}' may not be supported."
            )

        total = len(frames)
        for i, frame_path in enumerate(frames):
            frame = cv2.imread(frame_path)
            if frame is None:
                continue

            if frame.shape[:2] != (h, w):
                frame = cv2.resize(frame, (w, h))
            writer.write(frame)
            if progress_callback:
                progress_callback(i + 1, total)

        writer.release()
        return self.output_path

    def estimate_duration(self, frame_count: int) -> float:
        return frame_count / self.fps if self.fps > 0 else 0

