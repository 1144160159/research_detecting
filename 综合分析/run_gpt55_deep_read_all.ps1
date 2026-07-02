$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$env:PYTHONUTF8 = "1"

$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

$ScriptPath = Join-Path $PSScriptRoot "codex_cli_deep_read.py"
python $ScriptPath --start 1 --end 850 --timeout 1800
