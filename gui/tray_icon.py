import os
import math
import threading
from typing import Callable, Optional

_HERE = os.path.dirname(os.path.abspath(__file__))
_ICO_PATH = os.path.join(_HERE, "ico.ico")

try:
    import pystray
    from pystray import MenuItem as Item, Menu
    HAS_PYSTRAY = True
except ImportError:
    HAS_PYSTRAY = False

try:
    from PIL import Image, ImageDraw
    HAS_PILLOW = True
except ImportError:
    HAS_PILLOW = False

def _make_fallback_icon(size: int = 64, recording: bool = False) -> "Image.Image":

    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    pad = 2
    draw.ellipse([pad, pad, size - pad, size - pad],
                 fill="#fff0f5", outline="#e75480", width=3)

    inner_pad = size // 5
    draw.ellipse([inner_pad, inner_pad, size - inner_pad, size - inner_pad],
                 fill="#fde0ea", outline="#f4a0b5", width=2)

    dot_r = size // 8
    cx, cy = size // 2, size // 2
    dot_color = "#e75480" if recording else "#b07080"
    draw.ellipse([cx - dot_r, cy - dot_r, cx + dot_r, cy + dot_r],
                 fill=dot_color)

    tick_len = size // 10
    for angle_deg in [0, 120, 240]:
        angle = math.radians(angle_deg - 90)
        r_outer = size // 2 - pad - 4
        r_inner = r_outer - tick_len
        x1 = cx + r_inner * math.cos(angle)
        y1 = cy + r_inner * math.sin(angle)
        x2 = cx + r_outer * math.cos(angle)
        y2 = cy + r_outer * math.sin(angle)
        draw.line([x1, y1, x2, y2], fill="#e75480", width=2)

    return img


def _load_icon_image(size: int = 64, recording: bool = False) -> "Image.Image":

    if HAS_PILLOW:
        try:
            img = Image.open(_ICO_PATH).convert("RGBA").resize(
                (size, size), Image.LANCZOS)
            if recording:
                overlay = Image.new("RGBA", (size, size), (0, 0, 0, 0))
                d = ImageDraw.Draw(overlay)
                dot_r = size // 8
                cx, cy = size // 2, size // 2
                d.ellipse([cx - dot_r, cy - dot_r, cx + dot_r, cy + dot_r],
                          fill="#e75480")
                img = Image.alpha_composite(img, overlay)
            return img
        except Exception:
            pass
    return _make_fallback_icon(size=size, recording=recording)

class TrayIcon:

    def __init__(self,
                 app_title: str = "Timelapse Recorder",
                 on_show: Optional[Callable] = None,
                 on_quit: Optional[Callable] = None,
                 get_status: Optional[Callable[[], str]] = None):

        self.app_title  = app_title
        self.on_show    = on_show
        self.on_quit    = on_quit
        self.get_status = get_status

        self._icon: Optional["pystray.Icon"] = None
        self._thread: Optional[threading.Thread] = None
        self._recording = False

    @property
    def available(self) -> bool:
        return HAS_PYSTRAY and HAS_PILLOW

    def start(self):
        if not self.available:
            return
        if self._thread and self._thread.is_alive():
            return
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        if self._icon:
            try:
                self._icon.stop()
            except Exception:
                pass
            self._icon = None

    def set_recording(self, recording: bool):
        self._recording = recording
        if self._icon:
            try:
                self._icon.icon = _load_icon_image(recording=recording)
                self._icon.update_menu()
            except Exception:
                pass

    def show_notification(self, title: str, message: str):
        if self._icon:
            try:
                self._icon.notify(message, title)
            except Exception:
                pass

    def _run(self):
        menu = self._build_menu()
        image = _load_icon_image(recording=self._recording)
        self._icon = pystray.Icon(
            name="timelapse_recorder",
            icon=image,
            title=self.app_title,
            menu=menu,
        )
        self._icon.run(setup=lambda icon: setattr(icon, "visible", True))

    def _build_menu(self) -> "Menu":
        items = []
        if self.get_status:
            items.append(Item(lambda _: self.get_status(), None, enabled=False))
            items.append(Menu.SEPARATOR)
        items.append(Item("Show Window", self._handle_show, default=True))
        items.append(Menu.SEPARATOR)
        items.append(Item("Quit", self._handle_quit))
        return Menu(*items)

    def _handle_show(self, icon=None, item=None):
        if self.on_show:
            self.on_show()

    def _handle_quit(self, icon=None, item=None):
        self.stop()
        if self.on_quit:
            self.on_quit()