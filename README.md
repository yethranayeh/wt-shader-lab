# wt-shader-lab

Pixel shaders for Windows Terminal that stay readable.

[![Shaders](https://github.com/yethranayeh/wt-shader-lab/actions/workflows/shaders.yml/badge.svg)](https://github.com/yethranayeh/wt-shader-lab/actions/workflows/shaders.yml)
[![MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

Five looks, from barely-there to visibly damaged. All of them are single-pass
post-processes over the terminal's rendered frame: they change light, not
layout, and none of them move a glyph.

| Shader | What it does | Cost |
| --- | --- | --- |
| [`grain.hlsl`](shaders/grain.hlsl) | Film grain only. No colour shift, no geometry, no resampling. | 1 sample/px |
| [`neon.hlsl`](shaders/neon.hlsl) | Bright glyphs bloom in their own colour, with optional sub-pixel RGB split. | 36 samples/px |
| [`house.hlsl`](shaders/house.hlsl) | `neon` + grain. The everyday one. | 36 samples/px |
| [`signal-loss.hlsl`](shaders/signal-loss.hlsl) | Damaged-signal look for unfocused panes: torn bands, ghosting, bursts with RGB split. | 2 samples/px, 4 during a burst |
| [`pipboy.hlsl`](shaders/pipboy.hlsl) | Fallout Pip-Boy CRT: green phosphor, scanlines, mild curve. A tuned copy of upstream `crt.hlsl`. | 36 samples/px |

Cost is texture samples per pixel per frame.

## Install

Point `experimental.pixelShaderPath` at whichever shader you want. Per-profile is
the sane default; `profiles.defaults` applies it to everything. The examples use
`house.hlsl`.

The settings file is
`%LOCALAPPDATA%\Packages\Microsoft.WindowsTerminal_8wekyb3d8bbwe\LocalState\settings.json`
for the Store build, and `%LOCALAPPDATA%\Microsoft\Windows Terminal\settings.json`
for the unpackaged one.

Every shader is a standalone file: copy one into your own configuration and it
still works.

```jsonc
"profiles": {
  "defaults": {
    "experimental.pixelShaderPath": "C:/path/to/wt-shader-lab/shaders/house.hlsl"
  }
}
```

[`examples/settings.jsonc`](examples/settings.jsonc) is the same thing as a file
you can copy from.

Requires Windows Terminal 1.16 or newer: pixel shaders only work on the Atlas
renderer, which became the default in that version.

Changing `experimental.pixelShaderPath` takes effect immediately, in every open
pane using that profile; no new tab is needed.

Editing a shader file is the exception: the renderer recompiles when the path
value changes, so a saved `.hlsl` edit with the same path is ignored. Force a
recompile by toggling the effect off and on with `toggleShaderEffects`
(`Shift+F10` in [`examples/settings.jsonc`](examples/settings.jsonc)), or by
pointing the setting at another file and back.

A shader that fails to compile produces a warning dialog and is ignored until you
fix the file and force a recompile the same way.

Forward slashes work on any Windows version. Recent builds (1.24+) also accept a
path relative to `settings.json`.

## Tuning

Every knob is a `#define` at the top of the file. Edit, save, then force a
recompile.

### grain.hlsl

| Define | Default | Notes |
| --- | --- | --- |
| `GRAIN_INTENSITY` | `0.02` | `0.01` barely there, `0.035` obviously film |

The noise uses the same curve as upstream `crt.hlsl`: a roughly normal
distribution, which is what makes it read as film instead of TV static.

`grain.hlsl` uses `Time`, so it animates: expect a continuous redraw while the
shader is loaded.

### neon.hlsl

| Define | Default | Notes |
| --- | --- | --- |
| `GLOW_STRENGTH` | `0.80` | Halo opacity. The main more/less dial |
| `GLOW_THRESHOLD` | `0.40` | Peak value a pixel must exceed to emit |
| `GLOW_GAIN` | `1.40` | Recovers brightness lost to blur dilution |
| `GLOW_STEP_PX` | `2.0` | Blur radius. Lower it if filled UI badges fog up |
| `ENABLE_CHROMATIC_ABERRATION` | `1` | Set `0` to remove two samples |
| `CA_PIXELS` | `0.75` | Sub-pixel by design; `1.5` is a visible split |

#### What the 36 samples are

`sampleAberrated` costs 3 (centre, red, blue). `glowField` costs 33: one centre
tap plus eight offsets in each of four directions. Turning
`ENABLE_CHROMATIC_ABERRATION` off drops the total to 34.

The tap weights are upstream's. They sum to 1: the loop samples each symmetric
pair twice, so `0.102 + 2 × 0.449 = 1.000`, and a solid bright field passes
through the blur at full value.

### house.hlsl

Everything in `neon.hlsl`, plus `GRAIN_INTENSITY 0.02`. If you only try one
shader from this repository, try this one: the glow touches only bright pixels
and the grain mostly shows on dark ones, so the two effects stay out of each
other's way.

The glow and noise code is the same as in `neon.hlsl` and `grain.hlsl`.
`tools/check-shared-blocks.py` compares those symbols by name and fails when a
copy drifts.

| Define | Default | Notes |
| --- | --- | --- |
| `GRAIN_INTENSITY` | `0.02` | Same dial as `grain.hlsl` |

### signal-loss.hlsl

Built for `unfocusedAppearance`, so a pane that loses focus reads as a failing
signal.

| Define | Default | Notes |
| --- | --- | --- |
| `ANIMATE` | `1` | `0` removes every `Time` reference: frozen pattern, no redraw cost |
| `DIM` | `0.70` | How far the pane recedes |
| `BANDS` | `40.0` | Horizontal tear zones |
| `BAND_CHANCE` | `0.90` | Share of rows that stay clean |
| `BAND_DISPLACE` | `0.008` | Tear width as a fraction of pane width |
| `GHOST_PX` / `GHOST_MIX` | `3.0` / `0.18` | Double-image offset and strength |
| `STUCK_LINE` | `0.12` | Baseline brightness of frozen scan lines |
| `BURST_EVERY` | `3.0` | Seconds per glitch slot |
| `BURST_LENGTH` | `0.36` | Seconds a burst lasts |
| `BURST_CHANCE` | `0.60` | Share of slots that fire |
| `CA_BURST_PX` | `5.0` | Red/blue split during a burst, in pixels |

Idle, that is two samples: the pane and its ghost. During a burst the pane
needs three, one per colour at a different offset, plus the ghost.

### pipboy.hlsl

A Pip-Boy screen: green phosphor, scanlines, a mild tube curve. A tuned copy of
`crt.hlsl` from Hammster/windows-terminal-shaders; NOTICE.md records where it
differs.

Each stage sits behind an `ENABLE_*` switch at the top: curve, overscan, bloom,
blur, grayscale, blacklevel, refresh line, scanlines, tint, grain.

| Define | Default | Notes |
| --- | --- | --- |
| `CURVE_INTENSITY` | `0.35` | The fisheye. Upstream ships `1`, which is much stronger |
| `TINT_COLOR` | `TINT_PIPBOY` | `#12FF15`, Fallout 4's default. Amber and Apple II are defined beside it |
| `BLACKLEVEL_FLOOR` | `TINT_COLOR / 30` | Lifts black to a phosphor glow |
| `GRAYSCALE_LUMINANCE` | `1` | The enabled strategy. With bloom on, gleam and luma fall back to it |
| `GRAIN_INTENSITY` | `0.025` | Same noise curve as `grain.hlsl` |
| `BLUR_OFFSET` / `BLUR_STRENGTH` | `0.003` / `0.3` | Two 17-tap passes; with bloom, 36 samples/px |

## Unfocused panes

`unfocusedAppearance` accepts `experimental.pixelShaderPath` and applies per
control, so it tracks pane and tab focus, not just window focus.

```jsonc
"profiles": {
  "defaults": {
    "experimental.pixelShaderPath": "C:/path/to/wt-shader-lab/shaders/house.hlsl",
    "unfocusedAppearance": {
      "experimental.pixelShaderPath": "C:/path/to/wt-shader-lab/shaders/signal-loss.hlsl"
    }
  }
}
```

`toggleShaderEffects` flips only the focused appearance's shader path
(`ControlCore::ToggleShaderEffects` reads the focused settings). The unfocused
appearance re-applies its own shader when focus leaves, so the effect reappears
on the pane you just left. Drop `unfocusedAppearance` if you want the toggle to
be absolute.

## Demos

Two stdlib-only Python scripts that render reference content into the terminal,
so you can judge a threshold without guessing from real output.

`demo/neon-test.py` is the synthetic pattern: the same stroke at 25, 50, 75 and
100% brightness, one-pixel strokes, solid blocks, a black-to-white ramp, the
ANSI palette, and a log block.

`demo/testcard.py` is a whole Markdown page in ANSI: headings, body text, a
table, syntax-highlighted code blocks, status chips, a 6×6×6 colour cube, a
grayscale ramp, near-black and near-white steps for black-crush checks, and text
attributes.

```
python demo/neon-test.py
python demo/testcard.py
```

Run them after forcing a recompile, so you know which shader build you are
looking at.

## Design notes

**Threshold before blur.** A 1 px glyph stroke loses most of its brightness to a
wide blur. Gating the *blurred* result hides exactly the brightest thin text
while large bright blocks sail through. Thresholding each tap before weighting
is what a real bloom pass does, and it is why `emit()` runs per sample.

**Gate on peak channel.** Luma weights blue at 0.07, so blue and purple text
would never cross the threshold and would stay flat while everything else
glowed. Peak channel gives every saturated hue the same chance, which matters
when colour carries meaning.

**Screen blend.** `1 - (1 - colour) * (1 - glow)` adds light without pushing the
glyph core toward white, so amber stays amber instead of turning yellow.

**DPI.** Offsets are written in pixels and converted with `Scale / Resolution`,
so a given `GLOW_STEP_PX` stays constant in physical pixels across display
scaling.

## Limits

- Single pass, no history buffer: no phosphor persistence, motion blur or trails.
- A bloom pass cannot distinguish a bright glyph from a filled bright rectangle
  of the same value, so UI badges fog up before text does. Reduce
  `GLOW_STEP_PX`.
- `Time` in a shader means continuous redraws. Without it, a pane only redraws
  when its content changes.

## License and attribution

MIT — see [LICENSE](LICENSE) and [NOTICE.md](NOTICE.md). The grain curve builds on
[windows-terminal-shaders](https://github.com/Hammster/windows-terminal-shaders)
by Hans Koch (CC0 1.0), and the shader contract on Microsoft's Windows Terminal
pixel shader samples (MIT).
