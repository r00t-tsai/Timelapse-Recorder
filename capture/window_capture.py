import numpy as np
import threading
from typing import Optional, List

try:
    import pygetwindow as gw
    HAS_PYGETWINDOW = True
except ImportError:
    HAS_PYGETWINDOW = False

import mss

class WindowCapture:

    def __init__(self, window_title: str):
        self.window_title = window_title

        self._local = threading.local()

    def _get_sct(self):
        if not hasattr(self._local, "sct"):
            self._local.sct = mss.mss()
        return self._local.sct

    @staticmethod
    def list_windows() -> List[str]:
        if not HAS_PYGETWINDOW:
            return ["[pygetwindow not installed]"]
        try:
            titles = [t for t in gw.getAllTitles() if t.strip()]
            return sorted(set(titles))
        except Exception as e:
            return [f"Error: {e}"]

    def _find_window(self):
        if not HAS_PYGETWINDOW:
            raise RuntimeError("pygetwindow is required for window capture. "
                               "Install it with: pip install pygetwindow")
        matches = gw.getWindowsWithTitle(self.window_title)
        if not matches:
            raise RuntimeError(f"No window found with title containing: '{self.window_title}'")
        return matches[0]

    def capture_frame(self) -> np.ndarray:
        sct = self._get_sct()
        win = self._find_window()

        left = win.left
        top = win.top
        width = win.width
        height = win.height

        if width <= 0 or height <= 0:
            raise RuntimeError(f"Window '{self.window_title}' has invalid dimensions.")

        region = {"top": top, "left": left, "width": width, "height": height}
        screenshot = sct.grab(region)
        frame = np.array(screenshot)
        return frame[:, :, :3]  

    def get_window_geometry(self) -> Optional[tuple]:
        try:
            win = self._find_window()
            return (win.left, win.top, win.width, win.height)
        except Exception:
            return None

    def close(self):
        if hasattr(self._local, "sct"):
            try:
                self._local.sct.close()
            except Exception:
                pass
            del self._local.sct

    def __del__(self):
        self.close()

