# from fastapi import FastAPI, UploadFile, File, Form, HTTPException, BackgroundTasks
# from fastapi.responses import FileResponse
# from fastapi.middleware.cors import CORSMiddleware
# from pathlib import Path
# from uuid import uuid4
# from PIL import Image
# from docx import Document
# from pdf2docx import Converter
# from docx2pdf import convert
# from moviepy import VideoFileClip
# from pydub import AudioSegment
# import pymupdf
# import pypandoc
# import pandas as pd
# import shutil
# import os
# import platform
# import svgwrite
# import asyncio
# import mammoth
# import traceback
# from xhtml2pdf import pisa
# from bs4 import BeautifulSoup

# app = FastAPI()

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# UPLOAD_DIR = Path("uploads"); UPLOAD_DIR.mkdir(exist_ok=True)
# CONVERT_DIR = Path("convert_temp"); CONVERT_DIR.mkdir(exist_ok=True)
# PIXEL_SIZE = 2

# media_types = {
#     "html": "text/html", "txt": "text/plain", "json": "application/json", "csv": "text/csv",
#     "pdf": "application/pdf", "jpg": "image/jpeg", "jpeg": "image/jpeg", "png": "image/png",
#     "bmp": "image/bmp", "webp": "image/webp", "svg": "image/svg+xml", "mp3": "audio/mpeg",
#     "mp4": "video/mp4", "mkv": "video/x-matroska",
#     "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
# }

# def convert_html_file_to_pdf(input_html_path: str, output_pdf_path: str) -> bool:
#     with open(input_html_path, 'r', encoding='utf-8') as f:
#         html_string = f.read()
#     with open(output_pdf_path, "wb") as pdf_file:
#         pisa_status = pisa.CreatePDF(html_string, dest=pdf_file)
#     return not pisa_status.err

# pandoc_path = os.path.abspath("bin/pandoc.exe")
# pypandoc.ensure_pandoc_installed = lambda: True  # Bypass download check
# os.environ["PYPANDOC_PANDOC"] = pandoc_path


# @app.post("/convert/")
# async def convert_file(file: UploadFile = File(...), target_format: str = Form(...)):
#     input_path = CONVERT_DIR / f"{uuid4()}_{file.filename}"
#     output_path = CONVERT_DIR / f"{input_path.stem}_converted.{target_format}"
#     media_type = media_types.get(target_format.lower(), "application/octet-stream")

#     try:
#         with input_path.open("wb") as buffer:
#             shutil.copyfileobj(file.file, buffer)

#         ext = input_path.suffix.lower()

#         if ext in [".png", ".jpg", ".jpeg", ".bmp", ".avif", ".webp", ".tiff"] and target_format in ["jpg", "png", "bmp", "jpeg", "webp", "tiff"]:
#             with Image.open(input_path) as img:
#                 img.convert("RGB").save(output_path)

#         elif ext in [".png", ".jpg", ".jpeg"] and target_format == "svg":
#             with Image.open(input_path) as img:
#                 img = img.convert("RGB")
#                 width, height = img.size
#                 dwg = svgwrite.Drawing(output_path, size=(width * PIXEL_SIZE, height * PIXEL_SIZE))
#                 for y in range(height):
#                     for x in range(width):
#                         r, g, b = img.getpixel((x, y))
#                         hex_color = f'#{r:02x}{g:02x}{b:02x}';
#                         dwg.add(dwg.rect(insert=(x * PIXEL_SIZE, y * PIXEL_SIZE), size=(PIXEL_SIZE, PIXEL_SIZE), fill=hex_color))
#                 dwg.save()

#         elif ext == ".pdf" and target_format == "txt":
#             doc = pymupdf.open(input_path)
#             text = "".join([page.get_text() for page in doc])
#             with open(output_path, "w", encoding="utf-8") as f:
#                 f.write(text)

#         elif ext == ".docx" and target_format == "txt":
#             text = "\n".join(p.text for p in Document(input_path).paragraphs)
#             with open(output_path, "w", encoding="utf-8") as f:
#                 f.write(text)

#         elif ext == ".pdf" and target_format == "docx":
#             Converter(str(input_path)).convert(str(output_path)); Converter(str(input_path)).close()

#         elif ext == ".docx" and target_format == "pdf":
#             convert(str(input_path), str(output_path))

#         elif ext == ".docx" and target_format == "html":
#             with open(input_path, "rb") as docx_file:
#                 html = mammoth.convert_to_html(docx_file).value
#                 with open(output_path, "w", encoding="utf-8") as f:
#                     f.write(html)
        
#         elif ext == ".pdf" and target_format == "html":
#             doc = pymupdf.open(input_path)
#             html_content = "".join([page.get_text("html") for page in doc])
#             with open(output_path, "w", encoding="utf-8") as f:
#                 f.write(html_content)
        
