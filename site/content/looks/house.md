---
title: house
weight: 3
cost: 36 samples per pixel
summary: Neon glow plus film grain. The everyday one.
poster: https://res.cloudinary.com/drwbqceye/video/upload/so_12,w_1600,q_auto/v1794759164/house-demo_vzgzik.jpg
video: https://res.cloudinary.com/drwbqceye/video/upload/v1794759164/house-demo_vzgzik.mp4
source: https://github.com/yethranayeh/wt-shader-lab/blob/main/shaders/house.hlsl
---

[Neon]({{< relref "/looks/neon" >}}) plus `GRAIN_INTENSITY 0.02`. The glow
touches only bright pixels and the grain mostly shows on dark ones, so the two
stay out of each other's way.

| Define | Default | Notes |
| --- | --- | --- |
| `GRAIN_INTENSITY` | `0.02` | Same dial as [grain]({{< relref "/looks/grain" >}}) |

The glow and noise code is identical to `neon.hlsl` and `grain.hlsl`.
`tools/check-shared-blocks.py` compares those symbols by name and fails when a
copy drifts.
