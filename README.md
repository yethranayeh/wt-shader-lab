# wt-shader-lab

Pixel shaders for Windows Terminal that stay readable.

Two looks so far. Both are single-pass post-processes over the terminal's
rendered frame — they change light, not layout, and nothing about them moves a
glyph.

| Shader | What it does | Cost |
| --- | --- | --- |
| [`grain.hlsl`](shaders/grain.hlsl) | Film grain only. No colour shift, no geometry, no resampling. | 1 sample/px |
| [`neon.hlsl`](shaders/neon.hlsl) | Bright glyphs bloom in their own colour, with optional sub-pixel RGB split. | 36 samples/px |

## Install

Point `experimental.pixelShaderPath` at whichever shader you want. Per-profile is
the sane default; `profiles.defaults` applies it to everything.

```jsonc
"profiles": {
  "defaults": {
    "experimental.pixelShaderPath": "C:/path/to/wt-shader-lab/shaders/grain.hlsl"
  }
}
```

[`examples/settings.jsonc`](examples/settings.jsonc) is the same thing as a file
you can copy from.

Requires Windows Terminal 1.16 or newer. Pixel shaders are an `experimental.`
feature and only work with the Atlas renderer, which became the default in 1.16.
Support is older than that — 1.6 — but until Atlas was the default the behaviour
depended on which renderer a profile happened to be using, so 1.16 is the first
version where this is guaranteed to work.

A shader that fails to compile produces a warning dialog and is ignored until
you fix it and re-save `settings.json` or open a new tab. Shaders are compiled
per pane, so an already-open pane keeps the old one — **open a new tab** after
editing a shader.

Forward slashes work on any Windows version. Recent builds (1.24+) also accept a
path relative to `settings.json`.

## Tuning

Every knob is a `#define` at the top of the file. Edit, save, open a new tab.

### grain.hlsl

| Define | Default | Notes |
| --- | --- | --- |
| `GRAIN_INTENSITY` | `0.02` | `0.01` barely there, `0.035` obviously film |

The noise is not uniform random. It uses the same curve as upstream `crt.hlsl`,
which is roughly normally distributed, and that is what makes it read as film
instead of TV static.

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

The tap weights are upstream's. They sum to 1 once every symmetric pair is
counted twice, which is what the loop does, so a solid bright field passes
through the blur at full value and `GLOW_GAIN` is a boost rather than a
correction.

## Design notes

Four things bit hard enough to be worth writing down.

**Threshold before blur, not after.** A 1 px glyph stroke loses most of its
brightness to a wide blur. Gating the *blurred* result hides exactly the
brightest thin text while large bright blocks sail through. Thresholding each
tap before weighting is what a real bloom pass does, and it is why `emit()` runs
per sample instead of once on the sum.

**Gate on peak channel, not luma.** Luma weights blue at 0.07, so blue and
purple text would never cross the threshold and would stay flat while everything
else glowed. Peak channel gives every saturated hue the same chance, which
matters when colour carries meaning.

**Screen blend, not addition.** `1 - (1 - colour) * (1 - glow)` adds light
without pushing the glyph core toward white, so amber stays amber instead of
turning yellow.

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
