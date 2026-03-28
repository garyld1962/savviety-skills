---
applyTo: "**"
description: "PDF form filling: fillable fields, non-fillable annotation-based filling, coordinate extraction, validation"
---

# PDF Form Filling Guide

> **Prerequisites:** This skill requires `pdf-lib` (npm). Run `/setup-common-prompts` to check and install missing dependencies.

Use these instructions when filling out PDF forms. First determine if the PDF has fillable form fields, then follow the appropriate workflow.

**CRITICAL: Complete these steps in order. Do not skip ahead to writing code.**

## Step 0: Check for Fillable Fields

```bash
python scripts/check_fillable_fields.py <file.pdf>
```

Based on the result, follow either the **Fillable Fields** or **Non-Fillable Fields** workflow below.

---

## Fillable Fields Workflow

If the PDF has fillable form fields:

### 1. Extract Field Info

```bash
python scripts/extract_form_field_info.py <input.pdf> <field_info.json>
```

Creates a JSON file with field details:
```json
[
  {
    "field_id": "last_name",
    "page": 1,
    "rect": [100, 200, 300, 220],
    "type": "text"
  },
  {
    "field_id": "Checkbox12",
    "page": 1,
    "type": "checkbox",
    "checked_value": "/On",
    "unchecked_value": "/Off"
  },
  {
    "field_id": "gender",
    "page": 1,
    "type": "radio_group",
    "radio_options": [
      { "value": "/Male", "rect": [100, 300, 112, 312] },
      { "value": "/Female", "rect": [150, 300, 162, 312] }
    ]
  },
  {
    "field_id": "state",
    "page": 1,
    "type": "choice",
    "choice_options": [
      { "value": "CA", "text": "California" },
      { "value": "NY", "text": "New York" }
    ]
  }
]
```

### 2. Analyze the Form Visually

Convert PDF to images to understand each field's purpose:
```bash
python scripts/convert_pdf_to_images.py <file.pdf> <output_directory>
```

Analyze the images to determine what each field expects, matching bounding box PDF coordinates to image coordinates.

### 3. Create field_values.json

```json
[
  {
    "field_id": "last_name",
    "description": "The user's last name",
    "page": 1,
    "value": "Simpson"
  },
  {
    "field_id": "Checkbox12",
    "description": "Checkbox for 18+ confirmation",
    "page": 1,
    "value": "/On"
  }
]
```

- `field_id` must match the ID from `extract_form_field_info.py`
- For checkboxes, use `checked_value` to check, `unchecked_value` to uncheck
- For radio groups, use one of the `value` entries from `radio_options`

### 4. Fill the Form

```bash
python scripts/fill_fillable_fields.py <input.pdf> <field_values.json> <output.pdf>
```

The script validates field IDs and values; fix any reported errors and retry.

---

## Non-Fillable Fields Workflow

For PDFs without fillable form fields, add text annotations. Try structure extraction first (more accurate), then fall back to visual estimation.

### Step 1: Try Structure Extraction

```bash
python scripts/extract_form_structure.py <input.pdf> form_structure.json
```

Creates JSON containing:
- **labels**: Text elements with exact coordinates (x0, top, x1, bottom in PDF points)
- **lines**: Horizontal lines defining row boundaries
- **checkboxes**: Small square rectangles with center coordinates
- **row_boundaries**: Row top/bottom positions from horizontal lines

If `form_structure.json` has meaningful labels, use **Approach A**. If the PDF is scanned/image-based with few/no labels, use **Approach B**.

---

### Approach A: Structure-Based Coordinates (Preferred)

Use when `extract_form_structure.py` found text labels.

**Analyze the structure:**
1. **Label groups**: Adjacent text elements forming a single label (e.g., "Last" + "Name")
2. **Row structure**: Labels with similar `top` values are in the same row
3. **Field columns**: Entry areas start after label ends (x0 = label.x1 + gap)
4. **Checkboxes**: Use coordinates directly from the structure

