import svgwrite
from pathlib import Path
from PIL import Image
from fastapi import HTTPException

def convert_svg(ext: str, target_format: str, input_path: Path, output_path: Path, pixel_size: int = 2) -> None:
    if ext in {'.png', '.jpg', '.jpeg'} and target_format.lower() == 'svg':
        try:
            img = Image.open(input_path).convert('RGB')
            width, height = img.size
            dwg = svgwrite.Drawing(str(output_path), size=(width * pixel_size, height * pixel_size))
            for y in range(height):
                for x in range(width):
                    r, g, b = img.getpixel((x, y))
                    dwg.add(
                        dwg.rect(
                            insert=(x * pixel_size, y * pixel_size),
                            size=(pixel_size, pixel_size),
                            fill=f'#{r:02x}{g:02x}{b:02x}'
                        )
                    )
            dwg.save()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"SVG conversion failed: {e}")