#         elif ext in [".html", ".docx", ".doc", ".txt"] and target_format in ["rtf", "html"]:
#                 pandoc_from = "md" if ext == ".txt" else ext
#                 pypandoc.convert_file(str(input_path), target_format, format=pandoc_from, outputfile=str(output_path))
        
#         elif ext == ".pdf" and target_format == "rtf":
#             doc = pymupdf.open(str(input_path))
#             rtf_content = "{\\rtf1\\ansi\n"  # Start of RTF file
#             for page in doc:
#                 text = page.get_text("text")  # Plain text
#                 text = text.replace("\n", "\\line\n")  # Convert line breaks for RTF
#                 rtf_content += text + "\\par\n"

#             rtf_content += "}"

#             with open(output_path, "w", encoding="utf-8") as f:
#                 f.write(rtf_content)
        
#         elif ext == ".rtf" and target_format in ["html", "docx", "pdf", "txt"]:
#                 pandoc_target = "plain" if target_format == "txt" else target_format
#                 pypandoc.convert_file(str(input_path), pandoc_target, outputfile=str(output_path))
        
#         elif ext == ".html" and target_format in ["docx", "pdf", "doc", "txt", "rtf"]:
#                 if target_format == "pdf":
#                     convert_html_file_to_pdf(str(input_path), str(output_path))
#                 else:
#                     pandoc_target = "plain" if target_format == "txt" else target_format
#                     pypandoc.convert_file(str(input_path), pandoc_target, outputfile=str(output_path))

#         elif ext in [".mp4", ".mov", ".avi"] and target_format == "mp3":
#             VideoFileClip(str(input_path)).audio.write_audiofile(str(output_path))

#         elif ext in [".mp4", ".mov", ".avi"] and target_format in ["mp4", "mkv", "mov", "avi"]:
#             VideoFileClip(str(input_path)).write_videofile(str(output_path), codec="libx264", audio_codec="aac")

#         elif ext in [".wav", ".mp3", ".m4a"] and target_format == "mp3":
#             AudioSegment.from_file(input_path).export(output_path, format=target_format)

#         elif ext == ".xlsx" and target_format == "csv":
#             pd.read_excel(input_path, engine="openpyxl").to_csv(output_path, index=False)

#         elif ext == ".xlsx" and target_format == "json":
#             pd.read_excel(input_path, engine="openpyxl").to_json(output_path, orient="records", indent=2)

#         elif ext == ".csv" and target_format == "xlsx":
#             pd.read_csv(input_path).to_excel(output_path, index=False, engine="openpyxl")

#         elif ext == ".csv" and target_format == "json":
#             pd.read_csv(input_path).to_json(output_path, orient="records", indent=2)

#         elif ext == ".json" and target_format == "csv":
#             pd.read_json(input_path).to_csv(output_path, index=False)

#         elif ext == ".json" and target_format == "xlsx":
#             pd.read_json(input_path).to_excel(output_path, index=False, engine="openpyxl")

#         else:
#             raise HTTPException(status_code=400, detail=f"Unsupported conversion: {ext} to {target_format}")

#         if not output_path.exists():
#             raise HTTPException(status_code=500, detail="Conversion failed: Output file was not created")

#         return FileResponse(output_path, filename=output_path.name, media_type=media_type)

#     except Exception as e:
#         traceback.print_exc()
#         raise HTTPException(status_code=500, detail=f"Conversion error: {str(e)}")

# async def delete_file_later(path: Path, delay: int = 5):
#     await asyncio.sleep(delay*1000)
#     try: path.unlink()
#     except FileNotFoundError: pass

# @app.post("/upload-temp-docx/")
# async def upload_docx(file: UploadFile = File(...), background_tasks: BackgroundTasks = None):
#     if not file.filename.endswith(".docx"):
#         raise HTTPException(status_code=400, detail="Only .docx files allowed")

#     file_id = uuid4().hex
#     saved_path = UPLOAD_DIR / f"{file_id}_{file.filename}"
#     with saved_path.open("wb") as f:
#         shutil.copyfileobj(file.file, f)

#     background_tasks.add_task(delete_file_later, saved_path)

#     return {"url": f"/temp-files/{saved_path.name}"}

# @app.get("/view/{filename}")
# async def get_temp_file(filename: str):
#     file_path = UPLOAD_DIR / filename
#     if not file_path.exists():
#         raise HTTPException(status_code=404, detail="File not found")
#     return FileResponse(file_path)


import os
import shutil
import asyncio
import logging
from pathlib import Path
from uuid import uuid4
import pypandoc

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, BackgroundTasks, Depends
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseSettings

from converters import (
    convert_image,
    convert_svg,
    convert_pdf_txt,
    convert_docx_txt,
    convert_pdf_docx,
    convert_docx_pdf,
    convert_mammoth_html,
    convert_pdf_html,
    convert_with_pandoc,
    convert_rtf,
    convert_video,
    convert_audio,
    convert_sheet,
)

