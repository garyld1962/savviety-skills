# Draw.io XML Generation

Generate native draw.io files as XML. A minimal file is:

```xml
<mxfile host="app.diagrams.net">
  <diagram name="Page-1">
    <mxGraphModel dx="1200" dy="800" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1100" pageHeight="850" math="0" shadow="0">
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0"/>
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
```

## Cells

- Vertices use `vertex="1"` and a child `mxGeometry` with `x`, `y`, `width`, and `height`.
- Edges use `edge="1"`, `source`, `target`, and `mxGeometry relative="1" as="geometry"`.
- Use stable semantic IDs such as `start`, `auth-service`, or `order-db`.
- Escape labels with XML entities: `&amp;`, `&lt;`, `&gt;`, `&quot;`.
- Keep labels short. Put detail in separate note shapes.

## Common Styles

- Rounded process: `rounded=1;whiteSpace=wrap;html=1;arcSize=8;`
- Decision: `rhombus;whiteSpace=wrap;html=1;`
- Database: `shape=cylinder3d;whiteSpace=wrap;html=1;boundedLbl=1;backgroundOutline=1;size=15;`
- Actor: `shape=umlActor;verticalLabelPosition=bottom;verticalAlign=top;html=1;`
- Container: `swimlane;whiteSpace=wrap;html=1;startSize=28;collapsible=0;`
- Dashed dependency: `endArrow=block;html=1;rounded=0;dashed=1;`

## Layout

- Use a 40px minimum gap between shapes and a 120px minimum lane gap.
- Flowcharts usually read left-to-right for service flows and top-to-bottom for procedures.
- Put databases and external systems on the right or bottom edge.
- Use containers for bounded contexts, deployment zones, or packages.
- Avoid crossing edges; add waypoints inside `Array as="points"` when needed.

## Diagram Patterns

Flowchart:

```xml
<mxCell id="start" value="Start" style="ellipse;whiteSpace=wrap;html=1;" vertex="1" parent="1">
  <mxGeometry x="80" y="120" width="100" height="50" as="geometry"/>
</mxCell>
<mxCell id="step" value="Validate input" style="rounded=1;whiteSpace=wrap;html=1;arcSize=8;" vertex="1" parent="1">
  <mxGeometry x="260" y="110" width="150" height="70" as="geometry"/>
</mxCell>
<mxCell id="e1" value="" style="endArrow=block;html=1;rounded=0;" edge="1" parent="1" source="start" target="step">
  <mxGeometry relative="1" as="geometry"/>
</mxCell>
```

Sequence-style diagrams can be represented with actor/service boxes across the top, dashed vertical lifelines, and horizontal message edges. Use monotonically increasing y positions for message order.

ER diagrams should use table-like rectangles with field lists in the `value`; use crow-foot labels (`1`, `0..*`) near edge ends when needed.

## Quality Checks

- The XML must parse.
- Every edge source and target must reference an existing cell.
- Every visible vertex should have nonzero geometry.
- The resulting `.drawio` should open without conversion.
