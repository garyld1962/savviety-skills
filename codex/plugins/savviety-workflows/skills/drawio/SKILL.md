---
name: drawio
description: "Create or edit editable draw.io diagrams, optionally export PNG/SVG/PDF with embedded diagram data, or produce a diagrams.net URL. Use when draw.io format is requested; use native text diagrams for simple explanations that need no draw.io artifact."
---

# Draw.io

## Workflow
1. Identify the relationships, desired diagram type, source artifact and output path.
   Inspect an existing diagram before editing; preserve pages, IDs, links and styling
   outside the requested change.
2. Read [XML reference](references/xml.md). Write editable, uncompressed mxGraph XML
   to a .drawio file. Use stable IDs, readable geometry and edges attached to nodes.
3. Parse the XML, check duplicate IDs and dangling edge endpoints, then inspect it in
   an available renderer/editor. XML validity alone does not prove visual quality.
4. Default to returning the editable source. For a requested image or PDF, check the
   installed draw.io desktop CLI's --help and supported flags; export with embedded
   diagram data when that format supports it. Verify the output exists and inspect it.
   Keep the .drawio source even after export. If no renderer is available, return the
   source and clearly say the requested export/visual check is still unavailable.
5. For a requested URL, use [the URL helper](scripts/drawio_url.py) with the source file.
   It creates a diagrams.net #R fragment locally, without uploading or opening it.
   A shared link contains the diagram content; do not publish or open it automatically.

## Examples
- "Make an editable architecture diagram" → create a .drawio with real components,
  ownership boundaries and labeled relationships.
- "Export this to SVG too" → retain the source, export and verify SVG if supported.

## Closed decisions and open decisions
Honor the user's notation, names and architecture. Clarify unknown relationships instead
of inventing systems. Layout choices can follow the existing diagram.

## Do not
Do not depend on absent vendor skills or MCP servers, delete editable source after
export, or silently send private diagrams to an online conversion service.

## Codex integration
Use `$drawio` explicitly or let its description match the request. Resolve sibling
skills inside this plugin. Read AGENTS.md before repository edits; honor the current
host's tool access and delegation rules. Do not require another platform's runtime.
