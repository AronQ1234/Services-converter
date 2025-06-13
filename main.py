from fastapi import FastAPI, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from uuid import uuid4
from PIL import Image
from docx import Document
from pdf2docx import Converter
from docx2pdf import convert
from moviepy import VideoFileClip
from pydub import AudioSegment
import pymupdf
import pypandoc
import pandas as pd
import shutil
import os
import platform
import svgwrite
import asyncio
import mammoth
import traceback
from xhtml2pdf import pisa
from bs4 import BeautifulSoup

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = Path("uploads"); UPLOAD_DIR.mkdir(exist_ok=True)
CONVERT_DIR = Path("convert_temp"); CONVERT_DIR.mkdir(exist_ok=True)
PIXEL_SIZE = 2

media_types = {
    "html": "text/html", "txt": "text/plain", "json": "application/json", "csv": "text/csv",
    "pdf": "application/pdf", "jpg": "image/jpeg", "jpeg": "image/jpeg", "png": "image/png",
    "bmp": "image/bmp", "webp": "image/webp", "svg": "image/svg+xml", "mp3": "audio/mpeg",
    "mp4": "video/mp4", "mkv": "video/x-matroska",
    "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}

def convert_html_file_to_pdf(input_html_path: str, output_pdf_path: str) -> bool:
    with open(input_html_path, 'r', encoding='utf-8') as f:
        html_string = f.read()
    with open(output_pdf_path, "wb") as pdf_file:
        pisa_status = pisa.CreatePDF(html_string, dest=pdf_file)
    return not pisa_status.err

def clean_directory(path: Path):
    for item in path.iterdir():
        try:
            if item.is_file() or item.is_symlink():
                item.unlink()
            elif item.is_dir():
                shutil.rmtree(item)
        except Exception as e:
            print(f"Failed to delete {item}: {e}")

clean_directory(Path("uploads"))
clean_directory(Path("convert_temp"))
pypandoc.download_pandoc()


@app.post("/convert/")
async def convert_file(file: UploadFile = File(...), target_format: str = Form(...), background_tasks: BackgroundTasks = None):
    input_path = CONVERT_DIR / f"{uuid4()}_{file.filename}"
    output_path = CONVERT_DIR / f"{input_path.stem}_converted.{target_format}"
    media_type = media_types.get(target_format.lower(), "application/octet-stream")

    try:
        with input_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        ext = input_path.suffix.lower()

        if ext in [".png", ".jpg", ".jpeg", ".bmp", ".avif", ".webp", ".tiff"] and target_format in ["jpg", "png", "bmp", "jpeg", "webp", "tiff"]:
            with Image.open(input_path) as img:
                img.convert("RGB").save(output_path)

        elif ext in [".png", ".jpg", ".jpeg"] and target_format == "svg":
            with Image.open(input_path) as img:
                img = img.convert("RGB")
                width, height = img.size
                dwg = svgwrite.Drawing(output_path, size=(width * PIXEL_SIZE, height * PIXEL_SIZE))
                for y in range(height):
                    for x in range(width):
                        r, g, b = img.getpixel((x, y))
                        hex_color = f'#{r:02x}{g:02x}{b:02x}';
                        dwg.add(dwg.rect(insert=(x * PIXEL_SIZE, y * PIXEL_SIZE), size=(PIXEL_SIZE, PIXEL_SIZE), fill=hex_color))
                dwg.save()

        elif ext == ".pdf" and target_format == "txt":
            doc = pymupdf.open(input_path)
            text = "".join([page.get_text() for page in doc])
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(text)

        elif ext == ".docx" and target_format == "txt":
            text = "\n".join(p.text for p in Document(input_path).paragraphs)
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(text)

        elif ext == ".pdf" and target_format == "docx":
            Converter(str(input_path)).convert(str(output_path)); Converter(str(input_path)).close()

        elif ext == ".docx" and target_format == "pdf":
            convert(str(input_path), str(output_path))

        elif ext == ".docx" and target_format == "html":
            with open(input_path, "rb") as docx_file:
                html = mammoth.convert_to_html(docx_file).value
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(html)
        
        elif ext == ".pdf" and target_format == "html":
            doc = pymupdf.open(input_path)
            html_content = "".join([page.get_text("html") for page in doc])
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(html_content)
        
        elif ext in [".html", ".docx", ".doc", ".txt"] and target_format in ["rtf", "html"]:
            pandoc_from = "md" if ext == ".txt" else ext.lstrip(".")
            pypandoc.convert_file(str(input_path), target_format, format=pandoc_from, outputfile=str(output_path))
        
        elif ext == ".pdf" and target_format == "rtf":
            doc = pymupdf.open(str(input_path))
            rtf_content = "{\\rtf1\\ansi\n"  # Start of RTF file
            for page in doc:
                text = page.get_text("text")  # Plain text
                text = text.replace("\n", "\\line\n")  # Convert line breaks for RTF
                rtf_content += text + "\\par\n"

            rtf_content += "}"

            with open(output_path, "w", encoding="utf-8") as f:
                f.write(rtf_content)
        
        elif ext == ".rtf" and target_format in ["html", "docx", "pdf", "txt"]:
                pandoc_target = "plain" if target_format == "txt" else target_format
                pypandoc.convert_file(str(input_path), pandoc_target, outputfile=str(output_path))
        
        elif ext == ".html" and target_format in ["docx", "pdf", "doc", "txt", "rtf"]:
                if target_format == "pdf":
                    convert_html_file_to_pdf(str(input_path), str(output_path))
                else:
                    pandoc_target = "plain" if target_format == "txt" else target_format
                    pypandoc.convert_file(str(input_path), pandoc_target, outputfile=str(output_path))

        elif ext in [".mp4", ".mov", ".avi"] and target_format == "mp3":
            VideoFileClip(str(input_path)).audio.write_audiofile(str(output_path))

        elif ext in [".mp4", ".mov", ".avi"] and target_format in ["mp4", "mkv", "mov", "avi"]:
            VideoFileClip(str(input_path)).write_videofile(str(output_path), codec="libx264", audio_codec="aac")

        elif ext in [".wav", ".mp3", ".m4a"] and target_format == "mp3":
            AudioSegment.from_file(input_path).export(output_path, format=target_format)

        elif ext == ".xlsx" and target_format == "csv":
            pd.read_excel(input_path, engine="openpyxl").to_csv(output_path, index=False)

        elif ext == ".xlsx" and target_format == "json":
            pd.read_excel(input_path, engine="openpyxl").to_json(output_path, orient="records", indent=2)

        elif ext == ".csv" and target_format == "xlsx":
            pd.read_csv(input_path).to_excel(output_path, index=False, engine="openpyxl")

        elif ext == ".csv" and target_format == "json":
            pd.read_csv(input_path).to_json(output_path, orient="records", indent=2)

        elif ext == ".json" and target_format == "csv":
            pd.read_json(input_path).to_csv(output_path, index=False)

        elif ext == ".json" and target_format == "xlsx":
            pd.read_json(input_path).to_excel(output_path, index=False, engine="openpyxl")

        else:
            raise HTTPException(status_code=400, detail=f"Unsupported conversion: {ext} to {target_format}")

        if not output_path.exists():
            raise HTTPException(status_code=500, detail="Conversion failed: Output file was not created")

        if background_tasks:
            background_tasks.add_task(delete_file_later, input_path)
            background_tasks.add_task(delete_file_later, output_path)
        
        return FileResponse(output_path, filename=output_path.name, media_type=media_type)

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Conversion error: {str(e)}")

async def delete_file_later(path: Path, delay: int = 10):
    await asyncio.sleep(delay)
    try: path.unlink()
    except FileNotFoundError: pass

@app.post("/upload-temp-docx/")
async def upload_docx(file: UploadFile = File(...), background_tasks: BackgroundTasks = None):
    if not file.filename.endswith(".docx"):
        raise HTTPException(status_code=400, detail="Only .docx files allowed")

    file_id = uuid4().hex
    saved_path = UPLOAD_DIR / f"{file_id}_{file.filename}"
    with saved_path.open("wb") as f:
        shutil.copyfileobj(file.file, f)

    background_tasks.add_task(delete_file_later, saved_path)

    return {"url": f"/view/{saved_path.name}"}

@app.get("/view/{filename}")
async def get_temp_file(filename: str):
    file_path = UPLOAD_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path)
