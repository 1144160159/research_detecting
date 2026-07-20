param(
  [ValidateSet('init','local-index','external-search','merge-screen','zotero-batch','zotero-import','all-before-zotero')]
  [string]$Stage = 'init',
  [switch]$Run,
  [int]$Limit = 0,
  [string]$Sources = ''
)

$ErrorActionPreference = 'Stop'
$OutputEncoding = [System.Text.UTF8Encoding]::new()
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()
$env:PYTHONUTF8 = '1'
$env:PYTHONIOENCODING = 'utf-8'

$WorkflowRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$WorkspaceRoot = Split-Path -Parent $WorkflowRoot
$ConfigPath = Join-Path $WorkflowRoot 'config\pipeline.yml'
$QueriesPath = Join-Path $WorkflowRoot 'config\queries.yml'
$LogDir = Join-Path $WorkflowRoot 'logs'
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

function Find-Python {
  $uvPython = Join-Path $env:APPDATA 'uv\tools\paper-search-mcp\Scripts\python.exe'
  if (Test-Path -LiteralPath $uvPython) { return $uvPython }
  $cmd = Get-Command python -ErrorAction SilentlyContinue
  if ($cmd) { return $cmd.Source }
  throw 'Python not found. Install Python or paper-search-mcp uv tool first.'
}

function Invoke-StageScript {
  param(
    [string]$ScriptName,
    [string[]]$ExtraArgs = @()
  )
  $python = Find-Python
  $script = Join-Path $WorkflowRoot ("scripts\" + $ScriptName)
  if (-not (Test-Path -LiteralPath $script)) {
    throw "Missing script: $script"
  }

  $args = @(
    $script,
    '--workspace', $WorkspaceRoot,
    '--config', $ConfigPath
  )
  if (-not $Run) { $args += '--dry-run' }
  if ($Limit -gt 0) { $args += @('--limit', [string]$Limit) }
  if ($Sources) { $args += @('--sources', $Sources) }
  $args += $ExtraArgs

  Write-Host "python $($args -join ' ')"
  & $python @args
}

Write-Host "Workflow root: $WorkflowRoot"
Write-Host "Workspace root: $WorkspaceRoot"
if (-not $Run) {
  Write-Host "Mode: dry-run. Add -Run to execute file/network work."
}

switch ($Stage) {
  'init' {
    Write-Host 'Available stages: local-index, external-search, merge-screen, all-before-zotero'
    Write-Host 'Examples:'
    Write-Host '  .\zotero-workflow\run_pipeline.ps1 -Stage local-index'
    Write-Host '  .\zotero-workflow\run_pipeline.ps1 -Stage local-index -Run -Limit 50'
    Write-Host '  .\zotero-workflow\run_pipeline.ps1 -Stage external-search -Run -Sources semantic,core,arxiv'
  }
  'local-index' {
    Invoke-StageScript -ScriptName 'local_index.py'
  }
  'external-search' {
    Invoke-StageScript -ScriptName 'external_search.py' -ExtraArgs @('--queries', $QueriesPath)
  }
  'merge-screen' {
    Invoke-StageScript -ScriptName 'merge_screen.py' -ExtraArgs @('--queries', $QueriesPath)
  }
  'zotero-batch' {
    Invoke-StageScript -ScriptName 'zotero_batch.py'
  }
  'zotero-import' {
    Invoke-StageScript -ScriptName 'zotero_import_connector.py'
  }
  'all-before-zotero' {
    Invoke-StageScript -ScriptName 'local_index.py'
    Invoke-StageScript -ScriptName 'external_search.py' -ExtraArgs @('--queries', $QueriesPath)
    Invoke-StageScript -ScriptName 'merge_screen.py' -ExtraArgs @('--queries', $QueriesPath)
  }
}
