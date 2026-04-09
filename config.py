from dataclasses import dataclass, field
from typing import Optional, Tuple

@dataclass
class TimelapseConfig:

    capture_mode: str = "fullscreen"          
    target_window_title: Optional[str] = None  
    capture_interval_sec: float = 3.0          
    output_dir: str = "output"       
    output_filename: str = "recording.mp4"     
    output_fps: int = 30                        
    frame_format: str = "PNG"                  
    jpeg_quality: int = 90                     
    save_frames: bool = True                   
    video_codec: str = "mp4v"                  
    resolution_scale: float = 1.0              
    monitor_index: int = 1                     
    custom_region: Optional[Tuple[int,int,int,int]] = None  
    max_frames: int = 0                        
    auto_compile: bool = True                  

    def frames_dir(self) -> str:
        import os
        return os.path.join(self.output_dir, "frames")

    def video_path(self) -> str:
        import os
        return os.path.join(self.output_dir, self.output_filename)

