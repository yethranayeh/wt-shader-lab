#!/usr/bin/env python3
"""Checks that shaders sharing code actually share the same code.

house.hlsl carries the glow from neon.hlsl and the noise from grain.hlsl. Each
group below lists the symbols those files hold in common. A symbol that differs,
or is missing from one of the files, fails the check.
"""

import difflib
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

GROUPS = {
    "glow": {
        "files": ["shaders/neon.hlsl", "shaders/house.hlsl"],
        "functions": ["peak", "emit", "sampleAberrated", "glowField"],
        "defines": [
            "GLOW_STRENGTH",
            "GLOW_THRESHOLD",
            "GLOW_GAIN",
            "GLOW_STEP_PX",
            "ENABLE_CHROMATIC_ABERRATION",
            "CA_PIXELS",
        ],
        "declarations": ["glowWeights"],
    },
    "grain": {
        "files": ["shaders/grain.hlsl", "shaders/house.hlsl"],
        "functions": ["permute", "rand", "grain"],
        "defines": ["a0", "a1", "a2", "b0", "b1", "GRAIN_INTENSITY"],
    },
}


def read(rel):
    return (REPO / rel).read_text(encoding="utf-8").replace("\r\n", "\n")


def function_body(text, name):
    """Returns the function including its signature and braces, or None."""
    match = re.search(rf"^[A-Za-z_][\w\s\*]*?\b{re.escape(name)}\s*\(", text, re.MULTILINE)
    if not match:
        return None

    start = text.find("{", match.end())
    if start < 0:
        return None

    depth = 0
    for index in range(start, len(text)):
        if text[index] == "{":
            depth += 1
        elif text[index] == "}":
            depth -= 1
            if depth == 0:
                return text[match.start():index + 1]

    return None


def define_value(text, name):
    match = re.search(rf"^#define\s+{re.escape(name)}\s+(.+)$", text, re.MULTILINE)
    return match.group(1).strip() if match else None


def declaration(text, name):
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("static") and name in stripped:
            return stripped
    return None


EXTRACT = {
    "functions": function_body,
    "defines": define_value,
    "declarations": declaration,
}


def report(group, kind, name, values):
    missing = [rel for rel, value in values.items() if value is None]
    if missing:
        print(f"::error::[{group}] {kind[:-1]} {name} is missing from {', '.join(missing)}")
        return 1

    if len(set(values.values())) == 1:
        return 0

    print(f"::error::[{group}] {kind[:-1]} {name} differs between the copies")
    files = list(values)
    left, right = values[files[0]], values[files[1]]
    diff = difflib.unified_diff(
        left.splitlines(),
        right.splitlines(),
        fromfile=files[0],
        tofile=files[1],
        lineterm="",
    )
    for line in list(diff)[:24]:
        print(f"    {line}")
    return 1


def main():
    failures = 0
    checked = 0
    files = set()

    for group, spec in GROUPS.items():
        texts = {rel: read(rel) for rel in spec["files"]}
        files.update(spec["files"])

        for kind, extract in EXTRACT.items():
            for name in spec.get(kind, []):
                values = {rel: extract(text, name) for rel, text in texts.items()}
                checked += 1
                failures += report(group, kind, name, values)

    if failures:
        print(f"\n{failures} of {checked} shared symbols do not match.")
        return 1

    print(f"{checked} shared symbols match across {len(files)} shaders.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
