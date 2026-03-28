---
applyTo: "**"
description: "Word document (.docx) creation, editing, and manipulation: tracked changes, comments, tables, images, headers/footers, TOC"
---

# DOCX Creation, Editing, and Analysis

> **Prerequisites:** This skill requires `docx` (npm) and `pandoc` (CLI). Run `/setup-common-prompts` to check and install missing dependencies.

Use these instructions when creating, reading, editing, or manipulating Word documents (.docx files). This includes: mentions of 'Word doc', '.docx', professional documents with formatting like tables of contents, headings, page numbers, or letterheads. Also for extracting content from .docx files, working with tracked changes or comments, or converting content into a polished Word document.

## Overview

A .docx file is a ZIP archive containing XML files.

## Quick Reference

| Task | Approach |
|------|----------|
| Read/analyze content | `pandoc` or unpack for raw XML |
| Create new document | Use `docx-js` (npm `docx` package) |
| Edit existing document | Unpack → edit XML → repack |

### Converting .doc to .docx

Legacy `.doc` files must be converted before editing:
```bash
python scripts/office/soffice.py --headless --convert-to docx document.doc
```

### Reading Content

```bash
# Text extraction with tracked changes
pandoc --track-changes=all document.docx -o output.md

# Raw XML access
python scripts/office/unpack.py document.docx unpacked/
```

### Converting to Images

```bash
python scripts/office/soffice.py --headless --convert-to pdf document.docx
pdftoppm -jpeg -r 150 document.pdf page
```

### Accepting Tracked Changes

```bash
python scripts/accept_changes.py input.docx output.docx
```

---

## Creating New Documents

Generate .docx files with JavaScript using the `docx` npm package, then validate.

Install: `npm install -g docx`

### Setup

```javascript
const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, ImageRun,
        Header, Footer, AlignmentType, PageOrientation, LevelFormat, ExternalHyperlink,
        InternalHyperlink, Bookmark, FootnoteReferenceRun, PositionalTab,
        PositionalTabAlignment, PositionalTabRelativeTo, PositionalTabLeader,
        TabStopType, TabStopPosition, Column, SectionType,
        TableOfContents, HeadingLevel, BorderStyle, WidthType, ShadingType,
        VerticalAlign, PageNumber, PageBreak } = require('docx');

const doc = new Document({ sections: [{ children: [/* content */] }] });
Packer.toBuffer(doc).then(buffer => fs.writeFileSync("doc.docx", buffer));
```

### Validation

After creating, validate. If validation fails, unpack, fix XML, and repack.
```bash
python scripts/office/validate.py doc.docx
```

### Page Size

```javascript
// CRITICAL: docx-js defaults to A4, not US Letter
// Always set page size explicitly
sections: [{
  properties: {
    page: {
      size: {
        width: 12240,   // 8.5 inches in DXA
        height: 15840   // 11 inches in DXA
      },
      margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 } // 1 inch margins
    }
  },
  children: [/* content */]
}]
```

**Common page sizes (DXA units, 1440 DXA = 1 inch):**

