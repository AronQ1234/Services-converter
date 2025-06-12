from pathlib import Path
from fastapi import HTTPException
from moviepy import VideoFileClip

def convert_video(ext: str, target_format: str, input_path: Path, output_path: Path) -> None:
    video_exts = {'.mp4', '.mov', '.avi'}
    if ext in video_exts and target_format.lower() in {'mp4', 'mkv', 'mov', 'avi'}:
        try:
            clip = VideoFileClip(str(input_path))
            clip.write_videofile(str(output_path), codec='libx264', audio_codec='aac')
            clip.close()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Video conversion failed: {e}")
