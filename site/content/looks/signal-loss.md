---
title: signal-loss
weight: 4
cost: 2 samples per pixel, 4 during a burst
summary: Damaged-signal look for unfocused panes, torn bands and bursts included.
source: https://github.com/yethranayeh/wt-shader-lab/blob/main/shaders/signal-loss.hlsl
---

Built for `unfocusedAppearance`, so a pane that loses focus reads as a failing
signal. [Install]({{< relref "/install" >}}) has the settings.

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

Idle it costs two samples, the pane and its ghost. A burst needs three, one per
colour at a different offset, plus the ghost.

`toggleShaderEffects` flips only the focused appearance, so the unfocused shader
returns as soon as focus leaves the pane you toggled.
