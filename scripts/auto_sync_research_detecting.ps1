[CmdletBinding()]
param(
    [ValidateSet('watch', 'once', 'install', 'uninstall', 'start', 'stop', 'status')]
    [string]$Mode = 'watch',
    [string]$SourceRoot = '',
    [string]$DestinationRoot = '',
    [string]$LogPath = '',
    [string]$PidPath = '',
    [int]$DebounceSeconds = 45,
    [int]$FullScanSeconds = 300
)

$ErrorActionPreference = 'Stop'
$TaskName = 'ResearchDetectingAutoSync'
$ScriptPath = $PSCommandPath

if (-not $DestinationRoot) {
    $DestinationRoot = Split-Path -Parent $PSScriptRoot
}
if (-not $SourceRoot) {
    $sourceFolderName = -join @([char]0x5F02, [char]0x5E38, [char]0x68C0, [char]0x6D4B)
    $SourceRoot = Join-Path (Split-Path -Parent $DestinationRoot) $sourceFolderName
}
if (-not $LogPath) {
    $LogPath = Join-Path $DestinationRoot '.sync\auto-sync.log'
}
if (-not $PidPath) {
    $PidPath = Join-Path $DestinationRoot '.sync\auto-sync.pid'
}

$DocumentExtensions = @(
    '.md', '.markdown', '.txt', '.doc', '.docx', '.pdf', '.ppt', '.pptx',
    '.xls', '.xlsx', '.csv', '.tex', '.bib', '.rtf'
)

$SourceCodeExtensions = @(
    '.py', '.ipynb', '.js', '.jsx', '.ts', '.tsx', '.java', '.c', '.cc',
    '.cpp', '.cxx', '.h', '.hpp', '.cs', '.go', '.rs', '.rb', '.php',
    '.sh', '.ps1', '.bat', '.cmd', '.r', '.m', '.jl', '.scala', '.kt',
    '.kts', '.swift', '.sql', '.html', '.htm', '.css', '.scss', '.less',
    '.vue', '.svelte', '.xml', '.yaml', '.yml', '.toml', '.ini', '.cfg',
    '.conf', '.json'
)

$AlwaysCodeNames = @(
    'Dockerfile', 'Makefile', 'CMakeLists.txt', 'requirements.txt',
    'requirements-dev.txt', 'pyproject.toml', 'setup.py', 'setup.cfg',
    'package.json', 'package-lock.json', 'pnpm-lock.yaml', 'yarn.lock',
    'tsconfig.json', 'jsconfig.json', 'Cargo.toml', 'Cargo.lock',
    'go.mod', 'go.sum', 'Pipfile', 'Pipfile.lock'
)

$BaseSkipSegments = @(
    '.git', '.github', '.vscode', '.idea', '.pptx_build', '__pycache__',
    'node_modules', '.conda', '.venv', 'venv', 'env', '.pytest_cache',
    '.mypy_cache', '.sync'
)

$SourceArtifactSegments = @(
    'data_cache', 'cache', 'checkpoint', 'checkpoints', 'weights',
    'saved_models', 'pt_model', 'build_datasets', 'output', 'outputs',
    'result', 'results', 'log', 'logs'
)

$DatasetSegments = @('data', 'dataset', 'datasets')

$SourceArtifactExtensions = @(
    '.csv', '.xlsx', '.xls', '.npy', '.npz', '.pkl', '.pickle', '.mat',
    '.arff', '.pcap', '.ttl', '.log', '.err', '.out', '.safetensors',
    '.pth', '.pt', '.ckpt', '.model', '.h5', '.zip', '.rar', '.7z',
    '.tar', '.gz', '.mp4', '.avi', '.mov', '.mkv', '.arrow', '.bin',
    '.exe', '.dll', '.pdb', '.so', '.dylib', '.whl', '.egg', '.parquet',
    '.feather', '.sqlite', '.db'
)

function Initialize-Paths {
    if (-not (Test-Path -LiteralPath $SourceRoot -PathType Container)) {
        throw "Source root does not exist: $SourceRoot"
    }
    if (-not (Test-Path -LiteralPath $DestinationRoot -PathType Container)) {
        throw "Destination root does not exist: $DestinationRoot"
    }
    $logDir = Split-Path -Parent $LogPath
    if (-not (Test-Path -LiteralPath $logDir)) {
        New-Item -ItemType Directory -Path $logDir -Force | Out-Null
    }
    $pidDir = Split-Path -Parent $PidPath
    if (-not (Test-Path -LiteralPath $pidDir)) {
        New-Item -ItemType Directory -Path $pidDir -Force | Out-Null
    }
}

function Write-Log {
    param([string]$Message)
    $line = '{0} {1}' -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'), $Message
    Add-Content -LiteralPath $LogPath -Value $line -Encoding UTF8
}

