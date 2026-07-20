$ErrorActionPreference = "SilentlyContinue"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$AnalysisDir = $PSScriptRoot
$Root = Split-Path -Parent $AnalysisDir
$OutDirItem = Get-ChildItem -LiteralPath $AnalysisDir -Directory | Where-Object { $_.Name -like "GPT5.5*" } | Select-Object -First 1
$OutDir = if ($OutDirItem) { $OutDirItem.FullName } else { Join-Path $AnalysisDir "GPT5.5" }
$WorkDir = Join-Path $AnalysisDir "_data\codex_cli_deep_read"
$PidFile = Join-Path $WorkDir "full_run.pid"
$LogFile = Join-Path $WorkDir "run_log.jsonl"
$PapersJson = Join-Path $AnalysisDir "_data\papers_enriched.json"

$Total = 0
if (Test-Path -LiteralPath $PapersJson) {
    $Total = @((Get-Content -LiteralPath $PapersJson -Encoding UTF8 -Raw | ConvertFrom-Json)).Count
}
if ($Total -eq 0) {
    $Total = @(Get-ChildItem -LiteralPath (Join-Path $Root "paper") -File -Filter "*.pdf").Count
}

$Completed = 0
if (Test-Path -LiteralPath $OutDir) {
    $Completed = @(Get-ChildItem -LiteralPath $OutDir -File -Filter "*.md").Count
}

$Running = $false
$PidValue = ""
if (Test-Path -LiteralPath $PidFile) {
    $PidValue = (Get-Content -LiteralPath $PidFile -Raw).Trim()
    if ($PidValue) {
        $Running = [bool](Get-Process -Id ([int]$PidValue))
    }
}

[PSCustomObject]@{
    Completed = $Completed
    Total = $Total
    Remaining = [Math]::Max(0, $Total - $Completed)
    Running = $Running
    Pid = $PidValue
    OutputDir = $OutDir
    LogFile = $LogFile
} | Format-List

if (Test-Path -LiteralPath $LogFile) {
    ""
    "Recent log:"
    Get-Content -LiteralPath $LogFile -Encoding UTF8 -Tail 20 |
        ForEach-Object {
            try {
                $j = $_ | ConvertFrom-Json
                [PSCustomObject]@{
                    Num = $j.num
                    Status = $j.status
                    ReturnCode = $j.returncode
                    Seconds = $j.elapsed_sec
                    Time = $j.time
                    Output = $j.final_output
                }
            } catch {
                $null
            }
        } |
        Select-Object -Last 8 |
        Format-Table -AutoSize
}
