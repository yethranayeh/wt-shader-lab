---
title: Install
description: Point Windows Terminal at a shader, and see it in every open pane.
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

## When changes apply

Changing `experimental.pixelShaderPath` takes effect immediately, in every open
pane using that profile. Saving `settings.json` is enough; no new tab is needed.

Editing a shader file is the exception: the renderer recompiles when the path
value changes, so a saved `.hlsl` edit with the same path is ignored. Force a
recompile by toggling the effect off and on (below), or by pointing the setting
at another file and back.

A shader that fails to compile produces a warning dialog and is ignored until you
fix the file and force a recompile the same way.

## Toggle it

`toggleShaderEffects` turns the effect off and on without editing settings,
which is how you tell what a shader is actually doing to a pane. It also forces
a recompile of an edited shader file.

```json
"actions": [
  { "command": "toggleShaderEffects", "keys": "shift+f10" }
]
```

## Unfocused panes

`unfocusedAppearance` takes the same key and applies per control, so it tracks
pane and tab focus. The [gallery]({{< relref "/gallery" >}}) shows both states
side by side, and [signal-loss]({{< relref "/looks/signal-loss" >}}) is built for
this slot.

```json
"profiles": {
  "defaults": {
    "experimental.pixelShaderPath": "C:/path/to/wt-shader-lab/shaders/house.hlsl",
    "unfocusedAppearance": {
      "experimental.pixelShaderPath": "C:/path/to/wt-shader-lab/shaders/signal-loss.hlsl"
    }
  }
}
```

