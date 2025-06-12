import pypandoc
from pathlib import Path
from fastapi import HTTPException

def convert_with_pandoc(ext: str, target_format: str, input_path: Path, output_path: Path) -> None:
    mapping = {
        '.txt': 'md',
        '.doc': 'doc',
        '.docx': 'docx',
        '.html': 'html',
        '.rtf': 'rtf'
    }
    if ext in mapping and target_format.lower() in {'rtf', 'html', 'docx', 'pdf', 'txt'}:
        try:
            pypandoc.download_pandoc()
            src_fmt = mapping[ext]
            out_fmt = 'plain' if target_format.lower() == 'txt' else target_format
            if out_fmt == 'pdf':
                # PDF via HTML→PDF fallback
                from converters import convert_pdf_html
                html_temp = input_path.with_suffix('.html')
                convert_pdf_html(ext, 'html', input_path, html_temp)
                from converters import convert_docx_pdf
                convert_docx_pdf('.docx', 'pdf', html_temp, output_path)
            else:
                pypandoc.convert_file(str(input_path), out_fmt, format=src_fmt, outputfile=str(output_path))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Pandoc conversion failed: {e}")
