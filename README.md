# wt-shader-lab

Pixel shaders for Windows Terminal that stay readable.

One look so far: film grain that reads as film rather than television static.
It is a single-pass post-process over the terminal's rendered frame — it changes
light, not layout, and nothing about it moves a glyph.

| Shader | What it does | Cost |
| --- | --- | --- |
| [`grain.hlsl`](shaders/grain.hlsl) | Film grain only. No colour shift, no geometry, no resampling. | 1 sample/px |

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

## Limits

- Single pass, no history buffer: no phosphor persistence, motion blur or trails.
- `Time` in a shader means continuous redraws. Without it, a pane only redraws
  when its content changes.

## License and attribution

MIT — see [LICENSE](LICENSE) and [NOTICE.md](NOTICE.md). The grain curve builds on
[windows-terminal-shaders](https://github.com/Hammster/windows-terminal-shaders)
by Hans Koch (CC0 1.0), and the shader contract on Microsoft's Windows Terminal
pixel shader samples (MIT).
