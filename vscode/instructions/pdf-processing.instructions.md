---
applyTo: "**"
description: "PDF processing: reading, creating, merging, splitting, extracting text/tables, watermarks, encryption, OCR"
---

# PDF Processing Guide

> **Prerequisites:** This skill requires `pdf-lib` (npm). Optional: `poppler-utils`, `qpdf` (CLI). Run `/setup-common-prompts` to check and install missing dependencies.

Use these instructions whenever working with PDF files — reading, extracting text/tables, combining, splitting, rotating pages, adding watermarks, creating new PDFs, encrypting/decrypting, extracting images, or OCR on scanned PDFs. If the user mentions a .pdf file or asks to produce one, follow this guide.

For filling PDF forms, see `pdf-forms.instructions.md`.

## Quick Start

```python
from pypdf import PdfReader, PdfWriter

# Read a PDF
reader = PdfReader("document.pdf")
print(f"Pages: {len(reader.pages)}")

# Extract text
text = ""
for page in reader.pages:
    text += page.extract_text()
```

## Python Libraries

### pypdf - Basic Operations

#### Merge PDFs
```python
from pypdf import PdfWriter, PdfReader

writer = PdfWriter()
for pdf_file in ["doc1.pdf", "doc2.pdf", "doc3.pdf"]:
    reader = PdfReader(pdf_file)
    for page in reader.pages:
        writer.add_page(page)

with open("merged.pdf", "wb") as output:
    writer.write(output)
```

#### Split PDF
```python
reader = PdfReader("input.pdf")
for i, page in enumerate(reader.pages):
    writer = PdfWriter()
    writer.add_page(page)
    with open(f"page_{i+1}.pdf", "wb") as output:
        writer.write(output)
```

#### Extract Metadata
```python
reader = PdfReader("document.pdf")
meta = reader.metadata
print(f"Title: {meta.title}")
print(f"Author: {meta.author}")
print(f"Subject: {meta.subject}")
print(f"Creator: {meta.creator}")
```

#### Rotate Pages
```python
reader = PdfReader("input.pdf")
writer = PdfWriter()

page = reader.pages[0]
page.rotate(90)  # Rotate 90 degrees clockwise
writer.add_page(page)

with open("rotated.pdf", "wb") as output:
    writer.write(output)
```

### pdfplumber - Text and Table Extraction

#### Extract Text with Layout
```python
import pdfplumber

with pdfplumber.open("document.pdf") as pdf:
    for page in pdf.pages:
        text = page.extract_text()
        print(text)
```

#### Extract Tables
```python
with pdfplumber.open("document.pdf") as pdf:
    for i, page in enumerate(pdf.pages):
        tables = page.extract_tables()
        for j, table in enumerate(tables):
            print(f"Table {j+1} on page {i+1}:")
            for row in table:
                print(row)
```

#### Advanced Table Extraction
```python
import pandas as pd

with pdfplumber.open("document.pdf") as pdf:
    all_tables = []
    for page in pdf.pages:
        tables = page.extract_tables()
        for table in tables:
            if table:
                df = pd.DataFrame(table[1:], columns=table[0])
                all_tables.append(df)

if all_tables:
    combined_df = pd.concat(all_tables, ignore_index=True)
    combined_df.to_excel("extracted_tables.xlsx", index=False)
```

#### Extract Text with Precise Coordinates
```python
import pdfplumber

with pdfplumber.open("document.pdf") as pdf:
    page = pdf.pages[0]

    chars = page.chars
    for char in chars[:10]:
        print(f"Char: '{char['text']}' at x:{char['x0']:.1f} y:{char['y0']:.1f}")

    # Extract text by bounding box (left, top, right, bottom)
    bbox_text = page.within_bbox((100, 100, 400, 200)).extract_text()
```

#### Custom Table Settings for Complex Layouts
```python
import pdfplumber

with pdfplumber.open("complex_table.pdf") as pdf:
    page = pdf.pages[0]
    table_settings = {
        "vertical_strategy": "lines",
        "horizontal_strategy": "lines",
        "snap_tolerance": 3,
        "intersection_tolerance": 15
    }
    tables = page.extract_tables(table_settings)

    # Visual debugging
    img = page.to_image(resolution=150)
    img.save("debug_layout.png")
```

### reportlab - Create PDFs

#### Basic PDF Creation
```python
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

c = canvas.Canvas("hello.pdf", pagesize=letter)
width, height = letter

c.drawString(100, height - 100, "Hello World!")
c.drawString(100, height - 120, "This is a PDF created with reportlab")
c.line(100, height - 140, 400, height - 140)
c.save()
```

