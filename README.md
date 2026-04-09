# Timelapse Recorder

A Python timelapse recorder. Captures frames at a configurable interval and compiles them into an MP4 video using OpenCV. Since it is an interval-based capture and compile system, it doesn't interfere much with the performance of your device, making it good for art timelapses.

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
#### Some of these settings can be manually edited inside the `config.py`

| Setting | Description |
|---|---|
| **Mode** | Full Screen or specific Window |
| **Monitor** | 1-based monitor index |
| **Interval (sec)** | Seconds between captures |
| **Max Frames** | Auto-stop after N frames (0 = unlimited) |
| **Playback FPS** | Speed of the compiled video (24–30 recommended) |
| **Codec** | `mp4v` (MPEG-4, default), `avc1` (H.264), `XVID`, `MJPG` |
| **Resolution Scale** | Downscale captures (saves disk space) |
| **Frame Format** | PNG (lossless) or JPEG (smaller) |
| **JPEG Quality** | 1–100, only applies when JPEG is chosen |
| **Keep Frames** | Whether to retain individual frame images after compiling |
| **Auto-Compile** | Automatically compile video when stopped |

---

### Workflow
#### Note that this app requires administrator privileges to work properly and to avoid compiling issues.

1. Tweak settings and press **APPLY SETTINGS**.
2. Press **RECORD** to begin capturing. The app will be minimized in the system tray.
3. Optionally **PAUSE** / **RESUME** at any time.
4. Press **STOP** and the app compiles the timelapse automatically.

- If progress is lost due to an unexpected interference like a device shutdown, the program in the second startup will automatically save your progress and prompts you to either compile or delete it. If you choose to ignore this and start a new recording session, the data that you recorded before will be overwritten/deleted.
- During recording, the recorder will be minimized in the system tray. You can find it there if you ever need to take a break to pause or to finish your recording session.

---
## Images
<table>
  <tr>
    <td><img src="https://github.com/user-attachments/assets/6e065357-bb80-46b5-9a15-7a3419e48054" alt="Screenshot 1" /></td>
    <td><img src="https://github.com/user-attachments/assets/3eadf854-1fc4-466a-9229-75654a777844" alt="Screenshot 2" /></td>
  </tr>
  <tr>
    <td><img src="https://github.com/user-attachments/assets/52266ea2-1d1b-4d10-a17f-98c0fbf44104" alt="Screenshot 3" /></td>
    <td><img src="https://github.com/user-attachments/assets/6dbfa84d-18c8-49a4-b3e3-05d69e51d0cb" alt="Screenshot 4" /></td>
  </tr>
</table>

---
## Downloads
Check the [releases](https://github.com/r00t-tsai/Timelapse-Recorder/releases/tag/v1.0)


