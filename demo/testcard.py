#!/usr/bin/env python3
"""Static ANSI test card: a rendered Markdown document, for judging terminal shaders.

Covers full-bleed edges, hard color edges, flat color fields, 1-cell detail,
the full luminance range, and saturated per-channel content.
"""

import random
import re
import shutil
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", newline="\n")
except (AttributeError, ValueError):
    pass

E = "\x1b["
R = E + "0m"
BOLD, DIM, IT, UND, STRIKE, REV = (E + c + "m" for c in ("1", "2", "3", "4", "9", "7"))

ANSI = re.compile(r"\x1b\[[0-9;]*m")


def fg(c):
    return f"{E}38;2;{c[0]};{c[1]};{c[2]}m"


def bg(c):
    return f"{E}48;2;{c[0]};{c[1]};{c[2]}m"


def vis(s):
    return ANSI.sub("", s)


def pad(s, w, ch=" "):
    n = w - len(vis(s))
    return s + ch * n if n > 0 else s


C = {
    "h1": (255, 121, 198), "h2": (189, 147, 249), "h3": (139, 233, 253),
    "h4": (80, 250, 123), "h5": (241, 250, 140), "h6": (255, 184, 108),
    "ink": (230, 234, 240), "dim": (130, 138, 152), "faint": (74, 80, 92),
    "link": (97, 175, 239), "str": (152, 195, 121), "num": (209, 154, 102),
    "kw": (198, 120, 221), "fn": (97, 175, 239), "com": (98, 104, 116),
    "ok": (152, 195, 121), "warn": (229, 192, 123), "err": (224, 108, 117),
    "quote": (95, 135, 175), "border": (72, 78, 90),
    "codebg": (32, 35, 43), "tabbg": (44, 48, 58),
}

PY_KW = {
    "def", "class", "return", "if", "elif", "else", "for", "while", "import", "from",
    "as", "with", "not", "in", "is", "None", "True", "False", "lambda", "try",
    "except", "finally", "yield", "raise", "pass", "assert", "and", "or", "global",
}
SH_KW = {"sudo", "apt", "pip", "git", "wsl", "cd", "ls", "export", "if", "then", "fi", "for", "do", "done"}

TOK = re.compile(
    r"(#[^\n]*)"                                    # comment
    r'|("(?:[^"\\]|\\.)*"|\'(?:[^\'\\]|\\.)*\')'    # string
    r"|(\b\d+(?:\.\d+)?\b)"                         # number
    r"|([A-Za-z_]\w*)(?=\()"                        # call
    r"|([A-Za-z_]\w*)"                              # word
    r"|(\s+)|(.)"                                   # space, other
)


def highlight(line, kws):
    out = ""
    for m in TOK.finditer(line):
        comment, string, number, call, word, space, other = m.groups()
        if comment:
            out += fg(C["com"]) + IT + comment + R
        elif string:
            out += fg(C["str"]) + string + R
        elif number:
            out += fg(C["num"]) + number + R
        elif call:
            out += fg(C["fn"]) + call + R
        elif word:
            out += fg(C["kw"]) + BOLD + word + R if word in kws else fg(C["ink"]) + word + R
        elif space:
            out += space
        else:
            out += fg(C["dim"]) + other + R
    return out


def colorbar(width):
    bars = [
        (0, 0, 0), (128, 0, 0), (0, 128, 0), (128, 128, 0), (0, 0, 128), (128, 0, 128),
        (0, 128, 128), (192, 192, 192), (128, 128, 128), (255, 0, 0), (0, 255, 0),
        (255, 255, 0), (0, 0, 255), (255, 0, 255), (0, 255, 255), (255, 255, 255),
    ]
    w, rem = divmod(width, len(bars))
    return "".join(bg(c) + " " * (w + (1 if i < rem else 0)) for i, c in enumerate(bars)) + R


