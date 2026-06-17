<div align="center">
  <img width="212" height="212" alt="record-button" src="https://github.com/user-attachments/assets/dea7b99a-567e-4846-be8d-031acc914d34" />
</div>

# <p align="center">Timelapse Recorder </p>

### <p align="center">*A simple timelapse recorder that captures frames at a configurable interval and compiles them into an MP4 or AVI video using OpenCV and FFmpeg.* </p>

<p align="center">
  <a href="https://github.com/r00t-tsai/Timelapse-Recorder/releases/latest">
    <img src="https://img.shields.io/github/downloads/r00t-tsai/Timelapse-Recorder/total?style=for-the-badge&color=2ea44f&label=DOWNLOADS" alt="Download Counts">
  </a>
</p>

---
### Overview
This application is an interval-based capture and compile system timelapse recorder that doesn't interfere much with the performance of the device, making it good for art timelapses.

### Updates
#### 4/14/2026 - New [version 1.2.1](https://github.com/r00t-tsai/Timelapse-Recorder/releases/tag/v1.2.1) that fixes most errors encountered in the previous versions. The newer version now supports high-effeciency codec (H.264) that results in high-quality rendered video timelapses.
---

### Settings Reference
#### <div align="center"> Some of these settings can also be manually edited inside the `config.py`</div>

<div align="center">

| Setting | Description |
|---|---|
| **Mode** | Full Screen or specific Window |
| **Monitor** | 1-based monitor index |
| **Interval (sec)** | Seconds between captures |
| **Max Frames** | Auto-stop after N frames (0 = unlimited) |
| **Playback FPS** | Speed of the compiled video (24–30 recommended) |
| **Codec** | `avc1` (H.264, default), `mp4v` (MPEG-4V), `XVID`, `MJPG` |
| **Resolution Scale** | Downscale captures (saves disk space) |
| **Frame Format** | PNG (lossless) or JPEG (smaller) |
| **JPEG Quality** | 1–100, only applies when JPEG is chosen |
| **Keep Frames** | Whether to retain individual frame images after compiling |
| **Auto-Compile** | Automatically compile video when stopped |

</div>

### Workflow
#### Note that this app requires administrator privileges to work properly and to avoid compiling issues.

1. Tweak your settings inside the application.
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
## Videos
<div align="center">
  <video src="https://github.com/user-attachments/assets/adaaac99-86f9-40b7-a525-9fb197ba34e8" width="800" controls></video>
  <p><i>Video and art by Cattailarts</i></p>
  <p><i>Please support them: https://x.com/Cattailarts</i></p>
</div>

---
## Downloads
#### Check the [releases](https://github.com/r00t-tsai/Timelapse-Recorder/releases).
---
## References
[FFmpeg](https://ffmpeg.org/)
[OpenCV](https://opencv.org/)