#### Create PDF with Multiple Pages
```python
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet

doc = SimpleDocTemplate("report.pdf", pagesize=letter)
styles = getSampleStyleSheet()
story = []

title = Paragraph("Report Title", styles['Title'])
story.append(title)
story.append(Spacer(1, 12))

body = Paragraph("This is the body of the report. " * 20, styles['Normal'])
story.append(body)
story.append(PageBreak())

story.append(Paragraph("Page 2", styles['Heading1']))
story.append(Paragraph("Content for page 2", styles['Normal']))

doc.build(story)
```

#### Professional Reports with Tables
```python
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

data = [
    ['Product', 'Q1', 'Q2', 'Q3', 'Q4'],
    ['Widgets', '120', '135', '142', '158'],
    ['Gadgets', '85', '92', '98', '105']
]

doc = SimpleDocTemplate("report.pdf")
elements = []
styles = getSampleStyleSheet()
title = Paragraph("Quarterly Sales Report", styles['Title'])
elements.append(title)

table = Table(data)
table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, 0), 14),
    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
    ('GRID', (0, 0), (-1, -1), 1, colors.black)
]))
elements.append(table)
doc.build(elements)
```

#### Subscripts and Superscripts

**IMPORTANT**: Never use Unicode subscript/superscript characters in ReportLab PDFs. The built-in fonts do not include these glyphs, causing them to render as solid black boxes. Use ReportLab's XML markup tags instead:

```python
from reportlab.platypus import Paragraph
from reportlab.lib.styles import getSampleStyleSheet
styles = getSampleStyleSheet()

chemical = Paragraph("H<sub>2</sub>O", styles['Normal'])
squared = Paragraph("x<super>2</super> + y<super>2</super>", styles['Normal'])
```

### pypdfium2 - Fast Rendering and Text Extraction

```python
import pypdfium2 as pdfium
from PIL import Image

pdf = pdfium.PdfDocument("document.pdf")
page = pdf[0]
bitmap = page.render(scale=2.0, rotation=0)
img = bitmap.to_pil()
img.save("page_1.png", "PNG")

# Process multiple pages
for i, page in enumerate(pdf):
    bitmap = page.render(scale=1.5)
    img = bitmap.to_pil()
    img.save(f"page_{i+1}.jpg", "JPEG", quality=90)

# Extract text
for i, page in enumerate(pdf):
    text = page.get_text()
    print(f"Page {i+1} text length: {len(text)} chars")
```

## JavaScript Libraries

### pdf-lib - Create and Modify PDFs

```javascript
import { PDFDocument, rgb, StandardFonts } from 'pdf-lib';
import fs from 'fs';

// Load and modify existing PDF
async function manipulatePDF() {
    const existingPdfBytes = fs.readFileSync('input.pdf');
    const pdfDoc = await PDFDocument.load(existingPdfBytes);
    const newPage = pdfDoc.addPage([600, 400]);
    newPage.drawText('Added by pdf-lib', { x: 100, y: 300, size: 16 });
    const pdfBytes = await pdfDoc.save();
    fs.writeFileSync('modified.pdf', pdfBytes);
}

// Merge PDFs
async function mergePDFs() {
    const mergedPdf = await PDFDocument.create();
    const pdf1 = await PDFDocument.load(fs.readFileSync('doc1.pdf'));
    const pdf2 = await PDFDocument.load(fs.readFileSync('doc2.pdf'));

    const pdf1Pages = await mergedPdf.copyPages(pdf1, pdf1.getPageIndices());
    pdf1Pages.forEach(page => mergedPdf.addPage(page));

    const pdf2Pages = await mergedPdf.copyPages(pdf2, [0, 2, 4]);
    pdf2Pages.forEach(page => mergedPdf.addPage(page));

    fs.writeFileSync('merged.pdf', await mergedPdf.save());
}
```

## Command-Line Tools

### pdftotext (poppler-utils)
```bash
pdftotext input.pdf output.txt                    # Extract text
pdftotext -layout input.pdf output.txt            # Preserve layout
pdftotext -f 1 -l 5 input.pdf output.txt          # Pages 1-5
pdftotext -bbox-layout document.pdf output.xml     # With bounding boxes
```

