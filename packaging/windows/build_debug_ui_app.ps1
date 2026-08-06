$ErrorActionPreference = "Stop"

$repo = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$env:PYTHONPATH = Join-Path $repo "src"

python -m PyInstaller `
  --noconfirm `
  --clean `
  --windowed `
  --name HearthstoneCopilotDebugUI `
  --paths (Join-Path $repo "src") `
  --collect-all webview `
  (Join-Path $repo "packaging\windows\windows_app_entry.py")

if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}

Write-Host "Built: $(Join-Path $repo 'dist\HearthstoneCopilotDebugUI\HearthstoneCopilotDebugUI.exe')"
