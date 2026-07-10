---
name: drawio
description: "Generate native draw.io diagrams as .drawio XML files, with optional app.diagrams.net URLs and draw.io Desktop exports. Use when the user asks for draw.io, diagrams.net, flowcharts, sequence diagrams, ER diagrams, class diagrams, architecture diagrams, or editable diagram files. Prefer this over Mermaid when the requested output must remain editable in draw.io."
---

# Draw.io

Create native `.drawio` files by writing mxGraph XML directly. Do not require MCP or network access.

Read `references/xml-generation.md` before generating non-trivial diagrams. Use `scripts/drawio_tools.py` to wrap, validate, URL-encode, or export diagrams.

## Workflow

1. Determine the diagram type, intended filename, and requested output: `.drawio` default, `url`, `png`, `svg`, or `pdf`.
2. Generate an `mxGraphModel` with stable IDs, readable labels, and explicit geometry.
3. Run `python3 scripts/drawio_tools.py wrap --input model.xml --output name.drawio` if the generated file is only an `mxGraphModel`; otherwise write a full `mxfile` directly.
4. For `url`, run `python3 scripts/drawio_tools.py url --input name.drawio` and give the user the URL.
5. For image/PDF export, run `python3 scripts/drawio_tools.py export --input name.drawio --format png|svg|pdf` only when draw.io Desktop is installed; otherwise leave the `.drawio` file and explain the missing exporter.
6. Keep the `.drawio` source unless the user explicitly asks for only the exported artifact.

## Native Codex Notes

- Use normal Codex file editing for the output diagram file.
- Use the script for deterministic wrapping and URL compression instead of hand-encoding.
- Request approval before opening a browser or GUI app.
- Do not browse or install dependencies unless the user explicitly asks.