function Get-FullPathWithSlash {
    param([string]$Path)
    return ([IO.Path]::GetFullPath($Path).TrimEnd('\') + '\')
}

function Get-RelativePath {
    param([string]$BasePath, [string]$Path)
    $baseFull = Get-FullPathWithSlash $BasePath
    $pathFull = [IO.Path]::GetFullPath($Path)
    $baseUri = [Uri]$baseFull
    $pathUri = [Uri]$pathFull
    return [Uri]::UnescapeDataString($baseUri.MakeRelativeUri($pathUri).ToString()).Replace('/', '\')
}

function Get-PathSegments {
    param([string]$RelativePath)
    return @($RelativePath -split '[\\/]' | Where-Object { $_ } | ForEach-Object { $_.ToLowerInvariant() })
}

function Test-HasAnySegment {
    param([string[]]$Segments, [string[]]$Blocked)
    foreach ($segment in $Segments) {
        if ($Blocked -contains $segment) {
            return $true
        }
    }
    return $false
}

function Test-UnderSource {
    param([string[]]$Segments)
    return ($Segments.Count -gt 0 -and $Segments[0] -eq 'source')
}

function Test-SkipDirectory {
    param([System.IO.DirectoryInfo]$Directory)
    $rel = Get-RelativePath $SourceRoot $Directory.FullName
    $segments = Get-PathSegments $rel
    if (Test-HasAnySegment $segments $BaseSkipSegments) {
        return $true
    }
    if (Test-UnderSource $segments) {
        if (Test-HasAnySegment $segments $SourceArtifactSegments) {
            return $true
        }
        if (Test-HasAnySegment $segments $DatasetSegments) {
            return $true
        }
    }
    return $false
}

function Get-CandidateFiles {
    $stack = New-Object System.Collections.Stack
    $stack.Push((Get-Item -LiteralPath $SourceRoot))

    while ($stack.Count -gt 0) {
        $current = [System.IO.DirectoryInfo]$stack.Pop()
        foreach ($item in Get-ChildItem -LiteralPath $current.FullName -Force -ErrorAction SilentlyContinue) {
            if ($item.PSIsContainer) {
                if (-not (Test-SkipDirectory $item)) {
                    $stack.Push($item)
                }
                continue
            }
            $item
        }
    }
}

function Test-ShouldSyncFile {
    param([System.IO.FileInfo]$File)
    if ($File.Name.StartsWith('~$')) {
        return $false
    }

    $rel = Get-RelativePath $SourceRoot $File.FullName
    $segments = Get-PathSegments $rel
    if (Test-HasAnySegment $segments $BaseSkipSegments) {
        return $false
    }

    $ext = $File.Extension.ToLowerInvariant()
    $name = $File.Name
    $underSource = Test-UnderSource $segments

    if ($underSource) {
        if (Test-HasAnySegment $segments $SourceArtifactSegments) {
            return $false
        }
        if (Test-HasAnySegment $segments $DatasetSegments) {
            return $false
        }
        if ($SourceArtifactExtensions -contains $ext) {
            return $false
        }
        if ($AlwaysCodeNames -contains $name) {
            return $true
        }
        if ($DocumentExtensions -contains $ext) {
            return $true
        }
        if ($SourceCodeExtensions -contains $ext) {
            if ($ext -eq '.json' -and $File.Length -gt 1MB) {
                return $false
            }
            return $true
        }
        return $false
    }

    return ($DocumentExtensions -contains $ext)
}

function Copy-IfNeeded {
    param([System.IO.FileInfo]$SourceFile)

    $rel = Get-RelativePath $SourceRoot $SourceFile.FullName
    $destPath = Join-Path $DestinationRoot $rel
    $destDir = Split-Path -Parent $destPath
    if (-not (Test-Path -LiteralPath $destDir)) {
        New-Item -ItemType Directory -Path $destDir -Force | Out-Null
    }

    $needsCopy = $true
    if (Test-Path -LiteralPath $destPath -PathType Leaf) {
        $destFile = Get-Item -LiteralPath $destPath
        $timeDelta = [Math]::Abs(($SourceFile.LastWriteTimeUtc - $destFile.LastWriteTimeUtc).TotalSeconds)
        $needsCopy = ($SourceFile.Length -ne $destFile.Length -or $timeDelta -gt 2)
    }

    if ($needsCopy) {
        Copy-Item -LiteralPath $SourceFile.FullName -Destination $destPath -Force
        (Get-Item -LiteralPath $destPath).LastWriteTimeUtc = $SourceFile.LastWriteTimeUtc
        return $rel.Replace('\', '/')
    }
    return $null
}

function Invoke-Git {
    param([string[]]$Arguments, [switch]$AllowFailure)
    $oldErrorActionPreference = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    try {
        $output = & git -C $DestinationRoot @Arguments 2>&1
        $exitCode = $LASTEXITCODE
    }
    finally {
        $ErrorActionPreference = $oldErrorActionPreference
    }
    if ($exitCode -ne 0 -and -not $AllowFailure) {
        throw "git $($Arguments -join ' ') failed ($exitCode): $output"
    }
    return [PSCustomObject]@{ ExitCode = $exitCode; Output = $output }
}

function Add-GitPaths {
    param([string[]]$Paths)
    $chunk = New-Object System.Collections.Generic.List[string]
    foreach ($path in $Paths) {
        $chunk.Add($path)
        if ($chunk.Count -ge 80) {
            Invoke-Git (@('add', '--') + @($chunk)) | Out-Null
            $chunk.Clear()
        }
    }
    if ($chunk.Count -gt 0) {
        Invoke-Git (@('add', '--') + @($chunk)) | Out-Null
    }
}

function Invoke-GitCommitAndPush {
    param([string[]]$ChangedPaths)
    $trackable = New-Object System.Collections.Generic.List[string]
    foreach ($path in ($ChangedPaths | Sort-Object -Unique)) {
        $ignoreResult = Invoke-Git @('check-ignore', '-q', '--', $path) -AllowFailure
        if ($ignoreResult.ExitCode -ne 0) {
            $trackable.Add($path)
        }
    }

    if ($trackable.Count -eq 0) {
        Write-Log 'No trackable files to commit after sync.'
        return
    }

    Invoke-Git @('pull', '--ff-only', 'origin', 'main') | Out-Null
    Add-GitPaths @($trackable)
    $staged = Invoke-Git @('diff', '--cached', '--name-only') | Select-Object -ExpandProperty Output
    if (-not $staged) {
        Write-Log 'Synced files matched existing git content; no commit needed.'
        return
    }

    $message = 'Auto sync docs/source code {0}' -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
    Invoke-Git @('commit', '-m', $message) | Out-Null
    Invoke-Git @('push', 'origin', 'main') | Out-Null
    Write-Log ("Committed and pushed {0} path(s)." -f $trackable.Count)
}

function Invoke-PushPending {
    $aheadResult = Invoke-Git @('rev-list', '--count', 'origin/main..HEAD') -AllowFailure
    if ($aheadResult.ExitCode -ne 0 -or -not $aheadResult.Output) {
        return
    }
    $ahead = 0
    if ([int]::TryParse(($aheadResult.Output | Select-Object -First 1), [ref]$ahead) -and $ahead -gt 0) {
        Write-Log ("Pushing {0} pending local commit(s)." -f $ahead)
        Invoke-Git @('push', 'origin', 'main') | Out-Null
        Write-Log 'Pending local commits pushed.'
    }
}

function Invoke-SyncOnce {
    param([string]$Reason = 'manual')
    Initialize-Paths
    Write-Log "Sync scan started: $Reason"

    $changed = New-Object System.Collections.Generic.List[string]
    $scanned = 0
    foreach ($file in Get-CandidateFiles) {
        if (Test-ShouldSyncFile $file) {
            $scanned++
            $rel = Copy-IfNeeded $file
            if ($rel) {
                $changed.Add($rel)
            }
        }
    }

    Write-Log ("Sync scan finished. Eligible={0}; Copied={1}." -f $scanned, $changed.Count)
    if ($changed.Count -gt 0) {
        Invoke-GitCommitAndPush @($changed)
    } else {
        Invoke-PushPending
    }
}

function Invoke-SyncSafely {
    param([string]$Reason)
    try {
        Invoke-SyncOnce $Reason
    }
    catch {
        Write-Log ("ERROR during sync ({0}): {1}" -f $Reason, $_.Exception.Message)
    }
}

function Get-PowerShellExecutable {
    $pwsh = Get-Command pwsh -ErrorAction SilentlyContinue
    if ($pwsh) {
        return $pwsh.Source
    }
    return (Get-Command powershell.exe).Source
}

function Install-AutoSyncTask {
    Initialize-Paths
    $psExe = Get-PowerShellExecutable
    $args = '-NoProfile -ExecutionPolicy Bypass -File "{0}" -Mode watch' -f $ScriptPath
    $action = New-ScheduledTaskAction -Execute $psExe -Argument $args
    $trigger = New-ScheduledTaskTrigger -AtLogOn
    $settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -MultipleInstances IgnoreNew
    Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger -Settings $settings -Description 'Sync research documents and source code to GitHub.' -Force | Out-Null
    Write-Log "Scheduled task installed: $TaskName"
}

function Start-AutoSyncProcess {
    Initialize-Paths
    if (Test-Path -LiteralPath $PidPath) {
        $existingPid = Get-Content -LiteralPath $PidPath -ErrorAction SilentlyContinue | Select-Object -First 1
        if ($existingPid -and (Get-Process -Id ([int]$existingPid) -ErrorAction SilentlyContinue)) {
            Write-Output "Already running with PID $existingPid"
            return
        }
    }
    $psExe = Get-PowerShellExecutable
    $args = '-NoProfile -ExecutionPolicy Bypass -File "{0}" -Mode watch' -f $ScriptPath
    $process = Start-Process -FilePath $psExe -ArgumentList $args -WindowStyle Hidden -PassThru
    Write-Output "Started watcher PID $($process.Id)"
}

function Stop-AutoSyncProcess {
    Initialize-Paths
    if (-not (Test-Path -LiteralPath $PidPath)) {
        Write-Output 'No PID file found.'
        return
    }
    $existingPid = Get-Content -LiteralPath $PidPath -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($existingPid -and (Get-Process -Id ([int]$existingPid) -ErrorAction SilentlyContinue)) {
        Stop-Process -Id ([int]$existingPid) -Force
        Write-Output "Stopped watcher PID $existingPid"
    } else {
        Write-Output 'Watcher process was not running.'
    }
    Remove-Item -LiteralPath $PidPath -Force -ErrorAction SilentlyContinue
}

function Show-AutoSyncStatus {
    Initialize-Paths
    $pidText = $null
    $running = $false
    if (Test-Path -LiteralPath $PidPath) {
        $pidText = Get-Content -LiteralPath $PidPath -ErrorAction SilentlyContinue | Select-Object -First 1
        if ($pidText) {
            $running = [bool](Get-Process -Id ([int]$pidText) -ErrorAction SilentlyContinue)
        }
    }
    $task = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
    [PSCustomObject]@{
        WatcherRunning = $running
        Pid = $pidText
        TaskInstalled = [bool]$task
        TaskState = if ($task) { $task.State } else { $null }
        LogPath = $LogPath
    }
}

function Start-WatchLoop {
    Initialize-Paths
    Set-Content -LiteralPath $PidPath -Value $PID -Encoding ASCII
    Write-Log "Watcher started. PID=$PID"
    $watcher = $null
    $subscriptions = @()
    try {
        Invoke-SyncSafely 'startup'

        $global:ResearchDetectingPendingSync = $false
        $global:ResearchDetectingLastEventUtc = [DateTime]::UtcNow
        $lastFullScanUtc = [DateTime]::UtcNow

        $watcher = New-Object System.IO.FileSystemWatcher
        $watcher.Path = $SourceRoot
        $watcher.IncludeSubdirectories = $true
        $watcher.NotifyFilter = [IO.NotifyFilters]'FileName, DirectoryName, LastWrite, Size'
        $watcher.EnableRaisingEvents = $true

        $action = {
            $global:ResearchDetectingPendingSync = $true
            $global:ResearchDetectingLastEventUtc = [DateTime]::UtcNow
        }

        $subscriptions = @()
        $subscriptions += Register-ObjectEvent -InputObject $watcher -EventName Created -Action $action
        $subscriptions += Register-ObjectEvent -InputObject $watcher -EventName Changed -Action $action
        $subscriptions += Register-ObjectEvent -InputObject $watcher -EventName Renamed -Action $action

        Write-Log 'File watcher armed.'
        while ($true) {
            Start-Sleep -Seconds 2
            $now = [DateTime]::UtcNow
            if ($global:ResearchDetectingPendingSync -and (($now - $global:ResearchDetectingLastEventUtc).TotalSeconds -ge $DebounceSeconds)) {
                $global:ResearchDetectingPendingSync = $false
                Invoke-SyncSafely 'filesystem event'
                $lastFullScanUtc = [DateTime]::UtcNow
            }
            if (($now - $lastFullScanUtc).TotalSeconds -ge $FullScanSeconds) {
                Invoke-SyncSafely 'periodic full scan'
                $lastFullScanUtc = [DateTime]::UtcNow
            }
        }
    }
    catch {
        Write-Log ("FATAL watcher error: {0}" -f $_.Exception.Message)
        throw
    }
    finally {
        foreach ($subscription in $subscriptions) {
            Unregister-Event -SubscriptionId $subscription.Id -ErrorAction SilentlyContinue
        }
        if ($watcher) {
            $watcher.Dispose()
        }
        Remove-Item -LiteralPath $PidPath -Force -ErrorAction SilentlyContinue
        Write-Log 'Watcher stopped.'
    }
}

switch ($Mode) {
    'once' { Invoke-SyncOnce 'manual once' }
    'install' { Install-AutoSyncTask }
    'uninstall' {
        Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue
        Write-Log "Scheduled task uninstalled: $TaskName"
    }
    'start' { Start-AutoSyncProcess }
    'stop' { Stop-AutoSyncProcess }
    'status' { Show-AutoSyncStatus | Format-List }
    'watch' { Start-WatchLoop }
}
