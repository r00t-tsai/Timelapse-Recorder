import threading
import time
import os
import shutil
import glob
from typing import Callable, Optional

from config import TimelapseConfig
from capture.screen_capture import ScreenCapture
from capture.window_capture import WindowCapture
from recorder.frame_writer import FrameWriter, FRAMES_TEMP_DIR
from recorder.video_compiler import VideoCompiler

def unfinished_session() -> bool:
    if not os.path.isdir(FRAMES_TEMP_DIR):
        return False
    for pattern in [
        os.path.join(FRAMES_TEMP_DIR, "frame_*.png"),
        os.path.join(FRAMES_TEMP_DIR, "frame_*.jpg"),
    ]:
        if glob.glob(pattern):
            return True
    return False

class RecordingSession:

    STATUS_IDLE       = "idle"
    STATUS_RECORDING  = "recording"
    STATUS_PAUSED     = "paused"
    STATUS_COMPILING  = "compiling"
    STATUS_DONE       = "done"
    STATUS_ERROR      = "error"

    def __init__(self, config: TimelapseConfig,
                 on_frame: Optional[Callable[[int], None]] = None,
                 on_status: Optional[Callable[[str, str], None]] = None,
                 on_compile_progress: Optional[Callable[[int, int], None]] = None):
        self.config = config
        self.on_frame = on_frame
        self.on_status = on_status
        self.on_compile_progress = on_compile_progress

        self._status = self.STATUS_IDLE
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._pause_event = threading.Event()
        self._pause_event.set()

        self._capturer = None
        self._writer: Optional[FrameWriter] = None
        self._error_message = ""

    @property
    def status(self) -> str:
        return self._status

    @property
    def frame_count(self) -> int:
        return self._writer.frame_count if self._writer else 0

    @property
    def error_message(self) -> str:
        return self._error_message

    def _set_status(self, status: str, message: str = ""):
        self._status = status
        if self.on_status:
            self.on_status(status, message)

    def _build_capturer(self):
        cfg = self.config
        if cfg.capture_mode == "window" and cfg.target_window_title:
            return WindowCapture(cfg.target_window_title)
        return ScreenCapture(
            monitor_index=cfg.monitor_index,
            custom_region=cfg.custom_region,
        )

    def start(self):
        if self._status in (self.STATUS_RECORDING, self.STATUS_COMPILING):
            return

        os.makedirs(FRAMES_TEMP_DIR, exist_ok=True)

        self._stop_event.clear()
        self._pause_event.set()
        self._capturer = None

        self._writer = FrameWriter(
            frames_dir=FRAMES_TEMP_DIR,
            frame_format=self.config.frame_format,
            jpeg_quality=self.config.jpeg_quality,
            resolution_scale=self.config.resolution_scale,
        )

        self._thread = threading.Thread(target=self._capture_loop, daemon=True)
        self._thread.start()
        self._set_status(self.STATUS_RECORDING, "Recording started.")

    def pause(self):
        if self._status == self.STATUS_RECORDING:
            self._pause_event.clear()
            self._set_status(self.STATUS_PAUSED, "Recording paused.")

    def resume(self):
        if self._status == self.STATUS_PAUSED:
            self._pause_event.set()
            self._set_status(self.STATUS_RECORDING, "Recording resumed.")

    def stop(self, compile_video: bool = True):

        if self._status in (self.STATUS_IDLE, self.STATUS_DONE, self.STATUS_ERROR):
            return

        self._stop_event.set()
        self._pause_event.set()

        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=10)

        if self._capturer:
            try:
                self._capturer.close()
            except Exception:
                pass

        if compile_video and self._writer and self._writer.frame_count > 0:

            threading.Thread(target=self._compile, daemon=True).start()
        else:
            shutil.rmtree(FRAMES_TEMP_DIR, ignore_errors=True)
            self._set_status(self.STATUS_DONE, "Recording stopped.")

    def compile_leftovers_async(self):

        threading.Thread(target=self._compile, daemon=True).start()

    def delete_leftovers(self):

        shutil.rmtree(FRAMES_TEMP_DIR, ignore_errors=True)

    def _capture_loop(self):

        try:
            self._capturer = self._build_capturer()

            while not self._stop_event.is_set():
                self._pause_event.wait()

                if self._stop_event.is_set():
                    break

                frame = self._capturer.capture_frame()
                self._writer.write_frame(frame)

                if self.on_frame:
                    self.on_frame(self._writer.frame_count)

                if (self.config.max_frames > 0
                        and self._writer.frame_count >= self.config.max_frames):
                    self._set_status(
                        self.STATUS_DONE,
                        f"Max frames ({self.config.max_frames}) reached."
                    )
                    self._stop_event.set()
                    break

                self._interruptible_sleep(self.config.capture_interval_sec)

        except Exception as e:
            self._error_message = str(e)
            self._set_status(self.STATUS_ERROR, f"Capture error: {e}")

    def _interruptible_sleep(self, seconds: float):
        step = 0.1
        elapsed = 0.0
        while elapsed < seconds and not self._stop_event.is_set():
            time.sleep(min(step, seconds - elapsed))
            elapsed += step

    def _compile(self):

        self._set_status(self.STATUS_COMPILING, "Compiling video...")
        try:
            compiler = VideoCompiler(
                frames_dir=FRAMES_TEMP_DIR,
                output_path=self.config.video_path(),
                fps=self.config.output_fps,
                codec=self.config.video_codec,
            )
            output = compiler.compile(progress_callback=self.on_compile_progress)
            shutil.rmtree(FRAMES_TEMP_DIR, ignore_errors=True)
            self._set_status(self.STATUS_DONE, f"Video saved: {output}")
        except Exception as e:
            self._error_message = str(e)
            self._set_status(self.STATUS_ERROR, f"Compile error: {e}")