def gradient(width, stops):
    s = ""
    for x in range(width):
        t = x / (width - 1) * (len(stops) - 1)
        i = int(t)
        f = t - i
        a, b = stops[i], stops[min(i + 1, len(stops) - 1)]
        s += fg(tuple(round(a[k] + (b[k] - a[k]) * f) for k in range(3))) + "\u2588"
    return s + R


def octant(x, width):
    """One eighth of the width, for a stepped luminance strip."""
    return max(1, round(width / 8))


def heading(level, text):
    col = fg(C[f"h{level}"])
    mark = fg(C["faint"]) + "#" * level + R
    body = (BOLD if level <= 2 else "") + col + text + R
    used = 4 + level + len(text)
    rule = fg(C["faint"]) + "\u2500" * max(0, W - used)
    return f"  {mark} {body} {rule}" if W - used > 0 else f"  {mark} {body}"


def para(*segs):
    return "  " + "".join(segs)


def quote(lines):
    out = []
    for i, line in enumerate(lines):
        out.append(f"  {fg(C['quote'])}\u2502{R} {fg(C['dim'])}{IT}{line}{R}")
    return out


def item(marker, text, depth=0, mcol="dim"):
    ind = "  " + "  " * depth
    return f"{ind}{fg(C[mcol])}{marker}{R} {text}"


