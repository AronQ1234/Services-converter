from pathlib import Path
from fastapi import HTTPException
from pdf2docx import Converter

def convert_pdf_docx(ext: str, target_format: str, input_path: Path, output_path: Path) -> None:
    if ext == '.pdf' and target_format.lower() == 'docx':
        try:
            cv = Converter(str(input_path))
            cv.convert(str(output_path))
            cv.close()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"PDF→DOCX failed: {e}")
