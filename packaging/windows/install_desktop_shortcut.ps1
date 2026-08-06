$ErrorActionPreference = "Stop"

$repo = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$exe = Join-Path $repo "dist\HearthstoneCopilotDebugUI\HearthstoneCopilotDebugUI.exe"
if (-not (Test-Path -LiteralPath $exe)) {
    throw "Build the app first: $exe"
}

$desktop = [Environment]::GetFolderPath("Desktop")
$shortcut = Join-Path $desktop "Hearthstone Copilot Debug UI.lnk"
$shell = New-Object -ComObject WScript.Shell
$link = $shell.CreateShortcut($shortcut)
$link.TargetPath = $exe
$link.WorkingDirectory = Split-Path $exe
$link.Description = "Hearthstone Copilot native debug UI"
$link.Save()
Write-Host "Installed: $shortcut"
