# Build ZodiacSignFinder.exe (Windows)
# Requires: Python 3.10+ with pip

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

Write-Host "Installing PyInstaller..." -ForegroundColor Cyan
python -m pip install -r requirements-build.txt

Write-Host "Building executable..." -ForegroundColor Cyan
python -m PyInstaller `
    --noconfirm `
    --clean `
    --windowed `
    --onefile `
    --name "ZodiacSignFinder" `
    --hidden-import zodiac_gui `
    --hidden-import zodiac_gui.app `
    --hidden-import zodiac_gui.theme `
    --hidden-import zodiac_gui.zodiac_logic `
    main.py

Write-Host ""
Write-Host "Done! Your app is here:" -ForegroundColor Green
Write-Host "  $PSScriptRoot\dist\ZodiacSignFinder.exe"
Write-Host ""
Write-Host "Upload dist\ZodiacSignFinder.exe via GitHub Releases (do not commit dist/ to git)."
