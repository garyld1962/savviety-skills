#!/usr/bin/env python3
"""Validate uncompressed draw.io XML and print an editor URL without network I/O."""
import argparse
import base64
from pathlib import Path
import sys
from urllib.parse import quote
import xml.etree.ElementTree as ET
import zlib


def editor_url(text):
    root = ET.fromstring(text)
    if root.tag not in ("mxfile", "mxGraphModel"):
        raise ValueError("expected mxfile or mxGraphModel")
    graphs = [root] if root.tag == "mxGraphModel" else root.findall("diagram/mxGraphModel")
    if not graphs or (root.tag == "mxfile" and len(graphs) != len(root.findall("diagram"))):
        raise ValueError("every page must contain an uncompressed mxGraphModel")
    for graph in graphs:
        graph_root = graph.find("root")
        if graph_root is None:
            raise ValueError("mxGraphModel requires a root element")
        cells = graph.findall(".//mxCell")
        if any(not cell.get("id") for cell in cells):
            raise ValueError("this helper requires explicit IDs on every mxCell")
        ids = [e.attrib["id"] for e in graph.iter() if "id" in e.attrib]
        if len(ids) != len(set(ids)) or not {"0", "1"}.issubset(ids):
            raise ValueError("page has duplicate IDs or missing root/layer cells 0 and 1")
        if graph_root.find("mxCell[@id='0']") is None or graph_root.find("mxCell[@id='1'][@parent='0']") is None:
            raise ValueError("root requires cell 0 and layer cell 1 with parent 0")
        vertices = {cell.get("id") for cell in cells if cell.get("vertex") == "1"}
        for cell in cells:
            for attribute in ("parent", "source", "target"):
                if attribute in cell.attrib and cell.attrib[attribute] not in ids:
                    raise ValueError(f"dangling {attribute}: {cell.attrib[attribute]}")
            if cell.get("edge") == "1" and not all(cell.get(k) for k in ("source", "target")):
                raise ValueError("edges require explicit source and target nodes")
            if cell.get("edge") == "1" and any(cell.get(k) not in vertices for k in ("source", "target")):
                raise ValueError("edge endpoints must refer to vertices, not roots or layers")
    encoded = quote(text, safe="~()*!.'-").encode("utf-8")
    compressor = zlib.compressobj(wbits=-15)
    payload = compressor.compress(encoded) + compressor.flush()
    return "https://app.diagrams.net/#R" + base64.b64encode(payload).decode("ascii")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    args = parser.parse_args()
    try:
        print(editor_url(args.source.read_text(encoding="utf-8")))
        return 0
    except (OSError, UnicodeError, ET.ParseError, ValueError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
