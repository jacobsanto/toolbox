# File Reading Strategies — Detailed Reference

## PDF — Text-based

```python
import pdfplumber, hashlib

def read_pdf_text(path):
    md5 = hashlib.md5(open(path,'rb').read()).hexdigest()
    with pdfplumber.open(path) as pdf:
        pages = len(pdf.pages)
        text = ""
        for page in pdf.pages[:2]:  # first 2 pages only
            text += page.extract_text() or ""
    return {"md5": md5, "pages": pages, "text": text[:3000]}
```

Extract from text:
- Lines 1–10: usually header with entity name, document type, logo text
- Look for: date patterns (DD/MM/YYYY, YYYY-MM-DD), ΑΦΜ (9 digits), invoice numbers

## PDF — Scanned (no selectable text)

```python
import pdf2image, pytesseract, hashlib
from PIL import Image

def read_pdf_scanned(path):
    md5 = hashlib.md5(open(path,'rb').read()).hexdigest()
    images = pdf2image.convert_from_path(path, dpi=200, first_page=1, last_page=2)
    text = ""
    for img in images:
        text += pytesseract.image_to_string(img, lang='ell+eng')
    return {"md5": md5, "pages": len(images), "text": text[:3000], "method": "OCR"}
```

OCR tips:
- Language `ell+eng` covers Greek + English simultaneously
- If OCR output is garbage (confidence <30%), fall back to Claude vision
- Pre-process: increase contrast if image is faint

## DOCX

```python
from docx import Document
import hashlib

def read_docx(path):
    md5 = hashlib.md5(open(path,'rb').read()).hexdigest()
    doc = Document(path)
    # Core properties
    props = doc.core_properties
    author = props.author
    created = props.created
    title = props.title
    # First 500 chars of body
    text = "\n".join([p.text for p in doc.paragraphs[:20]])
    return {"md5": md5, "author": author, "created": str(created),
            "title": title, "text": text[:1500]}
```

Also check: table content in first 3 tables (often has dates, entity names).

## XLSX

```python
import openpyxl, hashlib

def read_xlsx(path):
    md5 = hashlib.md5(open(path,'rb').read()).hexdigest()
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    sheets = wb.sheetnames
    # First sheet, first 10 rows
    ws = wb.active
    rows = []
    for i, row in enumerate(ws.iter_rows(values_only=True)):
        if i >= 10: break
        rows.append(row)
    return {"md5": md5, "sheets": sheets, "preview": rows}
```

Look for: company name in A1, date in headers, sheet names for document type.

## PPTX

```python
from pptx import Presentation
import hashlib

def read_pptx(path):
    md5 = hashlib.md5(open(path,'rb').read()).hexdigest()
    prs = Presentation(path)
    slide1 = prs.slides[0]
    text = "\n".join([shape.text for shape in slide1.shapes if hasattr(shape, 'text')])
    total_slides = len(prs.slides)
    return {"md5": md5, "slides": total_slides, "title_slide_text": text[:1000]}
```

## Images (JPG, PNG, WEBP, TIFF)

Strategy 1 — Claude vision (preferred):
- Pass image directly to Claude with prompt:
  "Read all visible text. What is this document? Who issued it? What date?"

Strategy 2 — pytesseract fallback:
```python
import pytesseract
from PIL import Image
text = pytesseract.image_to_string(Image.open(path), lang='ell+eng')
```

For photos (not documents): use vision to describe content → derive filename from subject.

## ZIP / RAR

```bash
# ZIP
unzip -l archive.zip | head -50

# RAR (if unrar installed)
unrar l archive.rar | head -50
```

Do NOT extract unless user explicitly asks. List contents, infer purpose from filenames inside.
MD5 on the archive file itself.

## CSV

```python
import pandas as pd, hashlib
md5 = hashlib.md5(open(path,'rb').read()).hexdigest()
df = pd.read_csv(path, nrows=5)
info = {"md5": md5, "columns": list(df.columns), "rows_preview": df.head(3).to_dict()}
```

## JSON

```bash
head -50 file.json | python3 -m json.tool 2>/dev/null || head -50 file.json
```

Look at top-level keys to infer document type.

## Code files (.py, .js, .ts, .sql, etc.)

```bash
head -100 file.py
```

Extract: first docstring/comment block, function names, imports (reveal purpose).
Entity = author if in header comment. Date = last modified or header date.

## Google Drive files

Preferred: `google_drive_fetch(document_ids=[file_id])`
- Extracts clean text from Google Docs, Sheets, Slides
- Returns markdown-formatted content

If fetch fails (too large): use `google_drive_search` to get metadata only (title, modified date, owner).

## Fallback chain

If all above fail:
1. Try `file` command: `file unknown_file` (detects true MIME type)
2. Try `strings unknown_file | head -50` (extract printable strings from binary)
3. Try `xxd unknown_file | head -20` (hex dump — last resort)
4. Report UNREADABLE with what was attempted

## Package installation (if needed)

```bash
pip install pdfplumber pdf2image pytesseract python-docx openpyxl python-pptx pandas pillow --break-system-packages
sudo apt-get install -y tesseract-ocr tesseract-ocr-ell poppler-utils 2>/dev/null
```
