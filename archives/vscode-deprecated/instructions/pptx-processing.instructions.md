---
applyTo: "**"
description: "PowerPoint (.pptx) creation, editing, design guidance, visual QA, template workflows, PptxGenJS"
---

# PPTX Processing

> **Prerequisites:** This skill requires `pptxgenjs` (npm) and `Pillow` (Python/uv). Run `/setup-common-prompts` to check and install missing dependencies.

Use these instructions any time a .pptx file is involved — creating slide decks, reading/extracting text, editing existing presentations, combining/splitting files, working with templates, layouts, speaker notes, or comments. Trigger whenever "deck", "slides", "presentation", or a .pptx filename is mentioned.

## Quick Reference

| Task | Guide |
|------|-------|
| Read/analyze content | `python -m markitdown presentation.pptx` |
| Edit or create from template | See [Editing Workflow](#editing-workflow) |
| Create from scratch | See [Creating from Scratch with PptxGenJS](#creating-from-scratch-with-pptxgenjs) |

---

## Reading Content

```bash
python -m markitdown presentation.pptx           # Text extraction
python scripts/thumbnail.py presentation.pptx     # Visual overview
python scripts/office/unpack.py presentation.pptx unpacked/  # Raw XML
```

---

## Design Ideas

**Don't create boring slides.** Plain bullets on a white background won't impress anyone.

### Before Starting

- **Pick a bold, content-informed color palette**: If swapping your colors into a completely different presentation would still "work," you haven't made specific enough choices.
- **Dominance over equality**: One color should dominate (60-70% visual weight), with 1-2 supporting tones and one sharp accent.
- **Dark/light contrast**: Dark backgrounds for title + conclusion slides, light for content. Or commit to dark throughout for premium feel.
- **Commit to a visual motif**: Pick ONE distinctive element and repeat it — rounded frames, icons in circles, thick single-side borders.

### Color Palettes

| Theme | Primary | Secondary | Accent |
|-------|---------|-----------|--------|
| Midnight Executive | `1E2761` | `CADCFC` | `FFFFFF` |
| Forest & Moss | `2C5F2D` | `97BC62` | `F5F5F5` |
| Coral Energy | `F96167` | `F9E795` | `2F3C7E` |
| Warm Terracotta | `B85042` | `E7E8D1` | `A7BEAE` |
| Ocean Gradient | `065A82` | `1C7293` | `21295C` |
| Charcoal Minimal | `36454F` | `F2F2F2` | `212121` |
| Teal Trust | `028090` | `00A896` | `02C39A` |
| Berry & Cream | `6D2E46` | `A26769` | `ECE2D0` |
| Sage Calm | `84B59F` | `69A297` | `50808E` |
| Cherry Bold | `990011` | `FCF6F5` | `2F3C7E` |

### For Each Slide

**Every slide needs a visual element** — image, chart, icon, or shape. Text-only slides are forgettable.

**Layout options:**
- Two-column (text left, illustration right)
- Icon + text rows (icon in colored circle, bold header, description)
- 2x2 or 2x3 grid
- Half-bleed image with content overlay

**Data display:**
- Large stat callouts (big numbers 60-72pt with small labels)
- Comparison columns (before/after, pros/cons)
- Timeline or process flow (numbered steps, arrows)

### Typography

| Header Font | Body Font |
|-------------|-----------|
| Georgia | Calibri |
| Arial Black | Arial |
| Cambria | Calibri |
| Trebuchet MS | Calibri |
| Palatino | Garamond |

| Element | Size |
|---------|------|
| Slide title | 36-44pt bold |
| Section header | 20-24pt bold |
| Body text | 14-16pt |
| Captions | 10-12pt muted |

### Spacing

- 0.5" minimum margins
- 0.3-0.5" between content blocks
- Leave breathing room

### Avoid (Common Mistakes)

- Don't repeat the same layout — vary columns, cards, callouts
- Don't center body text — left-align paragraphs and lists
- Don't skimp on size contrast — titles need 36pt+ vs 14-16pt body
- Don't default to blue — pick topic-specific colors
- Don't mix spacing randomly
- Don't style one slide and leave the rest plain
- Don't create text-only slides
- Don't forget text box padding (`margin: 0` when aligning with shapes)
- Don't use low-contrast elements
- **NEVER use accent lines under titles** — hallmark of AI-generated slides

---

## Editing Workflow

### Template-Based Workflow

1. **Analyze existing slides**:
   ```bash
   python scripts/thumbnail.py template.pptx
   python -m markitdown template.pptx
   ```

2. **Plan slide mapping**: Match content type to layout style. **USE VARIED LAYOUTS** — don't repeat the same text-heavy layout. Seek out multi-column, image + text, quote slides, stat callouts, section dividers.

3. **Unpack**: `python scripts/office/unpack.py template.pptx unpacked/`

4. **Build presentation** (structural changes):
   - Delete unwanted slides (remove from `<p:sldIdLst>`)
   - Duplicate slides: `python scripts/add_slide.py unpacked/ slide2.xml`
   - Reorder slides in `<p:sldIdLst>`
   - **Complete all structural changes before editing content**

5. **Edit content**: Update text in each `slide{N}.xml`

6. **Clean**: `python scripts/clean.py unpacked/`

7. **Pack**: `python scripts/office/pack.py unpacked/ output.pptx --original template.pptx`

### Scripts

| Script | Purpose |
|--------|---------|
| `scripts/office/unpack.py` | Extract and pretty-print PPTX |
| `scripts/add_slide.py` | Duplicate slide or create from layout |
| `scripts/clean.py` | Remove orphaned files |
| `scripts/office/pack.py` | Repack with validation |
| `scripts/thumbnail.py` | Create visual grid of slides |

### Slide Operations

- **Reorder**: Rearrange `<p:sldId>` elements in `ppt/presentation.xml`
- **Delete**: Remove `<p:sldId>`, then run `clean.py`
- **Add**: Use `add_slide.py` — never manually copy slide files

### Formatting Rules

- **Bold all headers, subheadings, and inline labels**: `b="1"` on `<a:rPr>`
- **Never use unicode bullets**: Use `<a:buChar>` or `<a:buAutoNum>`
- **Bullet consistency**: Let bullets inherit from layout

### Common Pitfalls

- **Template slots != source items**: If template has 4 items but source has 3, delete the 4th item's entire group (image + text boxes)
- **Multi-item content**: Create separate `<a:p>` elements — never concatenate into one string
- **Smart quotes**: Use XML entities (`&#x201C;`, `&#x201D;`, `&#x2018;`, `&#x2019;`)
- **Whitespace**: Use `xml:space="preserve"` on `<a:t>` with leading/trailing spaces
- **XML parsing**: Use `defusedxml.minidom`, not `xml.etree.ElementTree` (corrupts namespaces)

---

## Creating from Scratch with PptxGenJS

Install: `npm install -g pptxgenjs`

### Setup

```javascript
const pptxgen = require("pptxgenjs");

let pres = new pptxgen();
pres.layout = 'LAYOUT_16x9';  // 10" x 5.625"
pres.author = 'Your Name';
pres.title = 'Presentation Title';

let slide = pres.addSlide();
slide.addText("Hello World!", { x: 0.5, y: 0.5, fontSize: 36, color: "363636" });

pres.writeFile({ fileName: "Presentation.pptx" });
```

### Layout Dimensions (inches)

- `LAYOUT_16x9`: 10" x 5.625" (default)
- `LAYOUT_16x10`: 10" x 6.25"
- `LAYOUT_4x3`: 10" x 7.5"
- `LAYOUT_WIDE`: 13.3" x 7.5"

### Text & Formatting

```javascript
slide.addText("Simple Text", {
  x: 1, y: 1, w: 8, h: 2, fontSize: 24, fontFace: "Arial",
  color: "363636", bold: true, align: "center", valign: "middle"
});

// Character spacing (use charSpacing, not letterSpacing)
slide.addText("SPACED TEXT", { x: 1, y: 1, w: 8, h: 1, charSpacing: 6 });

// Rich text
slide.addText([
  { text: "Bold ", options: { bold: true } },
  { text: "Italic ", options: { italic: true } }
], { x: 1, y: 3, w: 8, h: 1 });

// Multi-line (requires breakLine: true)
slide.addText([
  { text: "Line 1", options: { breakLine: true } },
  { text: "Line 2", options: { breakLine: true } },
  { text: "Line 3" }
], { x: 0.5, y: 0.5, w: 8, h: 2 });
```

**Tip:** Set `margin: 0` when aligning text with shapes or icons.

### Lists & Bullets

```javascript
// CORRECT: Multiple bullets
slide.addText([
  { text: "First item", options: { bullet: true, breakLine: true } },
  { text: "Second item", options: { bullet: true, breakLine: true } },
  { text: "Third item", options: { bullet: true } }
], { x: 0.5, y: 0.5, w: 8, h: 3 });

// WRONG: Never use unicode bullets
slide.addText("• First item", { ... });  // Creates double bullets

// Sub-items and numbered lists
{ text: "Sub-item", options: { bullet: true, indentLevel: 1 } }
{ text: "First", options: { bullet: { type: "number" }, breakLine: true } }
```

### Shapes

```javascript
slide.addShape(pres.shapes.RECTANGLE, {
  x: 0.5, y: 0.8, w: 1.5, h: 3.0,
  fill: { color: "FF0000" }, line: { color: "000000", width: 2 }
});

slide.addShape(pres.shapes.LINE, {
  x: 1, y: 3, w: 5, h: 0, line: { color: "FF0000", width: 3, dashType: "dash" }
});

// Rounded rectangle (rectRadius only works with ROUNDED_RECTANGLE)
slide.addShape(pres.shapes.ROUNDED_RECTANGLE, {
  x: 1, y: 1, w: 3, h: 2, fill: { color: "FFFFFF" }, rectRadius: 0.1
});

// With shadow
slide.addShape(pres.shapes.RECTANGLE, {
  x: 1, y: 1, w: 3, h: 2, fill: { color: "FFFFFF" },
  shadow: { type: "outer", color: "000000", blur: 6, offset: 2, angle: 135, opacity: 0.15 }
});
```

**Shadow options:**

| Property | Range | Notes |
|----------|-------|-------|
| `type` | `"outer"`, `"inner"` | |
| `color` | 6-char hex | No `#` prefix, no 8-char hex |
| `blur` | 0-100 pt | |
| `offset` | 0-200 pt | Must be non-negative |
| `angle` | 0-359 degrees | 135 = bottom-right, 270 = upward |
| `opacity` | 0.0-1.0 | Use this for transparency |

### Images

```javascript
// From file, URL, or base64
slide.addImage({ path: "images/chart.png", x: 1, y: 1, w: 5, h: 3 });
slide.addImage({ data: "image/png;base64,iVBORw0KGgo...", x: 1, y: 1, w: 5, h: 3 });

// With options
slide.addImage({
  path: "image.png", x: 1, y: 1, w: 5, h: 3,
  rounding: true, transparency: 50, altText: "Description"
});

// Sizing modes
{ sizing: { type: 'contain', w: 4, h: 3 } }  // Fit inside
{ sizing: { type: 'cover', w: 4, h: 3 } }    // Fill area (may crop)
```

### Icons (react-icons → PNG)

```javascript
const React = require("react");
const ReactDOMServer = require("react-dom/server");
const sharp = require("sharp");
const { FaCheckCircle } = require("react-icons/fa");

function renderIconSvg(IconComponent, color = "#000000", size = 256) {
  return ReactDOMServer.renderToStaticMarkup(
    React.createElement(IconComponent, { color, size: String(size) })
  );
}

async function iconToBase64Png(IconComponent, color, size = 256) {
  const svg = renderIconSvg(IconComponent, color, size);
  const pngBuffer = await sharp(Buffer.from(svg)).png().toBuffer();
  return "image/png;base64," + pngBuffer.toString("base64");
}

const iconData = await iconToBase64Png(FaCheckCircle, "#4472C4", 256);
slide.addImage({ data: iconData, x: 1, y: 1, w: 0.5, h: 0.5 });
```

Install: `npm install -g react-icons react react-dom sharp`

### Slide Backgrounds

```javascript
slide.background = { color: "F1F1F1" };
slide.background = { path: "https://example.com/bg.jpg" };
slide.background = { data: "image/png;base64,..." };
```

### Tables

```javascript
slide.addTable([
  ["Header 1", "Header 2"],
  ["Cell 1", "Cell 2"]
], { x: 1, y: 1, w: 8, h: 2, border: { pt: 1, color: "999999" }, fill: { color: "F1F1F1" } });

// With merged cells and styling
let tableData = [
  [{ text: "Header", options: { fill: { color: "6699CC" }, color: "FFFFFF", bold: true } }, "Cell"],
  [{ text: "Merged", options: { colspan: 2 } }]
];
slide.addTable(tableData, { x: 1, y: 3.5, w: 8, colW: [4, 4] });
```

### Charts

```javascript
// Bar chart
slide.addChart(pres.charts.BAR, [{
  name: "Sales", labels: ["Q1", "Q2", "Q3", "Q4"], values: [4500, 5500, 6200, 7100]
}], {
  x: 0.5, y: 0.6, w: 6, h: 3, barDir: 'col',
  showTitle: true, title: 'Quarterly Sales'
});

// Better-looking chart
slide.addChart(pres.charts.BAR, chartData, {
  x: 0.5, y: 1, w: 9, h: 4, barDir: "col",
  chartColors: ["0D9488", "14B8A6", "5EEAD4"],
  chartArea: { fill: { color: "FFFFFF" }, roundedCorners: true },
  catAxisLabelColor: "64748B", valAxisLabelColor: "64748B",
  valGridLine: { color: "E2E8F0", size: 0.5 }, catGridLine: { style: "none" },
  showValue: true, dataLabelPosition: "outEnd", dataLabelColor: "1E293B",
  showLegend: false,
});
```

### Slide Masters

```javascript
pres.defineSlideMaster({
  title: 'TITLE_SLIDE', background: { color: '283A5E' },
  objects: [{
    placeholder: { options: { name: 'title', type: 'title', x: 1, y: 2, w: 8, h: 2 } }
  }]
});
let titleSlide = pres.addSlide({ masterName: "TITLE_SLIDE" });
titleSlide.addText("My Title", { placeholder: "title" });
```

### PptxGenJS Critical Pitfalls

1. **NEVER use "#" with hex colors** — causes file corruption: `"FF0000"` not `"#FF0000"`
2. **NEVER encode opacity in hex** — 8-char colors corrupt: use `opacity` property instead
3. **Use `bullet: true`** — NEVER unicode "•" (creates double bullets)
4. **Use `breakLine: true`** between array items
5. **Avoid `lineSpacing` with bullets** — use `paraSpaceAfter` instead
6. **Each presentation needs fresh instance** — don't reuse `pptxgen()` objects
7. **NEVER reuse option objects** — PptxGenJS mutates them in-place. Use factory functions.
8. **Don't use ROUNDED_RECTANGLE with accent borders** — rectangular overlays won't cover corners

---

## QA (Required)

**Assume there are problems. Your job is to find them.**

### Content QA

```bash
python -m markitdown output.pptx
```

Check for missing content, typos, wrong order.

**Check for leftover placeholder text:**
```bash
python -m markitdown output.pptx | grep -iE "xxxx|lorem|ipsum|this.*(page|slide).*layout"
```

### Visual QA

Convert to images, then inspect each slide:

```bash
python scripts/office/soffice.py --headless --convert-to pdf output.pptx
pdftoppm -jpeg -r 150 output.pdf slide
```

Look for:
- Overlapping elements
- Text overflow or cut off
- Elements too close (< 0.3" gaps)
- Uneven gaps
- Insufficient margin from edges (< 0.5")
- Low-contrast text or icons
- Leftover placeholder content

### Verification Loop

1. Generate → Convert to images → Inspect
2. List issues found
3. Fix issues
4. Re-verify affected slides
5. Repeat until clean

**Do not declare success until at least one fix-and-verify cycle.**

---

## Converting to Images

```bash
python scripts/office/soffice.py --headless --convert-to pdf output.pptx
pdftoppm -jpeg -r 150 output.pdf slide
```

Creates `slide-01.jpg`, `slide-02.jpg`, etc.

Re-render specific slides:
```bash
pdftoppm -jpeg -r 150 -f N -l N output.pdf slide-fixed
```

---

## Dependencies

- `pip install "markitdown[pptx]"` — text extraction
- `pip install Pillow` — thumbnail grids
- `npm install -g pptxgenjs` — creating from scratch
- `npm install -g react-icons react react-dom sharp` — icons
- LibreOffice (`soffice`) — PDF conversion
- Poppler (`pdftoppm`) — PDF to images
