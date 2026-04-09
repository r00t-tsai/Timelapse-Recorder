import numpy as np
import threading
from typing import Optional, Tuple
import mss
import mss.tools

class ScreenCapture:

    def __init__(self, monitor_index: int = 1,
                 custom_region: Optional[Tuple[int, int, int, int]] = None):

        self.monitor_index = monitor_index
        self.custom_region = custom_region

        self._local = threading.local()

    def _get_sct(self):
        if not hasattr(self._local, "sct"):
            self._local.sct = mss.mss()
        return self._local.sct

    def get_monitors(self):
        return self._get_sct().monitors[1:]  

    def capture_frame(self) -> np.ndarray:

        sct = self._get_sct()
        monitors = sct.monitors
        if self.monitor_index >= len(monitors):
            monitor = monitors[1]
        else:
            monitor = monitors[self.monitor_index]

        if self.custom_region:
            x, y, w, h = self.custom_region
            region = {
                "top": monitor["top"] + y,
                "left": monitor["left"] + x,
                "width": w,
                "height": h,
            }
        else:
            region = monitor

        screenshot = sct.grab(region)

        frame = np.array(screenshot)
        return frame[:, :, :3]  

    def close(self):
        if hasattr(self._local, "sct"):
            try:
                self._local.sct.close()
            except Exception:
                pass
            del self._local.sct

    def __del__(self):
        self.close()

