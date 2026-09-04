$ErrorActionPreference = "Stop"
Set-Location (Join-Path $PSScriptRoot "Backend")
if (-not (Test-Path ".env")) { Copy-Item ".env.example" ".env" }
$envText = Get-Content ".env" -Raw
if ($envText -match "SECRET_KEY=replace-with-a-long-random-secret") {
    $secret = python -c "import secrets; print(secrets.token_hex(32))"
    $envText = $envText -replace "SECRET_KEY=.*", "SECRET_KEY=$secret"
    Set-Content ".env" $envText
}
if (-not (Test-Path "backend_venv")) { python -m venv backend_venv }
& .\backend_venv\Scripts\Activate.ps1
python -m pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt
python app.py
