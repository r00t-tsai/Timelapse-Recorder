import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import time
import os

from config import TimelapseConfig
from recorder.session import RecordingSession, unfinished_session
from recorder.frame_writer import FRAMES_TEMP_DIR
from gui.control_panel import ControlPanel
from capture.window_capture import WindowCapture

try:
    import pystray
    from PIL import Image, ImageDraw
    HAS_TRAY = True
except ImportError:
    HAS_TRAY = False

_HERE     = os.path.dirname(os.path.abspath(__file__))
_ICO_PATH = os.path.join(_HERE, "ico.ico")

def _make_tray_icon_image(size: int = 64) -> "Image.Image":
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse([2, 2, size - 2, size - 2], fill="#fff0f5", outline="#e75480", width=3)
    pad = size // 5
    d.ellipse([pad, pad, size - pad, size - pad], fill="#e75480")
    return img

def _load_tray_image() -> "Image.Image":
    if HAS_TRAY:
        try:
            img = Image.open(_ICO_PATH)
            img = img.convert("RGBA")
            img = img.resize((64, 64), Image.LANCZOS)
            return img
        except Exception:
            pass
    return _make_tray_icon_image()

BG       = "#fff8f9"   
BG_TAB   = "#fdf0f4"   
BG_FIELD = "#ffffff"   
FG       = "#3d1a24"   
FG_DIM   = "#b07080"   
PINK     = "#e75480"   
ROSE     = "#f4a0b5"   
ACCENT   = "#c93b6a"   
BTN_BG   = "#f9dde6"   
SEP      = "#f0b8c8"   
FONT      = ("Consolas", 9)
FONT_BOLD = ("Consolas", 9, "bold")

def _field_entry(parent, textvariable, width=26, **kw):
    return tk.Entry(parent, textvariable=textvariable, font=FONT,
                    width=width, bg=BG_FIELD, fg=FG,
                    insertbackground=PINK, relief="flat",
                    highlightthickness=1, highlightbackground=ROSE,
                    highlightcolor=PINK, **kw)

def _spinbox(parent, textvariable, from_, to, increment=1, fmt=None, width=8):
    kw = dict(from_=from_, to=to, increment=increment,
              textvariable=textvariable, font=FONT, width=width,
              bg=BG_FIELD, fg=FG, buttonbackground=BTN_BG,
              insertbackground=PINK, relief="flat")
    if fmt:
        kw["format"] = fmt
    return tk.Spinbox(parent, **kw)

def _radio_row(parent, variable, choices, command=None):
    f = tk.Frame(parent, bg=BG_TAB)
    for text, val in choices:
        rb = tk.Radiobutton(f, text=text, variable=variable, value=val,
                            bg=BG_TAB, fg=FG, selectcolor=BTN_BG,
                            activebackground=BG_TAB, font=FONT,
                            command=command)
        rb.pack(side="left", padx=4)
    return f

def _small_btn(parent, text, command):
    return tk.Button(parent, text=text, font=("Consolas", 8),
                     bg=BTN_BG, fg=ACCENT, activebackground=ROSE,
                     cursor="hand2", relief="flat", bd=0, padx=6,
                     command=command)

class _TabFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG_TAB, padx=16, pady=12)
        self.columnconfigure(1, weight=1)
        self._row = 0

    def row(self):
        r = self._row; self._row += 1; return r

    def section(self, text):
        r = self.row()
        tk.Label(self, text=text, font=FONT_BOLD, fg=PINK,
                 bg=BG_TAB, anchor="w").grid(
            row=r, column=0, columnspan=3, sticky="w", pady=(10, 4))

    def label(self, text, row):
        tk.Label(self, text=text, font=FONT, fg=FG,
                 bg=BG_TAB, anchor="e").grid(
            row=row, column=0, sticky="e", padx=(0, 8), pady=3)

    def place(self, widget, row, col=1, sticky="w", colspan=1, **kw):
        widget.grid(row=row, column=col, columnspan=colspan,
                    sticky=sticky, pady=3, **kw)

