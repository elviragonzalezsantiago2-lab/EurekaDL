<#
Download and extract a static ffmpeg build to tools/ffmpeg-static on Windows.
This script avoids committing binaries to the repo; it places them in tools/ (gitignored).
#>
param(
    [string]$OutDir = "tools/ffmpeg-static",
    [switch]$Force
)

$ErrorActionPreference = 'Stop'

if (-Not (Test-Path $OutDir) -or $Force) {
    New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
    $zipUrl = 'https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip'
    $zipPath = Join-Path $OutDir 'ffmpeg-release-essentials.zip'
    Write-Host "Downloading ffmpeg to $zipPath (may take a while)..."
    Invoke-WebRequest -Uri $zipUrl -OutFile $zipPath
    $extractPath = Join-Path $OutDir 'extracted'
    Write-Host "Extracting to $extractPath"
    Expand-Archive -Path $zipPath -DestinationPath $extractPath -Force
    # Find bin folder
    $first = Get-ChildItem -Path $extractPath -Directory | Select-Object -First 1
    if ($first) { $bin = Join-Path $first.FullName 'bin' } else { $bin = Join-Path $extractPath 'bin' }
    Write-Host "ffmpeg binaries available at: $bin"
    Write-Host 'Done. Add $bin to your PATH or run scripts/convert_m4a_to_mp3.py which will use this binary location.'
} else {
    Write-Host "$OutDir already exists. Use -Force to re-download."
}
