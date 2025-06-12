from pathlib import Path
from fastapi import HTTPException
import mammoth

def convert_mammoth_html(ext: str, target_format: str, input_path: Path, output_path: Path) -> None:
    if ext == '.docx' and target_format.lower() == 'html':
        try:
            with open(input_path, 'rb') as f:
                html = mammoth.convert_to_html(f).value
            output_path.write_text(html, encoding='utf-8')
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"DOCX→HTML failed: {e}")
