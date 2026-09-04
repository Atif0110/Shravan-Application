$ErrorActionPreference = "Stop"
$root = $PSScriptRoot
if (-not (Test-Path "$root\Frontend\node_modules")) {
    Push-Location "$root\Frontend"
    npm install --no-audit --no-fund
    Pop-Location
}
Start-Process powershell -ArgumentList "-NoExit", "-File", "$root\run_backend.ps1"
Push-Location "$root\Frontend"
npm run dev
Pop-Location