**Coordinate system**: PDF coordinates where y=0 is at TOP of page, y increases downward.

**Calculate entry coordinates:**
- Text fields: entry x0 = label x1 + 5; entry x1 = next label's x0 or row boundary
- Checkboxes: use checkbox rectangle coordinates directly

**Check for missing elements**: Structure extraction may miss circular checkboxes, complex graphics, or faded elements. Use visual analysis (Approach B) for those specific fields.

**Create fields.json with PDF coordinates:**
```json
{
  "pages": [
    {"page_number": 1, "pdf_width": 612, "pdf_height": 792}
  ],
  "form_fields": [
    {
      "page_number": 1,
      "description": "Last name entry field",
      "field_label": "Last Name",
      "label_bounding_box": [43, 63, 87, 73],
      "entry_bounding_box": [92, 63, 260, 79],
      "entry_text": {"text": "Smith", "font_size": 10}
    },
    {
      "page_number": 1,
      "description": "US Citizen Yes checkbox",
      "field_label": "Yes",
      "label_bounding_box": [260, 200, 280, 210],
      "entry_bounding_box": [285, 197, 292, 205],
      "entry_text": {"text": "X"}
    }
  ]
}
```

Use `pdf_width`/`pdf_height` and coordinates from form_structure.json.

---

### Approach B: Visual Estimation (Fallback)

Use when PDF is scanned/image-based and structure extraction found no usable labels.

**1. Convert PDF to images:**
```bash
python scripts/convert_pdf_to_images.py <input.pdf> <images_dir/>
```

**2. Identify fields**: Examine each page image for form sections, labels, entry areas, checkboxes. Note approximate pixel coordinates.

**3. Zoom refinement (CRITICAL for accuracy):**

Crop a region around each estimated position:
```bash
magick <page_image> -crop <width>x<height>+<x>+<y> +repage <crop_output.png>
```

Examine the crop to determine precise coordinates, then convert back to full image coordinates:
- full_x = crop_x + crop_offset_x
- full_y = crop_y + crop_offset_y

**4. Create fields.json with image coordinates:**
```json
{
  "pages": [
    {"page_number": 1, "image_width": 1700, "image_height": 2200}
  ],
  "form_fields": [
    {
      "page_number": 1,
      "description": "Last name entry field",
      "field_label": "Last Name",
      "label_bounding_box": [120, 175, 242, 198],
      "entry_bounding_box": [255, 175, 720, 218],
      "entry_text": {"text": "Smith", "font_size": 10}
    }
  ]
}
```

Use `image_width`/`image_height` with refined pixel coordinates.

---

### Hybrid Approach: Structure + Visual

When structure extraction works for most fields but misses some:

1. Use **Approach A** for detected fields
2. Convert PDF to images for missing fields
3. Use zoom refinement from **Approach B** for missing fields
4. Convert all coordinates to PDF coordinate system:
   - `pdf_x = image_x * (pdf_width / image_width)`
   - `pdf_y = image_y * (pdf_height / image_height)`
5. Use a single coordinate system in fields.json with `pdf_width`/`pdf_height`

---

### Validate and Fill

**Validate bounding boxes:**
```bash
python scripts/check_bounding_boxes.py fields.json
```
Checks for intersecting boxes and boxes too small for font size. Fix errors before filling.

**Fill the form:**
```bash
python scripts/fill_pdf_form_with_annotations.py <input.pdf> fields.json <output.pdf>
```

The fill script auto-detects the coordinate system and handles conversion.

**Verify output:**
```bash
python scripts/convert_pdf_to_images.py <output.pdf> <verify_images/>
```

If text is mispositioned:
- **Approach A**: Verify PDF coordinates from form_structure.json with `pdf_width`/`pdf_height`
- **Approach B**: Check image dimensions and pixel coordinate accuracy
- **Hybrid**: Ensure coordinate conversions are correct
