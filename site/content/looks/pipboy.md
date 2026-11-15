---
title: pipboy
weight: 5
cost: 36 samples per pixel
summary: Fallout Pip-Boy CRT with green phosphor, scanlines and a mild curve.
source: https://github.com/yethranayeh/wt-shader-lab/blob/main/shaders/pipboy.hlsl
---

A tuned copy of `crt.hlsl` from
[Hammster/windows-terminal-shaders](https://github.com/Hammster/windows-terminal-shaders).
`NOTICE.md` records where it differs.

Each stage sits behind an `ENABLE_*` switch at the top: curve, overscan, bloom,
blur, grayscale, blacklevel, refresh line, scanlines, tint, grain.

| Define | Default | Notes |
| --- | --- | --- |
| `CURVE_INTENSITY` | `0.35` | The fisheye. Upstream ships `1`, which is much stronger |
| `TINT_COLOR` | `TINT_PIPBOY` | `#12FF15`, Fallout 4's default. Amber and Apple II are defined beside it |
| `BLACKLEVEL_FLOOR` | `TINT_COLOR / 30` | Lifts black to a phosphor glow |
| `GRAYSCALE_LUMINANCE` | `1` | The enabled strategy. With bloom on, gleam and luma fall back to it |
| `GRAIN_INTENSITY` | `0.025` | Same noise curve as [grain]({{< relref "/looks/grain" >}}) |
| `BLUR_OFFSET` / `BLUR_STRENGTH` | `0.003` / `0.3` | Two 17-tap passes; with bloom, 36 samples/px |
