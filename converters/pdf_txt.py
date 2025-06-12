import pymupdf
from pathlib import Path
from fastapi import HTTPException

def convert_pdf_txt(ext: str, target_format: str, input_path: Path, output_path: Path) -> None:
    if ext == '.pdf' and target_format.lower() == 'txt':
        try:
            doc = pymupdf.open(str(input_path))
            text = ''.join(page.get_text() for page in doc)
            output_path.write_text(text, encoding='utf-8')
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"PDF→TXT failed: {e}")
