# Attribution

This project is licensed MIT (see [LICENSE](LICENSE)). It builds on the following work.

## windows-terminal-shaders — Hans Koch (Hammster)

- Repository: https://github.com/Hammster/windows-terminal-shaders
- License: CC0 1.0 Universal (public domain dedication)

The film-grain noise curve, its lookup constants, and the blur tap weights used in
`shaders/grain.hlsl`, `shaders/neon.hlsl` and `shaders/house.hlsl` are taken from
`crt.hlsl` in that repository.

`shaders/pipboy.hlsl` is a copy of the same `crt.hlsl` with its tuning constants changed,
so the derivation is direct and deliberate. Two lines differ for reasons that are not
tuning: the debug switch is off, and the right-hand overscan test reads `uv.x` where
upstream repeats `uv.y` and never checks the right edge.

CC0 places no attribution requirement on any of this. The credit is here because the work
deserves it, not because the license demands it.

## Windows Terminal pixel shader samples — Microsoft

- Repository: https://github.com/microsoft/terminal/tree/main/samples/PixelShaders
- License: MIT

Defines the shader contract used here: texture `t0`, sampler `s0`, and the
`PixelShaderSettings` constant buffer (`Time`, `Scale`, `Resolution`, `Background`). The
`ps_5_0` entry point and the pixel-shader feature itself are Microsoft's.

Upstream `crt.hlsl` also derives its scanline technique from `Retro.hlsl` in that
repository. These shaders do not include scanline code, but the derivation chain is noted
for completeness.

## Colour-to-grayscale paper

Cited by upstream for the `GRAYSCALE_INTENSITY`, `GLEAM`, `LUMINANCE` and `LUMA`
strategies in `crt.hlsl`, which `shaders/pipboy.hlsl` retains:

> Kanan, C., & Cottrell, G. W. (2012). *Color-to-Grayscale: Does the Method Matter in
> Image Recognition?* PLOS ONE, 7(1), e29740.
> https://doi.org/10.1371/journal.pone.0029740

That paper defines the *Intensity*, *Gleam*, *Luminance* and *Luma* strategies retained in
`shaders/pipboy.hlsl`.

## Fallout Pip-Boy colour

`shaders/pipboy.hlsl` uses `#12FF15`, the default value of Fallout 4's public
`fPipboyEffectColor*` preference. It is a fact about the game's configuration, not an
asset from it. Fallout and Pip-Boy are trademarks of Bethesda Softworks; this project is
unaffiliated.
