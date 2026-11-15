---
title: grain
weight: 1
cost: 1 sample per pixel
summary: Film grain only, with no colour shift, geometry or resampling.
source: https://github.com/yethranayeh/wt-shader-lab/blob/main/shaders/grain.hlsl
---

The noise comes from the same curve as upstream `crt.hlsl`, a roughly normal
distribution, which is what makes it read as film.

| Define | Default | Notes |
| --- | --- | --- |
| `GRAIN_INTENSITY` | `0.02` | `0.01` barely there, `0.035` obviously film |

It samples `Time`, so a pane with the shader loaded redraws continuously.
