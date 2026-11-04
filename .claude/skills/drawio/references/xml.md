# Editable draw.io XML

Use an uncompressed `mxfile` containing one `diagram` and `mxGraphModel` per page.
Every page has its own `root`, root cell `0`, and default layer cell `1`.
Give nodes stable IDs, `vertex="1"`, a parent layer, and `mxGeometry`. Give edges
`edge="1"`, existing source/target IDs and relative geometry. Escape XML attribute
values (`&amp;`, `&lt;`, `&quot;`); label text is content, never executable markup.

```xml
<mxfile host="app.diagrams.net">
  <diagram id="architecture" name="Architecture">
    <mxGraphModel dx="800" dy="600" grid="1" gridSize="10">
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0"/>
        <mxCell id="client" value="Client" style="rounded=1;whiteSpace=wrap;html=0;"
                vertex="1" parent="1">
          <mxGeometry x="60" y="80" width="140" height="60" as="geometry"/>
        </mxCell>
        <mxCell id="service" value="Service" style="rounded=1;whiteSpace=wrap;html=0;"
                vertex="1" parent="1">
          <mxGeometry x="280" y="80" width="140" height="60" as="geometry"/>
        </mxCell>
        <mxCell id="request" value="Request" edge="1" parent="1"
                source="client" target="service" style="edgeStyle=orthogonalEdgeStyle;">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
```

Keep labels short, use consistent dimensions/spacing, group related components,
and avoid crossing connectors. Inspect at readable zoom after rendering. For
existing compressed diagrams, use an available editor to save uncompressed XML
before surgical edits; never replace unknown pages with a fresh one-page diagram.

The sibling URL helper validates this uncompressed structure, IDs and edge
references, then encodes XML as URI-escaped, raw-DEFLATE, base64 in a `#R` fragment.
It does not render, upload, open a browser, or overwrite the source.

For exports, inspect the installed desktop CLI's `--help`. Where supported:
`drawio --export --format svg --embed-diagram --output diagram.svg diagram.drawio`.
Use the corresponding PNG/PDF format only when supported. Check the result and
retain the editable source. Do not claim a successful export solely from exit 0.

Official format references, checked 2026-09-04:
[editable formats](https://www.drawio.com/docs/manual/editor/save-file-formats/),
[export formats and embedded data](https://www.drawio.com/docs/manual/export/export-diagram/),
[desktop CLI implementation](https://github.com/jgraph/drawio-desktop/blob/dev/src/main/electron.js).
