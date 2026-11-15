# Compiles every shader in shaders/ with fxc, the compiler Windows Terminal
# invokes at runtime. Needs the Windows SDK, which the windows-latest runner
# image ships; there is no equivalent toolchain on macOS or Linux.

$ErrorActionPreference = 'Stop'

$repo = Split-Path -Parent $PSScriptRoot
$shaderDir = Join-Path $repo 'shaders'

if ($env:RUNNER_TEMP) {
    $outDir = Join-Path $env:RUNNER_TEMP 'shader-out'
} else {
    $outDir = Join-Path ([System.IO.Path]::GetTempPath()) 'shader-out'
}
New-Item -ItemType Directory -Force -Path $outDir | Out-Null

$sdkBin = 'C:\Program Files (x86)\Windows Kits\10\bin'
if (-not (Test-Path $sdkBin)) {
    throw "Windows SDK not found at $sdkBin"
}

# Several SDK versions can be installed. Take the newest one that has fxc.
$fxc = $null
foreach ($dir in Get-ChildItem $sdkBin -Directory) {
    $candidate = Join-Path $dir.FullName 'x64\fxc.exe'
    if (-not (Test-Path $candidate)) { continue }

    $version = [version]'0.0'
    if (-not [version]::TryParse($dir.Name, [ref]$version)) { continue }

    if (-not $fxc -or $version -gt $fxc.Version) {
        $fxc = [pscustomobject]@{ Path = $candidate; Version = $version }
    }
}
if (-not $fxc) {
    throw "fxc.exe not found under $sdkBin"
}
Write-Host "fxc: $($fxc.Path)"

$shaders = @(Get-ChildItem (Join-Path $shaderDir '*.hlsl') | Sort-Object Name)
if ($shaders.Count -eq 0) {
    throw "No shaders found in $shaderDir"
}

$failures = 0
foreach ($shader in $shaders) {
    $cso = Join-Path $outDir ($shader.BaseName + '.cso')

    Write-Host "::group::$($shader.Name)"
    & $fxc.Path /nologo /T ps_5_0 /E main /Fo $cso $shader.FullName
    $code = $LASTEXITCODE
    Write-Host "::endgroup::"

    $size = 0
    if (Test-Path $cso) { $size = (Get-Item $cso).Length }

    if ($code -ne 0 -or $size -eq 0) {
        Write-Host "::error file=$($shader.FullName)::$($shader.Name) failed to compile"
        $failures++
    } else {
        Write-Host "$($shader.Name): ok, $size bytes"
    }
}

if ($failures -gt 0) {
    throw "$failures shader(s) failed to compile"
}
Write-Host "All shaders compiled."
