#!/usr/bin/env python3
"""Draws the project's icon: a glowing block cursor on the theme's background.

Writes PNG directly so the repository needs no image toolchain.
"""

import struct
import sys
import zlib
from pathlib import Path

BACKGROUND = (26, 23, 15)
ACCENT = (238, 195, 94)


def png(path, size, block):
    x0, y0, w, h = block
    radius = size * 0.075
    rows = []

    for y in range(size):
        row = bytearray([0])  # filter type: none
        for x in range(size):
            dx = max(x0 - x, x - (x0 + w - 1), 0)
            dy = max(y0 - y, y - (y0 + h - 1), 0)
            distance = (dx * dx + dy * dy) ** 0.5

            if distance == 0:
                r, g, b = ACCENT
            else:
                glow = 0.55 * pow(2.718, -distance / radius)
                r = min(255, round(BACKGROUND[0] + (ACCENT[0] - BACKGROUND[0]) * glow))
                g = min(255, round(BACKGROUND[1] + (ACCENT[1] - BACKGROUND[1]) * glow))
                b = min(255, round(BACKGROUND[2] + (ACCENT[2] - BACKGROUND[2]) * glow))
            row += bytes((r, g, b, 255))
        rows.append(bytes(row))

    raw = b"".join(rows)

    def chunk(kind, data):
        return (
            struct.pack(">I", len(data))
            + kind
            + data
            + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
        )

    header = struct.pack(">IIBBBBB", size, size, 8, 6, 0, 0, 0)
    out = (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", header)
        + chunk(b"IDAT", zlib.compress(raw, 9))
        + chunk(b"IEND", b"")
    )
    Path(path).write_bytes(out)
    print(f"{path}: {size}x{size}, {len(out)} bytes")


def main():
    # A 12-unit block in a 32-unit square, sitting low and left like a cursor.
    png("site/static/favicon.png", 32, (6, 14, 12, 12))
    png("site/static/apple-touch-icon.png", 180, (34, 79, 68, 68))
    return 0


if __name__ == "__main__":
    sys.exit(main())
