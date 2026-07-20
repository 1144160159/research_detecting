$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$env:PYTHONUTF8 = "1"

$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

$ScriptPath = Join-Path $PSScriptRoot "codex_cli_deep_read.py"
$PythonExe = $env:PYTHON_EXE
if (-not $PythonExe -and (Test-Path -LiteralPath "D:\soft\Anaconda3\python.exe")) {
    $PythonExe = "D:\soft\Anaconda3\python.exe"
}
if (-not $PythonExe) {
    $PythonExe = (Get-Command python -ErrorAction Stop).Source
}

& $PythonExe $ScriptPath --start 1 --timeout 1800
