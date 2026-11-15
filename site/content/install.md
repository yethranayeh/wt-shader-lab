---
title: Install
description: Point Windows Terminal at a shader, and see it on the next tab.
menu:
  main:
    weight: 1
---

Requires Windows Terminal 1.16 or newer: pixel shaders only work on the Atlas
renderer, which became the default in that version.

## Where the setting goes

The settings file is
`%LOCALAPPDATA%\Packages\Microsoft.WindowsTerminal_8wekyb3d8bbwe\LocalState\settings.json`
for the Store build, and `%LOCALAPPDATA%\Microsoft\Windows Terminal\settings.json`
for the unpackaged one.

Add the path under `profiles.defaults` to apply it to every profile, or under a
single profile to keep it there.

```json
"profiles": {
  "defaults": {
    "experimental.pixelShaderPath": "C:/path/to/wt-shader-lab/shaders/house.hlsl"
  }
}
```

Forward slashes work on any Windows version. From 1.24 on, the path can also be
relative to `settings.json`.

## Open a new tab

Shaders compile per pane, and a pane that is already open keeps the shader it
started with. A new tab is the only way to see the change.

A shader that fails to compile produces a warning dialog and is ignored until you
fix the file and re-save `settings.json` or open a new tab.

## Toggle it

`toggleShaderEffects` turns the effect off and on without editing settings,
which is how you tell what a shader is actually doing to a pane.

```json
"actions": [
  { "command": "toggleShaderEffects", "keys": "shift+f10" }
]
```
