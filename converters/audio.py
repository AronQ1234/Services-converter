from pathlib import Path
from fastapi import HTTPException
from pydub import AudioSegment

def convert_audio(ext: str, target_format: str, input_path: Path, output_path: Path) -> None:
    audio_exts = {'.wav', '.mp3', '.m4a'}
    if ext in audio_exts and target_format.lower() == 'mp3':
        try:
            AudioSegment.from_file(str(input_path)).export(str(output_path), format=target_format)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Audio conversion failed: {e}")
