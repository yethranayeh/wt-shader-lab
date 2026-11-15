---
title: neon
weight: 2
cost: 36 samples per pixel
summary: Bright glyphs bloom in their own colour, with optional sub-pixel RGB split.
source: https://github.com/yethranayeh/wt-shader-lab/blob/main/shaders/neon.hlsl
---

Nine taps out and nine back on both axes, weighted and summed. The threshold
applies to every tap before it is weighted, which is what a real bloom pass does
and what keeps thin bright text from disappearing into the blur.

| Define | Default | Notes |
| --- | --- | --- |
| `GLOW_STRENGTH` | `0.80` | Halo opacity. The main more/less dial |
| `GLOW_THRESHOLD` | `0.40` | Peak value a pixel must exceed to emit |
| `GLOW_GAIN` | `1.40` | Recovers brightness lost to blur dilution |
| `GLOW_STEP_PX` | `2.0` | Blur radius. Lower it if filled UI badges fog up |
| `ENABLE_CHROMATIC_ABERRATION` | `1` | Set `0` to remove two samples |
| `CA_PIXELS` | `0.75` | Sub-pixel by design; `1.5` is a visible split |

## Where the 36 samples go

`sampleAberrated` costs 3: centre, red, blue. `glowField` costs 33: one centre
tap plus eight offsets in each of four directions. Turning chromatic aberration
off drops the total to 34.

The tap weights are upstream's and sum to 1, so a solid bright field passes
through the blur at full value: `0.102 + 2 × 0.449 = 1.000`.
