$ErrorActionPreference = "Stop"
$env:PYTHONPATH = "Backend"
pytest Tests -q
