from pathlib import Path
from fastapi import HTTPException
from docx2pdf import convert

def convert_docx_pdf(ext: str, target_format: str, input_path: Path, output_path: Path) -> None:
    if ext == '.docx' and target_format.lower() == 'pdf':
        try:
            convert(str(input_path), str(output_path))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"DOCX→PDF failed: {e}")
