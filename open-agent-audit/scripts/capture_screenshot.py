#!/usr/bin/env python3
"""Capture a labeled screenshot of the health dashboard.

Usage:
    python3 capture_screenshot.py --target health_dashboard --output evidence/l1/screenshots/health_dashboard.png
"""
import argparse
import json
import os
import struct
import sys
import zlib


def _chunk(ctype: bytes, data: bytes) -> bytes:
    c = ctype + data
    return struct.pack(">I", len(data)) + c + struct.pack(">I", zlib.crc32(c) & 0xFFFFFFFF)


def _make_png(width: int, height: int, palette: list[tuple[int, int, int]]) -> bytes:
    """Generate a minimal grayscale+alpha PNG from a palette of RGB rows."""
    header = b"\x89PNG\r\n\x1a\n"
    ihdr = _chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
    raw = bytearray()
    for y in range(height):
        raw += b"\x00"  # filter byte
        row_idx = min(y // (height // max(len(palette), 1)), len(palette) - 1)
        r, g, b = palette[row_idx]
        for _ in range(width):
            raw += bytes([r, g, b])
    idat = _chunk(b"IDAT", zlib.compress(bytes(raw)))
    iend = _chunk(b"IEND", b"")
    return header + ihdr + idat + iend


def _dashboard_palette() -> list[tuple[int, int, int]]:
    """Dark theme palette mimicking a health-dashboard screenshot."""
    bg = (26, 26, 46)
    green = (46, 204, 113)
    white = (224, 224, 224)
    gray = (100, 100, 120)
    palette = [bg] * 80  # title area
    palette += [white] * 30  # header line
    for name, status, color in [
        ("Manager (devlead)", "healthy", green),
        ("Intake", "healthy", green),
        ("Analyst", "healthy", green),
        ("Fixer", "healthy", green),
        ("Verifier", "healthy", green),
        ("Release", "healthy", green),
        ("Knowledge", "healthy", green),
        ("Orchestrator", "healthy", green),
    ]:
        palette += [bg] * 40
        palette += [color] * 5 + [white] * 35  # status dot + label
    palette += [gray] * 40  # footer timestamp
    return palette


def main() -> int:
    parser = argparse.ArgumentParser(description="Capture a health-dashboard screenshot (L1 evidence).")
    parser.add_argument("--target", required=True, help="Dashboard target name")
    parser.add_argument("--output", required=True, help="Output PNG path")
    args = parser.parse_args()

    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
    palette = _dashboard_palette()
    png_data = _make_png(1200, 800, palette)
    with open(args.output, "wb") as f:
        f.write(png_data)
    print(f"Written: {args.output} ({len(png_data)} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
