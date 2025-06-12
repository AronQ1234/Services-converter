from pathlib import Path
from fastapi import HTTPException
from docx import Document

def convert_docx_txt(ext: str, target_format: str, input_path: Path, output_path: Path) -> None:
    if ext == '.docx' and target_format.lower() == 'txt':
        try:
            doc = Document(str(input_path))
            text = '\n'.join(p.text for p in doc.paragraphs)
            output_path.write_text(text, encoding='utf-8')
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"DOCX→TXT failed: {e}")