| Paper | Width | Height | Content Width (1" margins) |
|-------|-------|--------|---------------------------|
| US Letter | 12,240 | 15,840 | 9,360 |
| A4 (default) | 11,906 | 16,838 | 9,026 |

**Landscape orientation:** Pass portrait dimensions and let docx-js handle the swap:
```javascript
size: {
  width: 12240,   // Pass SHORT edge as width
  height: 15840,  // Pass LONG edge as height
  orientation: PageOrientation.LANDSCAPE
},
```

### Styles (Override Built-in Headings)

Use Arial as the default font. Keep titles black.

```javascript
const doc = new Document({
  styles: {
    default: { document: { run: { font: "Arial", size: 24 } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 32, bold: true, font: "Arial" },
        paragraph: { spacing: { before: 240, after: 240 }, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 28, bold: true, font: "Arial" },
        paragraph: { spacing: { before: 180, after: 180 }, outlineLevel: 1 } },
    ]
  },
  sections: [{
    children: [
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("Title")] }),
    ]
  }]
});
```

### Lists (NEVER use unicode bullets)

```javascript
// WRONG - never manually insert bullet characters
new Paragraph({ children: [new TextRun("• Item")] })  // BAD

// CORRECT - use numbering config with LevelFormat.BULLET
const doc = new Document({
  numbering: {
    config: [
      { reference: "bullets",
        levels: [{ level: 0, format: LevelFormat.BULLET, text: "\u2022", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
      { reference: "numbers",
        levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
    ]
  },
  sections: [{
    children: [
      new Paragraph({ numbering: { reference: "bullets", level: 0 },
        children: [new TextRun("Bullet item")] }),
      new Paragraph({ numbering: { reference: "numbers", level: 0 },
        children: [new TextRun("Numbered item")] }),
    ]
  }]
});

// Each reference creates INDEPENDENT numbering
// Same reference = continues (1,2,3 then 4,5,6)
// Different reference = restarts (1,2,3 then 1,2,3)
```

### Tables

**CRITICAL: Tables need dual widths** — set both `columnWidths` on the table AND `width` on each cell.

```javascript
// CRITICAL: Always use WidthType.DXA (percentages break in Google Docs)
// CRITICAL: Use ShadingType.CLEAR (not SOLID) to prevent black backgrounds
const border = { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" };
const borders = { top: border, bottom: border, left: border, right: border };

new Table({
  width: { size: 9360, type: WidthType.DXA },
  columnWidths: [4680, 4680],
  rows: [
    new TableRow({
      children: [
        new TableCell({
          borders,
          width: { size: 4680, type: WidthType.DXA },
          shading: { fill: "D5E8F0", type: ShadingType.CLEAR },
          margins: { top: 80, bottom: 80, left: 120, right: 120 },
          children: [new Paragraph({ children: [new TextRun("Cell")] })]
        })
      ]
    })
  ]
})
```

**Width rules:**
- Always use `WidthType.DXA` — never `WidthType.PERCENTAGE`
- Table width = sum of `columnWidths`
- Cell `width` must match corresponding `columnWidth`
- Cell `margins` are internal padding (reduce content area, not add to cell width)
- Full-width tables: use content width (page width minus left and right margins)

### Images

```javascript
// CRITICAL: type parameter is REQUIRED
new Paragraph({
  children: [new ImageRun({
    type: "png",
    data: fs.readFileSync("image.png"),
    transformation: { width: 200, height: 150 },
    altText: { title: "Title", description: "Desc", name: "Name" }
  })]
})
```

### Page Breaks

```javascript
// PageBreak must be inside a Paragraph
new Paragraph({ children: [new PageBreak()] })
new Paragraph({ pageBreakBefore: true, children: [new TextRun("New page")] })
```

### Hyperlinks

```javascript
// External link
new Paragraph({
  children: [new ExternalHyperlink({
    children: [new TextRun({ text: "Click here", style: "Hyperlink" })],
    link: "https://example.com",
  })]
})

// Internal link (bookmark + reference)
new Paragraph({ heading: HeadingLevel.HEADING_1, children: [
  new Bookmark({ id: "chapter1", children: [new TextRun("Chapter 1")] }),
]})
new Paragraph({ children: [new InternalHyperlink({
  children: [new TextRun({ text: "See Chapter 1", style: "Hyperlink" })],
  anchor: "chapter1",
})]})
```

### Footnotes

```javascript
const doc = new Document({
  footnotes: {
    1: { children: [new Paragraph("Source: Annual Report 2024")] },
    2: { children: [new Paragraph("See appendix for methodology")] },
  },
  sections: [{
    children: [new Paragraph({
      children: [
        new TextRun("Revenue grew 15%"),
        new FootnoteReferenceRun(1),
        new TextRun(" using adjusted metrics"),
        new FootnoteReferenceRun(2),
      ],
    })]
  }]
});
```

### Tab Stops

```javascript
// Right-align text on same line
new Paragraph({
  children: [new TextRun("Company Name"), new TextRun("\tJanuary 2025")],
  tabStops: [{ type: TabStopType.RIGHT, position: TabStopPosition.MAX }],
})

// Dot leader (TOC-style)
new Paragraph({
  children: [
    new TextRun("Introduction"),
    new TextRun({ children: [
      new PositionalTab({
        alignment: PositionalTabAlignment.RIGHT,
        relativeTo: PositionalTabRelativeTo.MARGIN,
        leader: PositionalTabLeader.DOT,
      }),
      "3",
    ]}),
  ],
})
```

### Multi-Column Layouts

```javascript
sections: [{
  properties: {
    column: { count: 2, space: 720, equalWidth: true, separate: true },
  },
  children: [/* content flows across columns */]
}]

// Custom widths (equalWidth: false)
column: {
  equalWidth: false,
  children: [new Column({ width: 5400, space: 720 }), new Column({ width: 3240 })],
},
```

### Table of Contents

```javascript
// CRITICAL: Headings must use HeadingLevel ONLY - no custom styles
new TableOfContents("Table of Contents", { hyperlink: true, headingStyleRange: "1-3" })
```

### Headers/Footers

```javascript
sections: [{
  properties: {
    page: { margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 } }
  },
  headers: {
    default: new Header({ children: [new Paragraph({ children: [new TextRun("Header")] })] })
  },
  footers: {
    default: new Footer({ children: [new Paragraph({
      children: [new TextRun("Page "), new TextRun({ children: [PageNumber.CURRENT] })]
    })] })
  },
  children: [/* content */]
}]
```

### Critical Rules for docx-js

- **Set page size explicitly** — defaults to A4; use US Letter (12240 x 15840 DXA) for US documents
- **Landscape: pass portrait dimensions** — docx-js swaps width/height internally
- **Never use `\n`** — use separate Paragraph elements
- **Never use unicode bullets** — use `LevelFormat.BULLET` with numbering config
- **PageBreak must be in Paragraph** — standalone creates invalid XML
- **ImageRun requires `type`** — always specify png/jpg/etc
- **Always use DXA for table widths** — never `WidthType.PERCENTAGE` (breaks in Google Docs)
- **Tables need dual widths** — `columnWidths` array AND cell `width`, both must match
- **Always add cell margins** — `margins: { top: 80, bottom: 80, left: 120, right: 120 }`
- **Use `ShadingType.CLEAR`** — never SOLID for table shading
- **Never use tables as dividers/rules** — use `border: { bottom: ... }` on a Paragraph instead
- **TOC requires HeadingLevel only** — no custom styles on heading paragraphs
- **Override built-in styles** — use exact IDs: "Heading1", "Heading2", etc.
- **Include `outlineLevel`** — required for TOC (0 for H1, 1 for H2, etc.)

---

## Editing Existing Documents

**Follow all 3 steps in order.**

### Step 1: Unpack

```bash
python scripts/office/unpack.py document.docx unpacked/
```

Extracts XML, pretty-prints, merges adjacent runs, and converts smart quotes to XML entities.

### Step 2: Edit XML

Edit files in `unpacked/word/`.

**Use "Claude" as the author** for tracked changes and comments unless the user specifies otherwise.

**CRITICAL: Use smart quotes for new content.** Use XML entities:
```xml
<w:t>Here&#x2019;s a quote: &#x201C;Hello&#x201D;</w:t>
```

| Entity | Character |
|--------|-----------|
| `&#x2018;` | ' (left single) |
| `&#x2019;` | ' (right single / apostrophe) |
| `&#x201C;` | " (left double) |
| `&#x201D;` | " (right double) |

**Adding comments:**
```bash
python scripts/comment.py unpacked/ 0 "Comment text with &amp; and &#x2019;"
python scripts/comment.py unpacked/ 1 "Reply text" --parent 0
python scripts/comment.py unpacked/ 0 "Text" --author "Custom Author"
```

Then add markers to document.xml.

### Step 3: Pack

```bash
python scripts/office/pack.py unpacked/ output.docx --original document.docx
```

Validates with auto-repair, condenses XML, and creates DOCX.

**Auto-repair fixes:** `durableId` overflow, missing `xml:space="preserve"`.

**Auto-repair won't fix:** Malformed XML, invalid nesting, missing relationships, schema violations.

### Common Pitfalls

- **Replace entire `<w:r>` elements** when adding tracked changes — don't inject tracked change tags inside a run
- **Preserve `<w:rPr>` formatting** — copy the original run's formatting into tracked change runs

---

## XML Reference

### Schema Compliance

- **Element order in `<w:pPr>`**: `<w:pStyle>`, `<w:numPr>`, `<w:spacing>`, `<w:ind>`, `<w:jc>`, `<w:rPr>` last
- **Whitespace**: Add `xml:space="preserve"` to `<w:t>` with leading/trailing spaces
- **RSIDs**: Must be 8-digit hex (e.g., `00AB1234`)

### Tracked Changes

**Insertion:**
```xml
<w:ins w:id="1" w:author="Claude" w:date="2025-01-01T00:00:00Z">
  <w:r><w:t>inserted text</w:t></w:r>
</w:ins>
```

**Deletion (use `<w:delText>` not `<w:t>`):**
```xml
<w:del w:id="2" w:author="Claude" w:date="2025-01-01T00:00:00Z">
  <w:r><w:delText>deleted text</w:delText></w:r>
</w:del>
```

**Minimal edits — only mark what changes:**
```xml
<w:r><w:t>The term is </w:t></w:r>
<w:del w:id="1" w:author="Claude" w:date="...">
  <w:r><w:delText>30</w:delText></w:r>
</w:del>
<w:ins w:id="2" w:author="Claude" w:date="...">
  <w:r><w:t>60</w:t></w:r>
</w:ins>
<w:r><w:t> days.</w:t></w:r>
```

**Deleting entire paragraphs** — mark paragraph mark as deleted:
```xml
<w:p>
  <w:pPr>
    <w:rPr>
      <w:del w:id="1" w:author="Claude" w:date="2025-01-01T00:00:00Z"/>
    </w:rPr>
  </w:pPr>
  <w:del w:id="2" w:author="Claude" w:date="2025-01-01T00:00:00Z">
    <w:r><w:delText>Entire paragraph content...</w:delText></w:r>
  </w:del>
</w:p>
```

**Rejecting another author's insertion:**
```xml
<w:ins w:author="Jane" w:id="5">
  <w:del w:author="Claude" w:id="10">
    <w:r><w:delText>their inserted text</w:delText></w:r>
  </w:del>
</w:ins>
```

**Restoring another author's deletion:**
```xml
<w:del w:author="Jane" w:id="5">
  <w:r><w:delText>deleted text</w:delText></w:r>
</w:del>
<w:ins w:author="Claude" w:id="10">
  <w:r><w:t>deleted text</w:t></w:r>
</w:ins>
```

### Comments

**CRITICAL: `<w:commentRangeStart>` and `<w:commentRangeEnd>` are siblings of `<w:r>`, never inside `<w:r>`.**

```xml
<w:commentRangeStart w:id="0"/>
<w:r><w:t>commented text</w:t></w:r>
<w:commentRangeEnd w:id="0"/>
<w:r><w:rPr><w:rStyle w:val="CommentReference"/></w:rPr><w:commentReference w:id="0"/></w:r>

<!-- Nested reply -->
<w:commentRangeStart w:id="0"/>
  <w:commentRangeStart w:id="1"/>
  <w:r><w:t>text</w:t></w:r>
  <w:commentRangeEnd w:id="1"/>
<w:commentRangeEnd w:id="0"/>
<w:r><w:rPr><w:rStyle w:val="CommentReference"/></w:rPr><w:commentReference w:id="0"/></w:r>
<w:r><w:rPr><w:rStyle w:val="CommentReference"/></w:rPr><w:commentReference w:id="1"/></w:r>
```

### Images in XML

1. Add image file to `word/media/`
2. Add relationship to `word/_rels/document.xml.rels`:
   ```xml
   <Relationship Id="rId5" Type=".../image" Target="media/image1.png"/>
   ```
3. Add content type to `[Content_Types].xml`:
   ```xml
   <Default Extension="png" ContentType="image/png"/>
   ```
4. Reference in document.xml (EMUs: 914400 = 1 inch):
   ```xml
   <w:drawing>
     <wp:inline>
       <wp:extent cx="914400" cy="914400"/>
       <a:graphic>
         <a:graphicData uri=".../picture">
           <pic:pic>
             <pic:blipFill><a:blip r:embed="rId5"/></pic:blipFill>
           </pic:pic>
         </a:graphicData>
       </a:graphic>
     </wp:inline>
   </w:drawing>
   ```

---

## Dependencies

- **pandoc**: Text extraction
- **docx**: `npm install -g docx` (new documents)
- **LibreOffice**: PDF conversion (via `scripts/office/soffice.py`)
- **Poppler**: `pdftoppm` for images
