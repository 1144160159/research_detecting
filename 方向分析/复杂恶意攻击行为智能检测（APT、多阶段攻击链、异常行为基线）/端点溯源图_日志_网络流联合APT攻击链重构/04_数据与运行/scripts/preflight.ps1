param(
    [string]$ProjectRoot = "",
    [string]$JsonOut = ""
)

$ErrorActionPreference = "Stop"
$OutputEncoding = [Console]::OutputEncoding = [Text.UTF8Encoding]::new()

function Find-ProjectRoot {
    param([string]$Start)
    $cursor = Get-Item -LiteralPath $Start
    if (-not $cursor.PSIsContainer) { $cursor = $cursor.Directory }
    while ($null -ne $cursor) {
        $hasPaper = Test-Path -LiteralPath (Join-Path $cursor.FullName "paper")
        $hasSource = Test-Path -LiteralPath (Join-Path $cursor.FullName "source")
        if ($hasPaper -and $hasSource) { return $cursor.FullName }
        $cursor = $cursor.Parent
    }
    throw "Cannot locate project root containing paper/ and source/."
}

if ([string]::IsNullOrWhiteSpace($ProjectRoot)) {
    $ProjectRoot = Find-ProjectRoot -Start $PSScriptRoot
} else {
    $ProjectRoot = (Resolve-Path -LiteralPath $ProjectRoot).Path
}

$repoSpecs = @(
    @{ Name = "TeRed"; Path = "source/TeRed"; Required = @("README.md", "main.py", "settings.py", "test_data") },
    @{ Name = "Krystal"; Path = "source/Krystal"; Required = @("README.md", "pom.xml", "config.yaml", "experiment/input", "experiment/query") },
    @{ Name = "Euler"; Path = "source/Euler"; Required = @("README.md", "euler", "lanl_experiments") },
    @{ Name = "eaGle"; Path = "source/eaGle"; Required = @("README.md", "anomaly_detection") },
    @{ Name = "TraceCluster"; Path = "source/TraceCluster"; Required = @("README.md", "train.py", "test.py") },
    @{ Name = "Open-CyKG"; Path = "source/Open-CyKG"; Required = @("README.md", "KG_goldStandard") },
    @{ Name = "DIDS-MFL"; Path = "source/DIDS-MFL"; Required = @("README.md", "main.py", "data") }
)

$paperSpecs = @(
    "paper/10.1016_j.cose.2022.102828.pdf",
    "paper/10.14722_ndss.2022.24107.pdf",
    "paper/10.1016_j.eswa.2024.125877.pdf",
    "paper/10.1016_j.jnca.2024.104036.pdf",
    "paper/10.1109_TIFS.2025.3588251.pdf",
    "paper/10.1109_TIFS.2025.3601381.pdf",
    "paper/10.1109_TDSC.2025.3611866.pdf",
    "paper/10.1109_TDSC.2025.3640696.pdf",
    "paper/10.1109_TIFS.2026.3653175.pdf",
    "paper/10.1109_TDSC.2025.3646355.pdf"
)

$repos = foreach ($spec in $repoSpecs) {
    $full = Join-Path $ProjectRoot $spec.Path
    $exists = Test-Path -LiteralPath $full
    $missing = @()
    if ($exists) {
        foreach ($item in $spec.Required) {
            if (-not (Test-Path -LiteralPath (Join-Path $full $item))) { $missing += $item }
        }
        $files = @(Get-ChildItem -LiteralPath $full -Recurse -File -ErrorAction SilentlyContinue)
        $bytes = ($files | Measure-Object -Property Length -Sum).Sum
    } else {
        $files = @()
        $bytes = 0
        $missing = @($spec.Required)
    }
    [pscustomobject]@{
        name = $spec.Name
        path = $spec.Path
        exists = $exists
        file_count = $files.Count
        bytes = [int64]$bytes
        missing_required = $missing
    }
}

$papers = foreach ($rel in $paperSpecs) {
    $full = Join-Path $ProjectRoot $rel
    $exists = Test-Path -LiteralPath $full
    $size = if ($exists) { (Get-Item -LiteralPath $full).Length } else { 0 }
    [pscustomobject]@{ path = $rel; exists = $exists; bytes = [int64]$size }
}

$specialChecks = @(
    @{ name = "TeRed CVE attack JSON"; path = "source/TeRed/test_data/cve-2016-4971-attack/cve-2016-4971-attack.json" },
    @{ name = "TeRed DeepLog attack log"; path = "source/TeRed/deeplog/output/attack.log" },
    @{ name = "eaGle ground truth UUID"; path = "source/eaGle/anomaly_detection/groundtruth_uuid.txt" },
    @{ name = "Euler requirements"; path = "source/Euler/requirements.txt" },
    @{ name = "Krystal configuration"; path = "source/Krystal/config.yaml" },
    @{ name = "Krystal forward reconstruction query"; path = "source/Krystal/experiment/query/forwardAnalysis.sparql" },
    @{ name = "Euler EGCN-H link placeholder"; path = "source/Euler/lanl_experiments/models/egcn_h.py" },
    @{ name = "DIDS-MFL CIC-BoT-IoT artifact"; path = "source/DIDS-MFL/data/CIC-BoT-IoT.pt" },
    @{ name = "TraceCluster feature map"; path = "source/TraceCluster/feature.txt" },
    @{ name = "TraceCluster label map"; path = "source/TraceCluster/label.txt" },
    @{ name = "TraceCluster ground truth"; path = "source/TraceCluster/groundtruth.txt" }
)

$special = foreach ($check in $specialChecks) {
    $full = Join-Path $ProjectRoot $check.path
    $exists = Test-Path -LiteralPath $full
    $size = if ($exists -and -not (Get-Item -LiteralPath $full).PSIsContainer) {
        (Get-Item -LiteralPath $full).Length
    } else { 0 }
    [pscustomobject]@{ name = $check.name; path = $check.path; exists = $exists; bytes = [int64]$size }
}

$pythonCandidates = @(
    "D:/soft/Anaconda3/python.exe",
    (Get-Command python -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Source -First 1)
) | Where-Object { -not [string]::IsNullOrWhiteSpace($_) } | Select-Object -Unique

$python = foreach ($candidate in $pythonCandidates) {
    $exists = Test-Path -LiteralPath $candidate
    $version = ""
    if ($exists) {
        try { $version = (& $candidate --version 2>&1 | Out-String).Trim() } catch { $version = $_.Exception.Message }
    }
    [pscustomobject]@{ path = $candidate; exists = $exists; version = $version }
}

$report = [pscustomobject]@{
    generated_at = (Get-Date).ToString("o")
    project_root = $ProjectRoot
    repositories = @($repos)
    core_papers = @($papers)
    special_files = @($special)
    python = @($python)
    notes = @(
        "Presence does not imply reproducibility.",
        "TraceCluster upstream README states that the complete implementation is not included.",
        "Krystal requires a compatible JVM and an RDF/SPARQL backend for the default live-store workflow.",
        "Euler contains relative-path placeholder files that require symlink restoration or import repair on Windows.",
        "A joint endpoint-log-flow dataset has not been confirmed by this preflight."
    )
}

$report | ConvertTo-Json -Depth 8

if (-not [string]::IsNullOrWhiteSpace($JsonOut)) {
    $parent = Split-Path -Parent $JsonOut
    if ($parent -and -not (Test-Path -LiteralPath $parent)) {
        New-Item -ItemType Directory -Path $parent -Force | Out-Null
    }
    $report | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $JsonOut -Encoding UTF8
}
