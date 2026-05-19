# One-time: log in to GitHub, then create repo and push Zodiac Sign Finder
# Run in PowerShell:  .\publish-to-github.ps1

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

Write-Host "Checking GitHub login..." -ForegroundColor Cyan
$auth = gh auth status 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "You need to log in to GitHub once." -ForegroundColor Yellow
    Write-Host "A browser window will open. Choose GitHub.com -> HTTPS -> Login with browser." -ForegroundColor Yellow
    gh auth login -h github.com -p https -w
}

$username = (gh api user -q .login)
if (-not $username) {
    throw "Could not read GitHub username. Run: gh auth login"
}

$repoName = "zodiac-sign-finder"
Write-Host "GitHub user: $username" -ForegroundColor Green
Write-Host "Creating public repo: $repoName ..." -ForegroundColor Cyan

gh repo create $repoName --public --source=. --remote=origin --push --description "Desktop zodiac sign finder - Python Tkinter portfolio project"

Write-Host ""
Write-Host "Done! Your repo:" -ForegroundColor Green
Write-Host "  https://github.com/$username/$repoName"
Write-Host ""
Write-Host "Add screenshots to docs/screenshots/ then: git add . ; git commit -m 'Add portfolio screenshots' ; git push"
