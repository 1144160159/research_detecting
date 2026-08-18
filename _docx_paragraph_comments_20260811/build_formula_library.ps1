param(
    [Parameter(Mandatory = $true)][string]$SpecsJson,
    [Parameter(Mandatory = $true)][string]$Output,
    [Parameter(Mandatory = $true)][string]$ReportPath
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

function Release-ComObject {
    param($Object)
    if ($null -ne $Object -and [System.Runtime.InteropServices.Marshal]::IsComObject($Object)) {
        [void][System.Runtime.InteropServices.Marshal]::FinalReleaseComObject($Object)
    }
}

$specs = Get-Content -LiteralPath (Resolve-Path -LiteralPath $SpecsJson).Path -Raw -Encoding UTF8 | ConvertFrom-Json
$formulas = New-Object 'System.Collections.Generic.List[string]'
foreach ($spec in $specs) {
    foreach ($match in [regex]::Matches([string]$spec.text, '\[\[MATH:(.*?)\]\]')) {
        $formulas.Add([string]$match.Groups[1].Value)
    }
}

$outputParent = Split-Path -Parent $Output
if (-not (Test-Path -LiteralPath $outputParent)) {
    New-Item -ItemType Directory -Path $outputParent -Force | Out-Null
}
if (Test-Path -LiteralPath $Output) {
    Remove-Item -LiteralPath $Output -Force
}

$word = $null
$document = $null
$table = $null
$warnings = New-Object 'System.Collections.Generic.List[object]'
$failures = New-Object 'System.Collections.Generic.List[object]'
$built = 0

try {
    $word = New-Object -ComObject Word.Application
    $word.Visible = $false
    $word.DisplayAlerts = 0
    $document = $word.Documents.Add()
    # Isolate every formula in its own table cell. A cell boundary prevents
    # Word's math parser from merging adjacent formula paragraphs.
    $insertRange = $document.Range(0, 0)
    $table = $document.Tables.Add($insertRange, $formulas.Count, 1)
    Release-ComObject $insertRange
    for ($index = 1; $index -le $formulas.Count; $index++) {
        $cell = $null
        try {
            $cell = $table.Cell($index, 1)
            $cell.Range.Text = [string]$formulas[$index - 1]
        }
        finally {
            Release-ComObject $cell
        }
    }

    for ($index = $formulas.Count; $index -ge 1; $index--) {
        $cell = $null
        $range = $null
        $maths = $null
        $omath = $null
        $formula = [string]$formulas[$index - 1]
        try {
            $cell = $table.Cell($index, 1)
            $range = $cell.Range.Duplicate
            $range.SetRange($range.Start, $range.Start + $formula.Length)
            $range.Font.Name = 'Cambria Math'
            $range.Font.NameAscii = 'Cambria Math'
            $range.Font.NameOther = 'Cambria Math'
            $range.Font.Size = 10.5
            [void]$document.OMaths.Add($range)
            $maths = $range.OMaths
            if ($maths.Count -ne 1) {
                throw "Expected one OMath object, got $($maths.Count)."
            }
            $omath = $maths.Item(1)
            if ([regex]::IsMatch($formula, '[_\^/]')) {
                try { $omath.BuildUp() }
                catch {
                    $warnings.Add([ordered]@{
                        index = $index
                        formula = $formula
                        message = $_.Exception.Message
                    })
                }
            }
            $built++
        }
        catch {
            $failures.Add([ordered]@{
                index = $index
                formula = $formula
                message = $_.Exception.Message
            })
        }
        finally {
            Release-ComObject $omath
            Release-ComObject $maths
            Release-ComObject $range
            Release-ComObject $cell
        }
    }
    $document.SaveAs2($Output, 16)
}
finally {
    if ($null -ne $document) { $document.Close($false) }
    if ($null -ne $word) { $word.Quit() }
    Release-ComObject $table
    Release-ComObject $document
    Release-ComObject $word
    [GC]::Collect()
    [GC]::WaitForPendingFinalizers()
}

$report = [ordered]@{
    output = $Output
    requested = $formulas.Count
    built = $built
    warnings = $warnings
    failures = $failures
    passed = ($built -eq $formulas.Count -and $warnings.Count -eq 0 -and $failures.Count -eq 0)
}
$report | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $ReportPath -Encoding UTF8
$report | ConvertTo-Json -Depth 4

if (-not $report.passed) { exit 1 }
