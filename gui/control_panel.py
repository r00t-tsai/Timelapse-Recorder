import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional

BG       = "#fff8f9"
SEP      = "#f0b8c8"
PINK     = "#e75480"
ROSE     = "#f4a0b5"
ACCENT   = "#c93b6a"
BTN_BG   = "#f9dde6"
FG       = "#3d1a24"
FG_DIM   = "#b07080"

FONT      = ("Consolas", 9)
FONT_BOLD = ("Consolas", 9, "bold")

class ControlPanel(tk.Frame):
    def __init__(self, parent,
                 on_record: Callable,
                 on_pause: Callable,
                 on_stop: Callable,
                 **kwargs):
        super().__init__(parent, **kwargs)
        self.on_record  = on_record
        self.on_pause   = on_pause
        self.on_stop    = on_stop
        self._build_ui()

    def _build_ui(self):
        bg = self["bg"]

        tk.Frame(self, height=1, bg=SEP).pack(fill="x", pady=(0, 8))

        status_frame = tk.Frame(self, bg=bg)
        status_frame.pack(fill="x", padx=12)

        self._status_dot = tk.Label(status_frame, text="●",
                                    font=("Consolas", 14),
                                    fg=FG_DIM, bg=bg)
        self._status_dot.pack(side="left")

        self._status_label = tk.Label(status_frame, text="IDLE",
                                      font=FONT_BOLD, fg=FG_DIM, bg=bg)
        self._status_label.pack(side="left", padx=(4, 16))

        self._frame_label = tk.Label(status_frame, text="Frames: 0",
                                     font=FONT, fg=FG_DIM, bg=bg)
        self._frame_label.pack(side="left", padx=8)

        self._time_label = tk.Label(status_frame, text="",
                                    font=FONT, fg=FG_DIM, bg=bg)
        self._time_label.pack(side="left", padx=8)

        btn_frame = tk.Frame(self, bg=bg)
        btn_frame.pack(fill="x", padx=12, pady=8)

        btn_style = dict(font=FONT_BOLD, relief="flat",
                         bd=0, padx=14, pady=8, cursor="hand2")

        self._rec_btn = tk.Button(btn_frame, text="RECORD",
                                  bg="#e75480", fg="#ffffff",
                                  activebackground="#c93b6a",
                                  command=self.on_record, **btn_style)
        self._rec_btn.pack(side="left", padx=(0, 6))

        self._pause_btn = tk.Button(btn_frame, text="PAUSE",
                                    bg=BTN_BG, fg=ACCENT,
                                    activebackground=ROSE,
                                    command=self.on_pause, state="disabled",
                                    **btn_style)
        self._pause_btn.pack(side="left", padx=6)

        self._stop_btn = tk.Button(btn_frame, text="STOP",
                                   bg=BTN_BG, fg=ACCENT,
                                   activebackground=ROSE,
                                   command=self.on_stop, state="disabled",
                                   **btn_style)
        self._stop_btn.pack(side="left", padx=6)

        style = ttk.Style()
        style.configure("Pink.Horizontal.TProgressbar",
                        troughcolor=BTN_BG, background=PINK,
                        bordercolor=ROSE, lightcolor=ROSE, darkcolor=ACCENT)

        self._progress_var = tk.DoubleVar(value=0)
        self._progress = ttk.Progressbar(self,
                                         style="Pink.Horizontal.TProgressbar",
                                         variable=self._progress_var,
                                         maximum=100, length=400,
                                         mode="determinate")
        self._progress_label = tk.Label(self, text="",
                                        font=("Consolas", 8),
                                        fg=ACCENT, bg=bg)

    def set_recording(self):
        self._rec_btn.config(state="disabled", bg=ROSE)
        self._pause_btn.config(state="normal")
        self._stop_btn.config(state="normal")
        self._set_dot(PINK)
        self._status_label.config(text="RECORDING", fg=PINK)
        self._hide_progress()

    def set_paused(self):
        self._pause_btn.config(text="RESUME")
        self._set_dot("#f39c12")
        self._status_label.config(text="PAUSED", fg="#d68910")

    def set_resumed(self):
        self._pause_btn.config(text="PAUSE")
        self._set_dot(PINK)
        self._status_label.config(text="RECORDING", fg=PINK)

    def set_idle(self):
        self._rec_btn.config(state="normal", bg=PINK)
        self._pause_btn.config(state="disabled", text="PAUSE")
        self._stop_btn.config(state="disabled")
        self._set_dot(FG_DIM)
        self._status_label.config(text="IDLE", fg=FG_DIM)

    def set_done(self, message: str = ""):
        self._rec_btn.config(state="normal", bg=PINK)
        self._pause_btn.config(state="disabled", text="PAUSE")
        self._stop_btn.config(state="disabled")
        self._set_dot("#27ae60")
        self._status_label.config(text="DONE", fg="#27ae60")
        self._hide_progress()

    def set_error(self, message: str = ""):
        self.set_idle()
        self._set_dot("#c0392b")
        self._status_label.config(text="ERROR", fg="#c0392b")

    def set_compiling(self):
        self._set_dot(ACCENT)
        self._status_label.config(text="COMPILING", fg=ACCENT)
        self._show_progress()

    def update_frame_count(self, count: int):
        self._frame_label.config(text=f"Frames: {count}")

    def update_elapsed(self, elapsed_sec: float):
        h = int(elapsed_sec // 3600)
        m = int((elapsed_sec % 3600) // 60)
        s = int(elapsed_sec % 60)
        self._time_label.config(text=f"{h:02d}:{m:02d}:{s:02d}")

    def update_compile_progress(self, current: int, total: int):
        pct = (current / total * 100) if total > 0 else 0
        self._progress_var.set(pct)
        self._progress_label.config(
            text=f"Compiling frame {current}/{total}  ({pct:.0f}%)")

    def _set_dot(self, color: str):
        self._status_dot.config(fg=color)

    def _show_progress(self):
        self._progress.pack(fill="x", padx=12, pady=(0, 2))
        self._progress_label.pack(padx=12, pady=(0, 6))

    def _hide_progress(self):
        self._progress.pack_forget()
        self._progress_label.pack_forget()
        self._progress_var.set(0)