---
title: Design notes
description: The four decisions that make these shaders read the way they do.
menu:
  main:
    weight: 3
---

Four decisions carry most of the look. Each is a line of shader code, and each
fails in a specific way when reversed.

## Threshold before blur

A 1 px glyph stroke loses most of its brightness to a wide blur. Gating the
*blurred* result hides exactly the brightest thin text while large bright blocks
sail through. Thresholding each tap before weighting is what a real bloom pass
does, and it is why `emit()` runs per sample.

## Gate on peak channel

Luma weights blue at 0.07, so blue and purple text would never cross the
threshold and would stay flat while everything else glowed. Peak channel gives
every saturated hue the same chance, which matters when colour carries meaning.

## Screen blend

`1 - (1 - colour) * (1 - glow)` adds light without pushing the glyph core toward
white, so amber stays amber.

## DPI

Offsets are written in pixels and converted with `Scale / Resolution`, so a given
`GLOW_STEP_PX` stays constant in physical pixels across display scaling.

## Limits

- Single pass, no history buffer: no phosphor persistence, motion blur or trails.
- A bloom pass cannot distinguish a bright glyph from a filled bright rectangle of
  the same value, so UI badges fog up before text does. Reduce `GLOW_STEP_PX`.
- `Time` in a shader means continuous redraws. Without it, a pane only redraws
  when its content changes.

## Credits

MIT. The grain curve and the tap weights come from
[windows-terminal-shaders](https://github.com/Hammster/windows-terminal-shaders)
by Hans Koch (CC0 1.0), and the shader contract from Microsoft's Windows Terminal
pixel shader samples. The full text is in
[NOTICE.md](https://github.com/yethranayeh/wt-shader-lab/blob/main/NOTICE.md) and
[LICENSE](https://github.com/yethranayeh/wt-shader-lab/blob/main/LICENSE).
