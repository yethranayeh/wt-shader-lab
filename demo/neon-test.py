#!/usr/bin/env python3
"""Glow test pattern: the cases a bloom shader gets wrong.

The same stroke at four brightness levels, one-pixel strokes, solid blocks where
a halo can only appear at the edges, the full black-to-white ramp, the ANSI
palette, and a realistic log block.
"""

import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", newline="\n")
except (AttributeError, ValueError):
    pass

RESET = "\x1b[0m"
GREY = "\x1b[38;2;120;120;120m"
BLOCK = "\u2588"


def fg(rgb):
    r, g, b = rgb
    return f"\x1b[38;2;{r};{g};{b}m"


def scaled(rgb, k):
    return tuple(int(v * k) for v in rgb)


COLORS = [
    ("red", (255, 40, 40)),
    ("lime", (140, 255, 40)),
    ("green", (40, 255, 90)),
    ("cyan", (40, 240, 255)),
    ("blue", (70, 120, 255)),
    ("magenta", (255, 60, 220)),
    ("amber", (255, 176, 0)),
    ("white", (235, 235, 235)),
]

print()
print(GREY + "-- 1. same stroke at 25% / 50% / 75% / 100% brightness" + RESET)
for name, rgb in COLORS:
    print(
        f"{name:<8}"
        + fg(scaled(rgb, 0.25)) + "MMMMMMMM  "
        + fg(scaled(rgb, 0.50)) + "MMMMMMMM  "
        + fg(scaled(rgb, 0.75)) + "MMMMMMMM  "
        + fg(rgb) + "MMMMMMMM"
        + RESET
    )

print()
print(GREY + "-- 2. one-pixel strokes: worst case for a blur-based glow" + RESET)
for name, rgb in COLORS:
    print(f"{name:<8}" + fg(rgb) + ("| " * 24) + RESET)

print()
print(GREY + "-- 3. solid blocks: halo can only appear at the edges" + RESET)
for name, rgb in COLORS:
    print(f"{name:<8}" + fg(rgb) + BLOCK * 8 + RESET)

print()
print(GREY + "-- 4. black to white ramp: glow should show on the right half" + RESET)
print("".join(fg((v, v, v)) + BLOCK for v in range(0, 256, 6)) + RESET)

print()
print(GREY + "-- 5. standard ANSI palette, normal then bright" + RESET)
print("".join(f"\x1b[{30 + i}m{BLOCK * 5}" for i in range(8)) + RESET)
print("".join(f"\x1b[{90 + i}m{BLOCK * 5}" for i in range(8)) + RESET)

print()
print(GREY + "-- 6. what your agent panes actually emit" + RESET)
print(fg((90, 200, 255)) + "2026-11-12T13:50:01Z " + fg((120, 255, 120)) + "INFO " + fg((200, 200, 200)) + "agent session started" + RESET)
print(fg((90, 200, 255)) + "2026-11-12T13:50:04Z " + fg((255, 200, 60)) + "WARN " + fg((200, 200, 200)) + "retrying tool call (2/3)" + RESET)
print(fg((90, 200, 255)) + "2026-11-12T13:50:06Z " + fg((255, 70, 70)) + "ERROR" + fg((200, 200, 200)) + " connection reset by peer" + RESET)
print(fg((120, 255, 120)) + "+ added line, bright green, should glow" + RESET)
print(fg((255, 90, 90)) + "- removed line, bright red, should glow" + RESET)
print(fg((130, 130, 130)) + "  context line: dim on purpose, should stay matte" + RESET)
print(fg((235, 235, 235)) + "plain white output, the most common case" + RESET)
print()
