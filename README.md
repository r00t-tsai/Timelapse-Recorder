# Timelapse Recorder

A Python timelapse recorder. Captures frames at a configurable interval and compiles them into an MP4 video using OpenCV.

---

# Manual Usage

### Speed Reference
1 sec interval @ 30 fps || 1 hr → ~2.5 min video

3 sec interval @ 30 fps || 1 hr → ~50 sec video

10 sec interval @ 30 fps || 1 hr → ~15 sec video

60 sec interval @ 30 fps || 1 hr → ~2.5 sec video

---

### Disk Usage Estimates
PNG  1080p → ~3.8 mb / frame

JPEG  1080p → ~0.3-1 mb / frame

PNG  0.5x → ~0.8-2 mb / frame

JPEG  0.5x → ~80-250 kb / frame

---

### Settings Reference

| Setting | Description |
|---|---|
| **Mode** | Full Screen or specific Window |
| **Window Title** | Partial title to match (window mode) |
| **Monitor** | 1-based monitor index |
| **Interval (sec)** | Seconds between captures |
| **Max Frames** | Auto-stop after N frames (0 = unlimited) |
| **Output Dir** | Folder for frames and final video |
| **Filename** | Output `.mp4` filename |
| **Playback FPS** | Speed of the compiled video (24–30 recommended) |
| **Codec** | `mp4v` (default), `avc1`, `XVID`, `MJPG` |
| **Resolution Scale** | Downscale captures (saves disk space) |
| **Frame Format** | PNG (lossless) or JPEG (smaller) |
| **JPEG Quality** | 1–100, only applies when JPEG is chosen |
| **Keep Frames** | Whether to retain individual frame images |
| **Auto-Compile** | Automatically compile video when stopped |

---

### Workflow

1. Tweak settings and press **APPLY SETTINGS**
2. Press **RECORD** to begin capturing
3. Optionally **PAUSE** / **RESUME** at any time
4. Press **STOP** — video compiles automatically if enabled

---

