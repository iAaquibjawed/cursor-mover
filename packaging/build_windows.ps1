# Build a single-file Windows executable plus a distributable zip.
#
# Usage (from the repository root):  .\packaging\build_windows.ps1
#Requires -Version 5.1
$ErrorActionPreference = 'Stop'

$RepoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $RepoRoot

function Write-Ok   ($m) { Write-Host "OK   $m" -ForegroundColor Green }
function Write-Info ($m) { Write-Host "->   $m" -ForegroundColor Yellow }
function Fail       ($m) { Write-Host "FAIL $m" -ForegroundColor Red; exit 1 }

if (-not $IsWindows -and $PSVersionTable.PSVersion.Major -ge 6) {
    Fail 'Windows executables must be built on Windows.'
}

if (-not (Get-Command pyinstaller -ErrorAction SilentlyContinue)) {
    Write-Info 'PyInstaller not found; installing...'
    python -m pip install --upgrade 'pyinstaller>=6.6'
}
Write-Ok "PyInstaller $(pyinstaller --version)"

Write-Info 'Cleaning previous build output...'
Remove-Item -Recurse -Force build, dist -ErrorAction SilentlyContinue

Write-Info 'Building CursorMover.exe...'
pyinstaller --clean --noconfirm packaging\windows.spec
if ($LASTEXITCODE -ne 0) { Fail 'PyInstaller failed.' }

if (-not (Test-Path 'dist\CursorMover.exe')) {
    Fail 'Build finished but dist\CursorMover.exe is missing.'
}

Write-Info 'Staging the zip...'
$Stage = 'dist\CursorMover-Windows'
Remove-Item -Recurse -Force $Stage -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Path $Stage | Out-Null

Copy-Item 'dist\CursorMover.exe' $Stage
Copy-Item 'docs\install\windows.txt' "$Stage\README.txt"
Copy-Item 'LICENSE' $Stage

Compress-Archive -Path "$Stage\*" -DestinationPath 'dist\CursorMover-Windows.zip' -Force
Remove-Item -Recurse -Force $Stage

$size = '{0:N1} MB' -f ((Get-Item 'dist\CursorMover.exe').Length / 1MB)
Write-Ok "Built dist\CursorMover.exe ($size)"
Write-Ok 'Built dist\CursorMover-Windows.zip'
Write-Host ''
Write-Info 'Try it: .\dist\CursorMover.exe --verbose'
