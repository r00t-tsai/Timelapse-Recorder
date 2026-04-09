import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import Callable, Optional

from config import TimelapseConfig
from capture.window_capture import WindowCapture

class SettingsPanel(tk.Frame):

    def __init__(self, parent, config: TimelapseConfig,
                 on_config_change: Optional[Callable] = None, **kwargs):
        super().__init__(parent, **kwargs)
        self.config = config
        self.on_config_change = on_config_change

        self._vars = {}
        self._build_ui()

    def _section_label(self, text: str, row: int):
        lbl = tk.Label(self, text=text, font=("Consolas", 9, "bold"),
                       fg="#7dd3c8", bg=self["bg"], anchor="w")
        lbl.grid(row=row, column=0, columnspan=3, sticky="w", padx=8, pady=(10, 2))

    def _row_label(self, text: str, row: int, col: int = 0):
        lbl = tk.Label(self, text=text, font=("Consolas", 9),
                       fg="#c8d8e0", bg=self["bg"], anchor="e")
        lbl.grid(row=row, column=col, sticky="e", padx=(8, 4), pady=2)
        return lbl

    def _build_ui(self):
        bg = self["bg"]
        self.columnconfigure(1, weight=1)

        row = 0

        self._section_label("[ CAPTURE ]", row); row += 1

        self._row_label("Mode:", row)
        self._vars["capture_mode"] = tk.StringVar(value=self.config.capture_mode)
        mode_frame = tk.Frame(self, bg=bg)
        mode_frame.grid(row=row, column=1, sticky="w")
        for text, val in [("Full Screen", "fullscreen"), ("Window", "window")]:
            rb = tk.Radiobutton(mode_frame, text=text, variable=self._vars["capture_mode"],
                                value=val, bg=bg, fg="#c8d8e0",
                                selectcolor="#1e3040", activebackground=bg,
                                font=("Consolas", 9), command=self._toggle_window_field)
            rb.pack(side="left", padx=4)
        row += 1

        self._row_label("Window Title:", row)
        self._vars["target_window_title"] = tk.StringVar(
            value=self.config.target_window_title or "")
        self._window_entry = tk.Entry(self, textvariable=self._vars["target_window_title"],
                                      font=("Consolas", 9), width=28,
                                      bg="#0f1e2a", fg="#e0f0ff",
                                      insertbackground="#7dd3c8",
                                      disabledbackground="#0a141e",
                                      disabledforeground="#3a5060")
        self._window_entry.grid(row=row, column=1, sticky="w", pady=2)
        win_btn = tk.Button(self, text="Pick", font=("Consolas", 8),
                            bg="#1e3040", fg="#7dd3c8",
                            activebackground="#2a4555", cursor="hand2",
                            relief="flat", bd=0, padx=6,
                            command=self._pick_window)
        win_btn.grid(row=row, column=2, padx=(4, 8), sticky="w")
        row += 1

        self._row_label("Monitor:", row)
        self._vars["monitor_index"] = tk.IntVar(value=self.config.monitor_index)
        monitor_spin = tk.Spinbox(self, from_=1, to=8,
                                  textvariable=self._vars["monitor_index"],
                                  font=("Consolas", 9), width=4,
                                  bg="#0f1e2a", fg="#e0f0ff",
                                  buttonbackground="#1e3040",
                                  insertbackground="#7dd3c8", relief="flat")
        monitor_spin.grid(row=row, column=1, sticky="w", pady=2)
        row += 1

        self._row_label("Interval (sec):", row)
        self._vars["capture_interval_sec"] = tk.DoubleVar(value=self.config.capture_interval_sec)
        interval_spin = tk.Spinbox(self, from_=0.5, to=3600, increment=0.5,
                                   textvariable=self._vars["capture_interval_sec"],
                                   format="%.1f", font=("Consolas", 9), width=8,
                                   bg="#0f1e2a", fg="#e0f0ff",
                                   buttonbackground="#1e3040",
                                   insertbackground="#7dd3c8", relief="flat")
        interval_spin.grid(row=row, column=1, sticky="w", pady=2)
        row += 1

        self._row_label("Max Frames:", row)
        self._vars["max_frames"] = tk.IntVar(value=self.config.max_frames)
        max_frame_spin = tk.Spinbox(self, from_=0, to=999999, increment=100,
                                    textvariable=self._vars["max_frames"],
                                    font=("Consolas", 9), width=8,
                                    bg="#0f1e2a", fg="#e0f0ff",
                                    buttonbackground="#1e3040",
                                    insertbackground="#7dd3c8", relief="flat")
        max_frame_spin.grid(row=row, column=1, sticky="w", pady=2)
        tk.Label(self, text="(0 = unlimited)", font=("Consolas", 8),
                 fg="#5a7a8a", bg=bg).grid(row=row, column=2, sticky="w")
        row += 1

        self._section_label("[ OUTPUT ]", row); row += 1

        self._row_label("Output Dir:", row)
        self._vars["output_dir"] = tk.StringVar(value=self.config.output_dir)
        dir_entry = tk.Entry(self, textvariable=self._vars["output_dir"],
                             font=("Consolas", 9), width=26,
                             bg="#0f1e2a", fg="#e0f0ff",
                             insertbackground="#7dd3c8", relief="flat")
        dir_entry.grid(row=row, column=1, sticky="ew", pady=2)
        tk.Button(self, text="Browse", font=("Consolas", 8),
                  bg="#1e3040", fg="#7dd3c8", activebackground="#2a4555",
                  cursor="hand2", relief="flat", bd=0, padx=6,
                  command=self._browse_output_dir
                  ).grid(row=row, column=2, padx=(4, 8), sticky="w")
        row += 1

        self._row_label("Filename:", row)
        self._vars["output_filename"] = tk.StringVar(value=self.config.output_filename)
        tk.Entry(self, textvariable=self._vars["output_filename"],
                 font=("Consolas", 9), width=26,
                 bg="#0f1e2a", fg="#e0f0ff",
                 insertbackground="#7dd3c8", relief="flat"
                 ).grid(row=row, column=1, sticky="ew", pady=2)
        row += 1

        self._section_label("[ VIDEO ]", row); row += 1

        self._row_label("Playback FPS:", row)
        self._vars["output_fps"] = tk.IntVar(value=self.config.output_fps)
        fps_spin = tk.Spinbox(self, from_=1, to=120, increment=1,
                              textvariable=self._vars["output_fps"],
                              font=("Consolas", 9), width=6,
                              bg="#0f1e2a", fg="#e0f0ff",
                              buttonbackground="#1e3040",
                              insertbackground="#7dd3c8", relief="flat")
        fps_spin.grid(row=row, column=1, sticky="w", pady=2)
        row += 1

        self._row_label("Codec:", row)
        self._vars["video_codec"] = tk.StringVar(value=self.config.video_codec)
        codec_combo = ttk.Combobox(self, textvariable=self._vars["video_codec"],
                                   values=["mp4v", "avc1", "XVID", "MJPG"],
                                   font=("Consolas", 9), width=8, state="readonly")
        codec_combo.grid(row=row, column=1, sticky="w", pady=2)
        row += 1

        self._row_label("Resolution Scale:", row)
        self._vars["resolution_scale"] = tk.DoubleVar(value=self.config.resolution_scale)
        scale_combo = ttk.Combobox(self, textvariable=self._vars["resolution_scale"],
                                   values=[0.25, 0.5, 0.75, 1.0],
                                   font=("Consolas", 9), width=6, state="readonly")
        scale_combo.grid(row=row, column=1, sticky="w", pady=2)
        row += 1

        self._section_label("[ FRAME STORAGE ]", row); row += 1

        self._row_label("Frame Format:", row)
        self._vars["frame_format"] = tk.StringVar(value=self.config.frame_format)
        fmt_frame = tk.Frame(self, bg=bg)
        fmt_frame.grid(row=row, column=1, sticky="w")
        for fmt in ["PNG", "JPEG"]:
            tk.Radiobutton(fmt_frame, text=fmt,
                           variable=self._vars["frame_format"],
                           value=fmt, bg=bg, fg="#c8d8e0",
                           selectcolor="#1e3040", activebackground=bg,
                           font=("Consolas", 9),
                           command=self._toggle_jpeg_quality).pack(side="left", padx=4)
        row += 1

        self._row_label("JPEG Quality:", row)
        self._vars["jpeg_quality"] = tk.IntVar(value=self.config.jpeg_quality)
        self._jpeg_spin = tk.Spinbox(self, from_=1, to=100, increment=5,
                                     textvariable=self._vars["jpeg_quality"],
                                     font=("Consolas", 9), width=6,
                                     bg="#0f1e2a", fg="#e0f0ff",
                                     buttonbackground="#1e3040",
                                     insertbackground="#7dd3c8", relief="flat")
        self._jpeg_spin.grid(row=row, column=1, sticky="w", pady=2)
        row += 1

        self._row_label("Keep Frames:", row)
        self._vars["save_frames"] = tk.BooleanVar(value=self.config.save_frames)
        tk.Checkbutton(self, variable=self._vars["save_frames"],
                       bg=bg, fg="#c8d8e0", selectcolor="#1e3040",
                       activebackground=bg, font=("Consolas", 9)
                       ).grid(row=row, column=1, sticky="w", pady=2)
        row += 1

        self._row_label("Auto-Compile:", row)
        self._vars["auto_compile"] = tk.BooleanVar(value=self.config.auto_compile)
        tk.Checkbutton(self, variable=self._vars["auto_compile"],
                       bg=bg, fg="#c8d8e0", selectcolor="#1e3040",
                       activebackground=bg, font=("Consolas", 9)
                       ).grid(row=row, column=1, sticky="w", pady=2)
        row += 1

        tk.Button(self, text="▶  APPLY SETTINGS",
                  font=("Consolas", 10, "bold"),
                  bg="#0d6e6e", fg="#e0ffff",
                  activebackground="#0f9090",
                  cursor="hand2", relief="flat", bd=0,
                  padx=12, pady=6,
                  command=self.apply_to_config
                  ).grid(row=row, column=0, columnspan=3, pady=(14, 6), padx=8, sticky="ew")

        self._toggle_window_field()
        self._toggle_jpeg_quality()

    def _toggle_window_field(self):
        mode = self._vars["capture_mode"].get()
        state = "normal" if mode == "window" else "disabled"
        self._window_entry.config(state=state)

    def _toggle_jpeg_quality(self):
        fmt = self._vars["frame_format"].get()
        state = "normal" if fmt == "JPEG" else "disabled"
        self._jpeg_spin.config(state=state)

    def _pick_window(self):
        titles = WindowCapture.list_windows()
        if not titles:
            messagebox.showinfo("No Windows", "No open windows found.")
            return

        win = tk.Toplevel(self)
        win.title("Select Window")
        win.configure(bg="#0a141e")
        win.resizable(False, True)

        tk.Label(win, text="Select a window to capture:",
                 font=("Consolas", 9), fg="#7dd3c8", bg="#0a141e"
                 ).pack(padx=12, pady=(10, 4), anchor="w")

        listbox = tk.Listbox(win, font=("Consolas", 9),
                             bg="#0f1e2a", fg="#c8d8e0",
                             selectbackground="#0d6e6e",
                             activestyle="none", width=60, height=15)
        listbox.pack(padx=12, pady=4, fill="both", expand=True)
        for t in titles:
            listbox.insert("end", t)

        def confirm():
            sel = listbox.curselection()
            if sel:
                self._vars["target_window_title"].set(titles[sel[0]])
                self._vars["capture_mode"].set("window")
                self._toggle_window_field()
            win.destroy()

        tk.Button(win, text="Select", font=("Consolas", 9, "bold"),
                  bg="#0d6e6e", fg="#e0ffff", relief="flat", cursor="hand2",
                  command=confirm).pack(pady=(4, 10))

    def _browse_output_dir(self):
        d = filedialog.askdirectory(title="Choose Output Directory")
        if d:
            self._vars["output_dir"].set(d)

    def apply_to_config(self):
        cfg = self.config
        cfg.capture_mode = self._vars["capture_mode"].get()
        cfg.target_window_title = self._vars["target_window_title"].get() or None
        cfg.monitor_index = self._vars["monitor_index"].get()
        cfg.capture_interval_sec = self._vars["capture_interval_sec"].get()
        cfg.max_frames = self._vars["max_frames"].get()
        cfg.output_dir = self._vars["output_dir"].get()
        cfg.output_filename = self._vars["output_filename"].get()
        cfg.output_fps = self._vars["output_fps"].get()
        cfg.video_codec = self._vars["video_codec"].get()
        cfg.resolution_scale = self._vars["resolution_scale"].get()
        cfg.frame_format = self._vars["frame_format"].get()
        cfg.jpeg_quality = self._vars["jpeg_quality"].get()
        cfg.save_frames = self._vars["save_frames"].get()
        cfg.auto_compile = self._vars["auto_compile"].get()

        if self.on_config_change:
            self.on_config_change(cfg)