class TimelapseApp:
    APP_TITLE = "TIMELAPSE Recorder"

    def __init__(self, root: tk.Tk):
        self.root = root
        self.config = TimelapseConfig()
        self._session: RecordingSession = None
        self._paused = False
        self._start_time: float = None
        self._elapsed_sec: float = 0
        self._timer_running = False
        self._tray_icon = None
        self._tray_thread = None
        self._vars: dict = {}

        self._build_window()
        self._build_ui()

        self.root.after(100, self._startup_leftover_check)

    def _build_window(self):
        self.root.title(self.APP_TITLE)
        self.root.configure(bg=BG)
        self.root.resizable(False, False)
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

        try:
            self.root.iconbitmap(_ICO_PATH)
        except Exception:
            pass

        self.root.bind("<Unmap>", self._on_unmap)

        w, h = 560, 560
        sw, sh = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        self.root.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")

    def _on_unmap(self, event):

        if event.widget is not self.root:
            return
        is_recording = (
            self._session is not None
            and self._session.status == RecordingSession.STATUS_RECORDING
        )
        if is_recording:

            self.root.after(0, self._go_to_tray)

    def _go_to_tray(self):
        if not HAS_TRAY:
            return  

        self.root.withdraw()
        self._ensure_tray_running()

    def _ensure_tray_running(self):
        if self._tray_icon is not None:
            return  

        menu = pystray.Menu(
            pystray.MenuItem("Show Recorder", self._restore_from_tray, default=True),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Stop & Quit", self._tray_quit),
        )
        self._tray_icon = pystray.Icon(
            "timelapse_recorder",
            _load_tray_image(),
            "Timelapse Recorder — recording…",
            menu,
        )

        def _run():
            self._tray_icon.run_detached()
            try:
                self._tray_icon.notify(
                    "Timelapse Recorder is recording.\n"
                    "Click this icon to restore the window.",
                    "Recording in background",
                )
            except Exception:
                pass

        self._tray_thread = threading.Thread(target=_run, daemon=True)
        self._tray_thread.start()

    def _build_ui(self):
        self._build_header()
        self._build_notebook()
        self._build_apply_btn()
        tk.Frame(self.root, height=1, bg=SEP).pack(fill="x")
        self._build_control_panel()

    def _build_header(self):
        hdr = tk.Frame(self.root, bg=BG)
        hdr.pack(fill="x")
        tk.Label(hdr, text="TIMELAPSE", font=("Consolas", 18, "bold"),
                 fg=PINK, bg=BG).pack(side="left", padx=16, pady=12)
        tk.Label(hdr, text="Recorder", font=("Consolas", 18),
                 fg=ROSE, bg=BG).pack(side="left")
        tk.Label(hdr, text="by Zhai", font=("Consolas", 8),
                 fg=FG_DIM, bg=BG).pack(side="right", padx=14)
        tk.Frame(self.root, height=2, bg=PINK).pack(fill="x")

    def _build_notebook(self):
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Pink.TNotebook",
                        background=BG, borderwidth=0, tabmargins=[0, 4, 0, 0])
        style.configure("Pink.TNotebook.Tab",
                        background=BTN_BG, foreground=FG_DIM,
                        font=FONT_BOLD, padding=[14, 6], borderwidth=0)
        style.map("Pink.TNotebook.Tab",
                  background=[("selected", ACCENT), ("active", ROSE)],
                  foreground=[("selected", "#ffffff"), ("active", FG)])

        style.configure("TCombobox",
                        fieldbackground=BG_FIELD, background=BTN_BG,
                        foreground=FG, arrowcolor=PINK)

        self._notebook = ttk.Notebook(self.root, style="Pink.TNotebook")
        self._notebook.pack(fill="both", expand=True)

        self._tab_capture = _TabFrame(self._notebook)
        self._tab_output  = _TabFrame(self._notebook)
        self._tab_video   = _TabFrame(self._notebook)
        self._tab_frames  = _TabFrame(self._notebook)

        self._notebook.add(self._tab_capture, text="  Capture  ")
        self._notebook.add(self._tab_output,  text="  Output   ")
        self._notebook.add(self._tab_video,   text="   Video   ")
        self._notebook.add(self._tab_frames,  text="  Frames   ")

        self._build_tab_capture()
        self._build_tab_output()
        self._build_tab_video()
        self._build_tab_frames()

    def _build_tab_capture(self):
        t = self._tab_capture
        t.section("Capture Source")

        self._vars["capture_mode"] = tk.StringVar(value=self.config.capture_mode)
        r = t.row(); t.label("Mode:", r)
        t.place(_radio_row(t, self._vars["capture_mode"],
                           [("Full Screen", "fullscreen"), ("Window", "window")],
                           command=self._toggle_window_field), r)

        self._vars["target_window_title"] = tk.StringVar(
            value=self.config.target_window_title or "")
        r = t.row(); t.label("Window Title:", r)
        row_frame = tk.Frame(t, bg=BG_TAB)
        self._window_entry = _field_entry(row_frame,
                                          self._vars["target_window_title"], width=24)
        self._window_entry.pack(side="left")
        _small_btn(row_frame, "Select", self._pick_window).pack(side="left", padx=(6, 0))
        t.place(row_frame, r)

        self._vars["monitor_index"] = tk.IntVar(value=self.config.monitor_index)
        r = t.row(); t.label("Monitor:", r)
        t.place(_spinbox(t, self._vars["monitor_index"], 1, 8, width=4), r)

        t.section("Timing")

        self._vars["capture_interval_sec"] = tk.DoubleVar(
            value=self.config.capture_interval_sec)
        r = t.row(); t.label("Interval (sec):", r)
        t.place(_spinbox(t, self._vars["capture_interval_sec"],
                         0.5, 3600, increment=0.5, fmt="%.1f"), r)

        self._vars["max_frames"] = tk.IntVar(value=self.config.max_frames)
        r = t.row(); t.label("Max Frames:", r)
        mf_frame = tk.Frame(t, bg=BG_TAB)
        _spinbox(mf_frame, self._vars["max_frames"], 0, 999999,
                 increment=100).pack(side="left")
        tk.Label(mf_frame, text="  (0 = unlimited)", font=FONT,
                 fg=FG_DIM, bg=BG_TAB).pack(side="left")
        t.place(mf_frame, r)

        self._toggle_window_field()

    def _build_tab_output(self):
        t = self._tab_output
        t.section("File Destination")

        self._vars["output_dir"] = tk.StringVar(value=self.config.output_dir)
        r = t.row(); t.label("Output Dir:", r)
        od_frame = tk.Frame(t, bg=BG_TAB)
        _field_entry(od_frame, self._vars["output_dir"], width=22).pack(side="left")
        _small_btn(od_frame, "Browse", self._browse_output_dir).pack(
            side="left", padx=(6, 0))
        t.place(od_frame, r)

        self._vars["output_filename"] = tk.StringVar(value=self.config.output_filename)
        r = t.row(); t.label("Filename:", r)
        t.place(_field_entry(t, self._vars["output_filename"]), r)

    def _build_tab_video(self):
        t = self._tab_video
        t.section("Encoding")

        self._vars["output_fps"] = tk.IntVar(value=self.config.output_fps)
        r = t.row(); t.label("Playback FPS:", r)
        fps_frame = tk.Frame(t, bg=BG_TAB)
        _spinbox(fps_frame, self._vars["output_fps"], 1, 120, width=6).pack(side="left")
        tk.Label(fps_frame, text="  frames/sec in final video",
                 font=FONT, fg=FG_DIM, bg=BG_TAB).pack(side="left")
        t.place(fps_frame, r)

        self._vars["video_codec"] = tk.StringVar(value=self.config.video_codec)
        r = t.row(); t.label("Codec:", r)
        codec_combo = ttk.Combobox(t, textvariable=self._vars["video_codec"],
                                   values=["mp4v", "avc1", "XVID", "MJPG"],
                                   font=FONT, width=8, state="readonly")
        t.place(codec_combo, r)

        t.section("Resolution")

        self._vars["resolution_scale"] = tk.DoubleVar(value=self.config.resolution_scale)
        r = t.row(); t.label("Scale Factor:", r)
        scale_frame = tk.Frame(t, bg=BG_TAB)
        scale_combo = ttk.Combobox(scale_frame,
                                   textvariable=self._vars["resolution_scale"],
                                   values=[0.25, 0.5, 0.75, 1.0],
                                   font=FONT, width=6, state="readonly")
        scale_combo.pack(side="left")
        tk.Label(scale_frame, text="  (1.0 = full resolution)",
                 font=FONT, fg=FG_DIM, bg=BG_TAB).pack(side="left")
        t.place(scale_frame, r)

    def _build_tab_frames(self):
        t = self._tab_frames
        t.section("Image Format")

        self._vars["frame_format"] = tk.StringVar(value=self.config.frame_format)
        r = t.row(); t.label("Format:", r)
        t.place(_radio_row(t, self._vars["frame_format"],
                           [("PNG  (lossless)", "PNG"), ("JPEG  (smaller)", "JPEG")],
                           command=self._toggle_jpeg_quality), r)

        self._vars["jpeg_quality"] = tk.IntVar(value=self.config.jpeg_quality)
        r = t.row(); t.label("JPEG Quality:", r)
        jq_frame = tk.Frame(t, bg=BG_TAB)
        self._jpeg_spin = _spinbox(jq_frame, self._vars["jpeg_quality"],
                                   1, 100, increment=5, width=6)
        self._jpeg_spin.pack(side="left")
        tk.Label(jq_frame, text="  (1–100, only for JPEG)",
                 font=FONT, fg=FG_DIM, bg=BG_TAB).pack(side="left")
        t.place(jq_frame, r)

        self._toggle_jpeg_quality()

    def _build_apply_btn(self):
        btn_frame = tk.Frame(self.root, bg=BG, pady=6)
        btn_frame.pack(fill="x", padx=16)
        tk.Button(btn_frame, text="APPLY SETTINGS",
                  font=("Consolas", 10, "bold"),
                  bg=ACCENT, fg="#ffffff", activebackground=PINK,
                  cursor="hand2", relief="flat", bd=0,
                  padx=12, pady=7,
                  command=self._apply_settings).pack(fill="x")

    def _build_control_panel(self):
        self._control_panel = ControlPanel(
            self.root,
            on_record=self._on_record,
            on_pause=self._on_pause,
            on_stop=self._on_stop,
            bg=BG,
        )
        self._control_panel.pack(fill="x", side="bottom")

    def _toggle_window_field(self):
        mode = self._vars["capture_mode"].get()
        self._window_entry.config(state="normal" if mode == "window" else "disabled")

    def _toggle_jpeg_quality(self):
        fmt = self._vars["frame_format"].get()
        self._jpeg_spin.config(state="normal" if fmt == "JPEG" else "disabled")

    def _pick_window(self):
        titles = WindowCapture.list_windows()
        if not titles:
            messagebox.showinfo("No Windows", "No open windows found.")
            return
        win = tk.Toplevel(self.root)
        win.title("Select Window")
        win.configure(bg=BG)
        win.resizable(False, True)
        try:
            win.iconbitmap(_ICO_PATH)
        except Exception:
            pass
        tk.Label(win, text="Select a window to capture:",
                 font=FONT, fg=PINK, bg=BG).pack(padx=12, pady=(10, 4), anchor="w")
        lb = tk.Listbox(win, font=FONT, bg=BG_FIELD, fg=FG,
                        selectbackground=ACCENT, selectforeground="#ffffff",
                        activestyle="none", width=58, height=14)
        lb.pack(padx=12, pady=4, fill="both", expand=True)
        for t in titles:
            lb.insert("end", t)

        def confirm():
            sel = lb.curselection()
            if sel:
                self._vars["target_window_title"].set(titles[sel[0]])
                self._vars["capture_mode"].set("window")
                self._toggle_window_field()
            win.destroy()

        tk.Button(win, text="Select", font=FONT_BOLD,
                  bg=ACCENT, fg="#ffffff", activebackground=PINK,
                  relief="flat", cursor="hand2",
                  command=confirm).pack(pady=(4, 10))

    def _browse_output_dir(self):
        d = filedialog.askdirectory(title="Choose Output Directory")
        if d:
            self._vars["output_dir"].set(d)

    def _apply_settings(self):
        cfg = self.config
        cfg.capture_mode         = self._vars["capture_mode"].get()
        cfg.target_window_title  = self._vars["target_window_title"].get() or None
        cfg.monitor_index        = self._vars["monitor_index"].get()
        cfg.capture_interval_sec = self._vars["capture_interval_sec"].get()
        cfg.max_frames           = self._vars["max_frames"].get()
        cfg.output_dir           = self._vars["output_dir"].get()
        cfg.output_filename      = self._vars["output_filename"].get()
        cfg.output_fps           = self._vars["output_fps"].get()
        cfg.video_codec          = self._vars["video_codec"].get()
        cfg.resolution_scale     = self._vars["resolution_scale"].get()
        cfg.frame_format         = self._vars["frame_format"].get()
        cfg.jpeg_quality         = self._vars["jpeg_quality"].get()
        cfg.save_frames          = False
        cfg.auto_compile         = True

    def _startup_leftover_check(self):
        if not unfinished_session():
            return

        dialog = tk.Toplevel(self.root)
        dialog.title("Unfinished Session Detected")
        dialog.configure(bg=BG)
        dialog.resizable(False, False)
        dialog.grab_set()
        try:
            dialog.iconbitmap(_ICO_PATH)
        except Exception:
            pass

        dw, dh = 440, 150
        mw = self.root.winfo_x() + self.root.winfo_width() // 2
        mh = self.root.winfo_y() + self.root.winfo_height() // 2
        dialog.geometry(f"{dw}x{dh}+{mw - dw // 2}+{mh - dh // 2}")

        tk.Label(dialog,
                 text="Unfinished Session Detected",
                 font=("Consolas", 11, "bold"), fg="#c0392b", bg=BG
                 ).pack(pady=(20, 6))
        tk.Label(dialog,
                 text=(
                     "Data from previous recording were found.\n"
                     "What would you like to do with them?"
                 ),
                 font=FONT, fg=FG, bg=BG, justify="center"
                 ).pack(pady=(0, 18))

        btn_frame = tk.Frame(dialog, bg=BG)
        btn_frame.pack()

        def _compile():
            dialog.destroy()
            self._apply_settings()
            leftover_session = RecordingSession(
                config=self.config,
                on_status=self._on_session_status,
                on_compile_progress=self._on_compile_progress,
            )
            self._session = leftover_session
            self._control_panel.set_compiling()
            leftover_session.compile_leftovers_async()

        def _delete():
            dialog.destroy()
            import shutil
            shutil.rmtree(FRAMES_TEMP_DIR, ignore_errors=True)

        tk.Button(btn_frame, text="Compile to MP4",
                  font=FONT_BOLD, bg=ACCENT, fg="#ffffff",
                  activebackground=PINK, cursor="hand2",
                  relief="flat", bd=0, padx=12, pady=7,
                  command=_compile).pack(side="left", padx=(0, 8))

        tk.Button(btn_frame, text="Delete Frames",
                  font=FONT_BOLD, bg="#c0392b", fg="#ffffff",
                  activebackground="#e74c3c", cursor="hand2",
                  relief="flat", bd=0, padx=12, pady=7,
                  command=_delete).pack(side="left", padx=(8, 0))

    def _start_tray(self):

        if not HAS_TRAY:
            self.root.iconify()
            return
        self.root.withdraw()
        self._ensure_tray_running()

    def _stop_tray(self):
        if self._tray_icon is not None:
            try:
                self._tray_icon.stop()
            except Exception:
                pass
            self._tray_icon = None
        self.root.after(0, self._restore_window)

    def _restore_window(self):
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()

    def _restore_from_tray(self, icon=None, item=None):
        self.root.after(0, self._restore_window)

    def _tray_quit(self, icon=None, item=None):
        self.root.after(0, self._on_close)

    def _on_record(self):
        self._apply_settings()

        if self.config.capture_mode == "window" and not self.config.target_window_title:
            messagebox.showwarning("No Window", "Please enter or pick a window title.")
            return

        if not self.config.output_filename.endswith(".mp4"):
            self.config.output_filename += ".mp4"

        self._paused = False
        self._elapsed_sec = 0

        self._session = RecordingSession(
            config=self.config,
            on_frame=self._on_frame_captured,
            on_status=self._on_session_status,
            on_compile_progress=self._on_compile_progress,
        )
        self._session.start()
        self._control_panel.set_recording()
        self._start_timer()
        self.root.after(800, self._start_tray)

    def _on_pause(self):
        if not self._session:
            return
        if not self._paused:
            self._session.pause()
            self._paused = True
            self._control_panel.set_paused()
            self._timer_running = False
        else:
            self._session.resume()
            self._paused = False
            self._control_panel.set_resumed()
            self._start_timer()

    def _on_stop(self):
        if not self._session:
            return
        self._timer_running = False
        self._stop_tray()
        self._control_panel.set_compiling()
        threading.Thread(
            target=self._session.stop,
            args=(True,),
            daemon=True,
        ).start()

    def _on_frame_captured(self, frame_number: int):
        self.root.after(0, lambda: self._control_panel.update_frame_count(frame_number))

    def _on_session_status(self, status: str, message: str):
        def update():
            if status == RecordingSession.STATUS_DONE:
                self._stop_tray()
                self._control_panel.set_done(message)
                self._timer_running = False
                messagebox.showinfo("Done", message)
            elif status == RecordingSession.STATUS_ERROR:
                self._stop_tray()
                self._control_panel.set_error(message)
                self._timer_running = False
                messagebox.showerror("Error", message)
            elif status == RecordingSession.STATUS_COMPILING:
                self._control_panel.set_compiling()
        self.root.after(0, update)

    def _on_compile_progress(self, current: int, total: int):
        self.root.after(0, lambda: self._control_panel.update_compile_progress(current, total))

    def _start_timer(self):
        self._start_time = time.time() - self._elapsed_sec
        self._timer_running = True
        self._tick_timer()

    def _tick_timer(self):
        if not self._timer_running:
            return
        self._elapsed_sec = time.time() - self._start_time
        self._control_panel.update_elapsed(self._elapsed_sec)
        self.root.after(1000, self._tick_timer)

    def _on_close(self):
        if self._session and self._session.status == RecordingSession.STATUS_RECORDING:
            if not messagebox.askyesno("Quit", "Recording is active. Stop and quit?"):
                return
            self._session.stop(compile_video=False)
        self._stop_tray()
        self.root.destroy()