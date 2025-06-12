import pymupdf
from pathlib import Path
from fastapi import HTTPException

def convert_pdf_html(ext: str, target_format: str, input_path: Path, output_path: Path) -> None:
    if ext == '.pdf' and target_format.lower() == 'html':
        try:
            doc = pymupdf.open(str(input_path))
            html = ''.join(page.get_text('html') for page in doc)
            output_path.write_text(html, encoding='utf-8')
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"PDF→HTML failed: {e}")
