from pathlib import Path
from PIL import Image
from fastapi import HTTPException

def convert_image(ext: str, target_format: str, input_path: Path, output_path: Path, pixel_size: int = 1) -> None:
    raster_exts = {'.png', '.jpg', '.jpeg', '.bmp', '.avif', '.webp', '.tiff'}
    targets = {'jpg', 'png', 'bmp', 'jpeg', 'webp', 'tiff'}
    if ext in raster_exts and target_format.lower() in targets:
        try:
            with Image.open(input_path) as img:
                img.convert('RGB').save(output_path)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Image conversion failed: {e}")