def table(headers, rows, aligns):
    widths = [
        max([len(vis(h))] + [len(vis(r[i])) for r in rows]) for i, h in enumerate(headers)
    ]
    b = fg(C["border"])

    def border(l, m, r):
        return b + l + m.join("\u2500" * (w + 2) for w in widths) + r + R

    def line(cells):
        parts = []
        for i, cell in enumerate(cells):
            gap = widths[i] - len(vis(cell))
            if aligns[i] == "r":
                cell = " " + " " * gap + cell
            elif aligns[i] == "c":
                cell = " " + " " * (gap // 2) + cell + " " * (gap - gap // 2)
            else:
                cell = " " + cell + " " * gap
            parts.append(cell + " ")
        return b + "\u2502" + R + (b + "\u2502" + R).join(parts) + b + "\u2502" + R

    out = [border("\u250c", "\u252c", "\u2510")]
    out.append(line([BOLD + fg(C["h3"]) + h + R for h in headers]))
    out.append(border("\u251c", "\u253c", "\u2524"))
    out += [line(r) for r in rows]
    out.append(border("\u2514", "\u2534", "\u2518"))
    return ["  " + l for l in out]


def code_block(lines, lang, kws):
    out = [bg(C["tabbg"]) + pad(f"  {fg(C['dim'])}{lang}{R}", W) + R]
    for line in lines:
        out.append(bg(C["codebg"]) + pad("  " + highlight(line, kws), W) + R)
    out.append(bg(C["codebg"]) + pad(" ", W) + R)
    return out


def cube():
    vals = (0, 95, 135, 175, 215, 255)
    out = []
    for r in range(6):
        s = "  "
        for g in range(6):
            for b in range(6):
                s += fg((vals[r], vals[g], vals[b])) + "\u2588\u2588"
        out.append(s + R)
    return out


def grays():
    steps = [8 + 10 * i for i in range(24)]
    return "  " + "".join(fg((v, v, v)) + "\u2588\u2588" for v in steps) + R


def pluge():
    near_black = [0, 3, 6, 9, 12, 16, 20, 24]
    near_white = [231, 236, 241, 246, 251, 255]
    left = "  " + "".join(bg((v, v, v)) + "   " for v in near_black) + R
    right = "".join(bg((v, v, v)) + "   " for v in near_white) + R
    return left, right


def main():
    global W
    cols, rows = shutil.get_terminal_size((100, 40))
    W = min(max(cols, 80), 110)

    out = ["", colorbar(cols), gradient(cols, [
        (0, 0, 0), (12, 40, 18), (0, 140, 60), (60, 255, 140), (235, 255, 245),
    ]), ""]

    out += [
        para(fg(C["faint"]) + "\u256d" + "\u2500" * (W - 4) + "\u256e" + R),
        para(f"{fg(C['faint'])}\u2502{R}"
             + pad(f"  {BOLD}{fg(C['h3'])}MARKDOWN ANSI TEST CARD{R}"
                   f"  {fg(C['dim'])}\u2014  shader / renderer reference{R}", W - 4)
             + f"{fg(C['faint'])}\u2502{R}"),
        para(fg(C["faint"]) + "\u2570" + "\u2500" * (W - 4) + "\u256f" + R),
        "",
    ]

    out.append(heading(1, "Heading level 1 \u2014 the loudest thing on screen"))
    out.append(heading(2, "Heading level 2 \u2014 slightly quieter"))
    out.append(heading(3, "Heading level 3 \u2014 cyan, mid contrast"))
    out.append(heading(4, "Heading level 4 \u2014 green"))
    out.append(heading(5, "Heading level 5 \u2014 yellow"))
    out.append(heading(6, "Heading level 6 \u2014 orange, smallest"))
    out.append("")

    out.append(para(
        fg(C["ink"]) + "Body text " + R + BOLD + fg(C["ink"]) + "bold" + R
        + fg(C["ink"]) + ", " + IT + "italic" + R + fg(C["ink"]) + ", " + BOLD + IT + "bold italic" + R
        + fg(C["ink"]) + ", " + bg(C["codebg"]) + fg(C["h1"]) + "inline_code()" + R
        + fg(C["ink"]) + ", " + STRIKE + fg(C["dim"]) + "deleted" + R
        + fg(C["ink"]) + ", and a " + UND + fg(C["link"]) + "link" + R + "."
    ))
    out.append(para(
        fg(C["dim"]) + "Glyphs: \u2192 \u2713 \u2717 \u25cf \u25cb \u25aa \u2500 \u2502 \u250c \u2588 \u2591 \u2592 \u2593"
        + " \u00b6 \u2020 \u00a7 \u00b5 \u00e9 \u00df \u00f1" + R
    ))
    out.append(para(
        fg(C["dim"]) + "Density: "
        + fg(C["ink"]) + "MW@#%&" + fg(C["dim"]) + " \u2593\u2592\u2591 \u00b7\u2022. " 
        + fg(C["ink"]) + "illlIII" + R
    ))
    out.append("")

    out += quote([
        "A shader sees a cell grid, not glyphs. Bloom, scanlines and chroma",
        "bleed all read as changes in this block, so it is the first thing",
        "to check when an effect looks wrong but you cannot say why.",
        "Nested note: \u2014 the bar on the left is one cell wide, in its own hue.",
    ])
    out.append("")

    out.append(item("\u2022", fg(C["ink"]) + "string" + R + fg(C["dim"]) + " \u2014 undecorated foreground" + R))
    out.append(item("\u2022", fg(C["ink"]) + "number" + R + fg(C["dim"]) + " \u2014 distinct hue, same weight" + R, 1))
    out.append(item("\u2022", fg(C["ink"]) + "boolean" + R + fg(C["dim"]) + " \u2014 nested two deep" + R, 2))
    out.append(item("\u2022", bg(C["codebg"]) + fg(C["h1"]) + "padded_background" + R + fg(C["dim"]) + " \u2014 flat fill with text" + R))
    out.append(item("1.", fg(C["ink"]) + "ordered" + R + fg(C["dim"]) + " \u2014 counted list" + R))
    out.append(item("2.", fg(C["ink"]) + "ordered again" + R + fg(C["dim"]) + " \u2014 alignment check" + R))
    out.append(item("\u2713", fg(C["ok"]) + "done" + R + fg(C["dim"]) + " \u2014 completed task" + R, 0, "ok"))
    out.append(item("\u2610", fg(C["warn"]) + "open" + R + fg(C["dim"]) + " \u2014 pending task" + R, 0, "warn"))
    out.append("")

    ok = fg(C["ok"]) + "\u2713" + R
    warn = fg(C["warn"]) + "?" + R
    err = fg(C["err"]) + "\u2717" + R
    out += table(
        ["Token", "SGR", "Support", "Notes"],
        [
            [fg(C["h3"]) + "24-bit" + R, fg(C["num"]) + "38;2;r;g;b" + R, ok,
             fg(C["dim"]) + "truecolor path" + R],
            [fg(C["h3"]) + "256-color" + R, fg(C["num"]) + "38;5;n" + R, ok,
             fg(C["dim"]) + "cube + 232\u2013255 ramp" + R],
            [fg(C["h3"]) + "16-color" + R, fg(C["num"]) + "30\u201337, 90\u201397" + R, ok,
             fg(C["dim"]) + "fallback floor" + R],
            [fg(C["h3"]) + "italic" + R, fg(C["num"]) + "3" + R, warn,
             fg(C["dim"]) + "font dependent" + R],
            [fg(C["h3"]) + "blink" + R, fg(C["num"]) + "5" + R, err,
             fg(C["dim"]) + "usually dropped" + R],
        ],
        ["l", "l", "c", "l"],
    )
    out.append("")

    out += code_block([
        "def rain(cols=80, fps=30):",
        '    """Column heads drift; the tail erases behind them."""',
        "    heads = [random.randrange(-24, 0) for _ in range(cols)]",
        "    for frame in range(1000):",
        "        for x, y in enumerate(heads):",
        '            paint(x, y, glyph(), glow=(y == heads[x]))',
        "            heads[x] += 1",
        '        if heads[x] > rows + 16:   # drained past the bottom',
        "            heads[x] = -random.randrange(1, 12)",
        "        sleep(1 / fps)",
    ], "python", PY_KW)

    out += code_block([
        "$ sudo apt install -y cmatrix   # ~12 KB, no deps",
        "$ cmatrix -ab -u 2              # async + bold heads",
        "$ wsl --install -d Ubuntu       # not docker-desktop",
    ], "bash", SH_KW)
    out.append("")

    out.append("  " + fg(C["border"]) + "\u2500" * (W - 2) + R)
    out.append("")

    def chip(label, fgc, bgc):
        return f"{bg(bgc)}{fg(fgc)}{BOLD} {label} {R}"

    out.append("  " + chip("build", (18, 20, 26), (152, 195, 121)) + " "
               + chip("coverage 91%", (18, 20, 26), (229, 192, 123)) + " "
               + chip("license MIT", (235, 240, 248), (60, 120, 216)) + " "
               + chip("shader probe", (235, 240, 248), (170, 70, 140)))
    out.append("")

    out.append("  " + fg(C["dim"]) + "6\u00d76\u00d76 color cube (216 cells)" + R)
    out += cube()
    out.append("  " + fg(C["dim"]) + "grayscale ramp 232\u2013255 (24 cells)" + R)
    out.append(grays())
    out.append("")
    out.append("  " + fg(C["dim"]) + "near-black / near-white steps \u2014 black crush check" + R)
    left, right = pluge()
    out.append(left + "   " + right)
    out.append("")

    out.append("  " + fg(C["dim"]) + "Attributes:" + R
               + " " + BOLD + fg(C["ink"]) + "bold" + R
               + " " + DIM + fg(C["ink"]) + "dim" + R
               + " " + IT + fg(C["ink"]) + "italic" + R
               + " " + UND + fg(C["ink"]) + "underline" + R
               + " " + STRIKE + fg(C["ink"]) + "strike" + R
               + " " + REV + " reverse " + R)
    out.append("")

    sys.stdout.write(E + "2J" + E + "H" + E + "0m")
    sys.stdout.write("\n".join(out) + R + "\n")


if __name__ == "__main__":
    main()