# --- Configuration ---
class Settings(BaseSettings):
    upload_dir: Path = Path(os.getenv("UPLOAD_DIR", "uploads"))
    convert_dir: Path = Path(os.getenv("CONVERT_DIR", "convert_temp"))
    cleanup_delay_sec: int = int(os.getenv("CLEANUP_DELAY_SEC", "10"))
    allowed_origins: list[str] = ["*"]
    pixel_size: int = 2

    class Config:
        env_file = ".env"

settings = Settings()

# --- Logging ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Pandoc Setup ---
# Tell pypandoc where to find the Pandoc binary and bypass install check

# --- App Initialization ---
app = FastAPI(title="File Conversion API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure directories exist
for directory in (settings.upload_dir, settings.convert_dir):
    directory.mkdir(parents=True, exist_ok=True)

# Supported output media types
MEDIA_TYPES: dict[str, str] = {
    "html": "text/html", "txt": "text/plain", "json": "application/json", "csv": "text/csv",
    "pdf": "application/pdf", "jpg": "image/jpeg", "jpeg": "image/jpeg", "png": "image/png",
    "bmp": "image/bmp", "webp": "image/webp", "svg": "image/svg+xml", "mp3": "audio/mpeg",
    "mp4": "video/mp4", "mkv": "video/x-matroska",
    "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}

# --- Utility Tasks ---
async def _delete_file(path: Path, delay_sec: int) -> None:
    await asyncio.sleep(delay_sec)
    try:
        path.unlink()
        logger.info(f"Deleted file: {path}")
    except FileNotFoundError:
        logger.warning(f"File already removed: {path}")

# --- Endpoints ---
@app.post("/convert/", response_class=FileResponse)
async def convert_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    target_format: str = Form(...),
    settings: Settings = Depends(lambda: settings),
):
    # Generate paths
    file_id = uuid4().hex
    input_path = settings.convert_dir / f"{file_id}_{file.filename}"
    output_filename = f"{Path(input_path.name).stem}_converted.{target_format}"
    output_path = settings.convert_dir / output_filename
    media_type = MEDIA_TYPES.get(target_format.lower(), "application/octet-stream")

    # Save upload
    try:
        with input_path.open("wb") as buf:
            shutil.copyfileobj(file.file, buf)
        logger.info(f"Saved input file: {input_path}")
    except Exception as e:
        logger.error(f"Failed to save upload: {e}")
        raise HTTPException(status_code=500, detail="Error saving upload")

    # Perform conversion
    try:
        ext = input_path.suffix.lower()
        convert_image(ext, target_format, input_path, output_path, pixel_size=settings.pixel_size)
        convert_svg(ext, target_format, input_path, output_path, pixel_size=settings.pixel_size)
        convert_pdf_txt(ext, target_format, input_path, output_path)
        convert_docx_txt(ext, target_format, input_path, output_path)
        convert_pdf_docx(ext, target_format, input_path, output_path)
        convert_docx_pdf(ext, target_format, input_path, output_path)
        convert_mammoth_html(ext, target_format, input_path, output_path)
        convert_pdf_html(ext, target_format, input_path, output_path)
        convert_with_pandoc(ext, target_format, input_path, output_path)
        convert_rtf(ext, target_format, input_path, output_path)
        convert_video(ext, target_format, input_path, output_path)
        convert_audio(ext, target_format, input_path, output_path)
        convert_sheet(ext, target_format, input_path, output_path)
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Conversion error")
        raise HTTPException(status_code=500, detail=f"Conversion failed: {e}")

    if not output_path.exists():
        logger.error("Output file not created")
        raise HTTPException(status_code=500, detail="Conversion failed: no output generated")

    # Schedule cleanup
    background_tasks.add_task(_delete_file, input_path, settings.cleanup_delay_sec)
    background_tasks.add_task(_delete_file, output_path, settings.cleanup_delay_sec)

    return FileResponse(
        path=str(output_path),
        filename=output_filename,
        media_type=media_type,
    )

@app.post("/upload-temp-docx/", response_model=dict)
async def upload_docx(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = Depends(),
    settings: Settings = Depends(lambda: settings),
):
    if not file.filename.lower().endswith(".docx"):
        raise HTTPException(status_code=400, detail="Only .docx files allowed")

    file_id = uuid4().hex
    saved_path = settings.upload_dir / f"{file_id}_{file.filename}"
    try:
        with saved_path.open("wb") as buf:
            shutil.copyfileobj(file.file, buf)
    except Exception as e:
        logger.error(f"Failed to save docx: {e}")
        raise HTTPException(status_code=500, detail="Error saving .docx file")

    background_tasks.add_task(_delete_file, saved_path, settings.cleanup_delay_sec)
    return {"url": f"/view/{saved_path.name}"}

@app.get("/view/{filename}", response_class=FileResponse)
async def get_temp_file(
    filename: str,
    settings: Settings = Depends(lambda: settings),
):
    file_path = settings.upload_dir / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(path=str(file_path))
