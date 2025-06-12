from pathlib import Path
from fastapi import HTTPException
import pymupdf

def convert_rtf(ext: str, target_format: str, input_path: Path, output_path: Path) -> None:
    if ext == '.pdf' and target_format.lower() == 'rtf':
        try:
            doc = pymupdf.open(str(input_path))
            rtf = '{\\rtf1\\ansi\n'
            for page in doc:
                txt = page.get_text('text').replace('\n', '\\line\n')
                rtf += txt + '\\par\n'
            rtf += '}'
            output_path.write_text(rtf, encoding='utf-8')
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"PDF→RTF failed: {e}")
