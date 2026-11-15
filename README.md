# wt-shader-lab

Pixel shaders for Windows Terminal that stay readable.

Four looks so far. All of them are single-pass post-processes over the
terminal's rendered frame — they change light, not layout, and none of them
move a glyph.

| Shader | What it does | Cost |
| --- | --- | --- |
| [`grain.hlsl`](shaders/grain.hlsl) | Film grain only. No colour shift, no geometry, no resampling. | 1 sample/px |
| [`neon.hlsl`](shaders/neon.hlsl) | Bright glyphs bloom in their own colour, with optional sub-pixel RGB split. | 36 samples/px |
| [`house.hlsl`](shaders/house.hlsl) | `neon` + grain. The everyday one. | 37 samples/px |
| [`signal-loss.hlsl`](shaders/signal-loss.hlsl) | Damaged-signal look for unfocused panes: torn bands, ghosting, bursts with RGB split. | 2 samples/px, 4 during a burst |

## Install

Point `experimental.pixelShaderPath` at whichever shader you want. Per-profile is
the sane default; `profiles.defaults` applies it to everything. The examples use
`house.hlsl`.

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

## Design notes

**Threshold before blur.** A 1 px glyph stroke loses most of its brightness to a
wide blur. Gating the *blurred* result hides exactly the brightest thin text
while large bright blocks sail through. Thresholding each tap before weighting
is what a real bloom pass does, and it is why `emit()` runs per sample instead of
once on the sum.

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
