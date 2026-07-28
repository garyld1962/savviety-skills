#!/usr/bin/env python3
from __future__ import annotations

import argparse
import base64
import shutil
import subprocess
import sys
import urllib.parse
import zlib
from pathlib import Path
from xml.etree import ElementTree as ET


def main() -> int:
    parser = argparse.ArgumentParser(description="Draw.io helper tools.")
    sub = parser.add_subparsers(dest="cmd", required=True)

    wrap = sub.add_parser("wrap", help="Wrap an mxGraphModel in an mxfile.")
    wrap.add_argument("--input", required=True)
    wrap.add_argument("--output", required=True)
    wrap.add_argument("--name", default="Page-1")

    validate = sub.add_parser("validate", help="Validate draw.io XML parses.")
    validate.add_argument("--input", required=True)

    url = sub.add_parser("url", help="Print an app.diagrams.net URL for a diagram.")
    url.add_argument("--input", required=True)

    export = sub.add_parser("export", help="Export via draw.io Desktop CLI.")
    export.add_argument("--input", required=True)
    export.add_argument("--format", required=True, choices=["png", "svg", "pdf"])
    export.add_argument("--output")

    args = parser.parse_args()
    if args.cmd == "wrap":
        return wrap_model(Path(args.input), Path(args.output), args.name)
    if args.cmd == "validate":
        return validate_xml(Path(args.input))
    if args.cmd == "url":
        return print_url(Path(args.input))
    if args.cmd == "export":
        return export_diagram(Path(args.input), args.format, Path(args.output) if args.output else None)
    return 2


def wrap_model(input_path: Path, output_path: Path, page_name: str) -> int:
    model_text = input_path.read_text(encoding="utf-8").strip()
    root = ET.fromstring(model_text)
    if root.tag == "mxfile":
        output_path.write_text(model_text + "\n", encoding="utf-8")
        return 0
    if root.tag != "mxGraphModel":
        print(f"{input_path}: expected mxGraphModel or mxfile, got {root.tag}", file=sys.stderr)
        return 1

    mxfile = ET.Element("mxfile", {"host": "app.diagrams.net"})
    diagram = ET.SubElement(mxfile, "diagram", {"name": page_name})
    diagram.append(root)
    ET.indent(mxfile)
    output_path.write_text(ET.tostring(mxfile, encoding="unicode") + "\n", encoding="utf-8")
    return 0


def validate_xml(path: Path) -> int:
    try:
        root = ET.fromstring(path.read_text(encoding="utf-8"))
    except ET.ParseError as exc:
        print(f"{path}: XML parse failed: {exc}", file=sys.stderr)
        return 1
    if root.tag not in {"mxfile", "mxGraphModel"}:
        print(f"{path}: expected mxfile or mxGraphModel, got {root.tag}", file=sys.stderr)
        return 1
    print(f"{path}: valid {root.tag}")
    return 0


def print_url(path: Path) -> int:
    xml = path.read_text(encoding="utf-8")
    ET.fromstring(xml)
    escaped = urllib.parse.quote(xml, safe="~()*!.'")
    compressed = zlib.compressobj(level=9, wbits=-15)
    raw = compressed.compress(escaped.encode("utf-8")) + compressed.flush()
    encoded = base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")
    print(f"https://app.diagrams.net/#R{encoded}")
    return 0


def export_diagram(path: Path, fmt: str, output: Path | None) -> int:
    executable = find_drawio()
    if not executable:
        print("draw.io Desktop CLI was not found on PATH.", file=sys.stderr)
        return 1
    output_path = output or path.with_suffix(path.suffix + f".{fmt}")
    cmd = [executable, "--export", "--format", fmt, "--output", str(output_path), str(path)]
    proc = subprocess.run(cmd, text=True)
    return proc.returncode


def find_drawio() -> str | None:
    for name in ["drawio", "draw.io", "drawio-desktop"]:
        found = shutil.which(name)
        if found:
            return found
    return None


if __name__ == "__main__":
    raise SystemExit(main())