### qpdf
```bash
qpdf --empty --pages file1.pdf file2.pdf -- merged.pdf                    # Merge
qpdf input.pdf --pages . 1-5 -- pages1-5.pdf                             # Split
qpdf input.pdf output.pdf --rotate=+90:1                                  # Rotate page 1
qpdf --password=mypassword --decrypt encrypted.pdf decrypted.pdf          # Decrypt
qpdf --linearize input.pdf optimized.pdf                                  # Optimize for web
qpdf --encrypt user_pass owner_pass 256 --print=none -- in.pdf out.pdf   # Encrypt
qpdf --split-pages=3 input.pdf output_%02d.pdf                           # Split into groups
qpdf --check input.pdf                                                    # Verify/repair
```

### pdftk (if available)
```bash
pdftk file1.pdf file2.pdf cat output merged.pdf    # Merge
pdftk input.pdf burst                              # Split
pdftk input.pdf rotate 1east output rotated.pdf    # Rotate
```

### Image Conversion (poppler-utils)
```bash
pdftoppm -png -r 300 document.pdf output_prefix       # High-res PNG
pdftoppm -jpeg -jpegopt quality=85 -r 200 doc.pdf out # JPEG with quality
pdfimages -j input.pdf output_prefix                   # Extract embedded images
pdfimages -list document.pdf                           # List image info
```

## Common Tasks

### Extract Text from Scanned PDFs (OCR)
```python
import pytesseract
from pdf2image import convert_from_path

images = convert_from_path('scanned.pdf')
text = ""
for i, image in enumerate(images):
    text += f"Page {i+1}:\n"
    text += pytesseract.image_to_string(image)
    text += "\n\n"
```

### Add Watermark
```python
from pypdf import PdfReader, PdfWriter

watermark = PdfReader("watermark.pdf").pages[0]
reader = PdfReader("document.pdf")
writer = PdfWriter()

for page in reader.pages:
    page.merge_page(watermark)
    writer.add_page(page)

with open("watermarked.pdf", "wb") as output:
    writer.write(output)
```

### Password Protection
```python
from pypdf import PdfReader, PdfWriter

reader = PdfReader("input.pdf")
writer = PdfWriter()
for page in reader.pages:
    writer.add_page(page)

writer.encrypt("userpassword", "ownerpassword")
with open("encrypted.pdf", "wb") as output:
    writer.write(output)
```

### Advanced Cropping
```python
from pypdf import PdfWriter, PdfReader

reader = PdfReader("input.pdf")
writer = PdfWriter()
page = reader.pages[0]
page.mediabox.left = 50
page.mediabox.bottom = 50
page.mediabox.right = 550
page.mediabox.top = 750
writer.add_page(page)
with open("cropped.pdf", "wb") as output:
    writer.write(output)
```

### Batch Processing
```python
import os, glob
from pypdf import PdfReader, PdfWriter
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def batch_process_pdfs(input_dir, operation='merge'):
    pdf_files = glob.glob(os.path.join(input_dir, "*.pdf"))
    if operation == 'merge':
        writer = PdfWriter()
        for pdf_file in pdf_files:
            try:
                reader = PdfReader(pdf_file)
                for page in reader.pages:
                    writer.add_page(page)
            except Exception as e:
                logger.error(f"Failed to process {pdf_file}: {e}")
                continue
        with open("batch_merged.pdf", "wb") as output:
            writer.write(output)
```

## Quick Reference

| Task | Best Tool | Command/Code |
|------|-----------|--------------|
| Merge PDFs | pypdf | `writer.add_page(page)` |
| Split PDFs | pypdf | One page per file |
| Extract text | pdfplumber | `page.extract_text()` |
| Extract tables | pdfplumber | `page.extract_tables()` |
| Create PDFs | reportlab | Canvas or Platypus |
| Command line merge | qpdf | `qpdf --empty --pages ...` |
| OCR scanned PDFs | pytesseract | Convert to image first |
| Fill PDF forms | pdf-lib or pypdf | See pdf-forms.instructions.md |
| Render to images | pypdfium2 | `page.render(scale=2.0)` |

## Performance Tips

- **Large PDFs**: Use streaming; `qpdf --split-pages` for splitting; process pages individually with pypdfium2
- **Text extraction**: `pdftotext -bbox-layout` is fastest; pdfplumber for structured data/tables
- **Image extraction**: `pdfimages` is much faster than rendering pages
- **Memory**: Process PDFs in chunks of 10 pages for very large files

## License Information

- **pypdf**: BSD | **pdfplumber**: MIT | **pypdfium2**: Apache/BSD | **reportlab**: BSD
- **poppler-utils**: GPL-2 | **qpdf**: Apache | **pdf-lib**: MIT | **pdfjs-dist**: Apache
