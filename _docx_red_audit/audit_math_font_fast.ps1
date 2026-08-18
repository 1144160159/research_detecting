param(
    [Parameter(Mandatory = $true)][string]$InputPath,
    [Parameter(Mandatory = $true)][string]$OutputPath,
    [int]$ExpectedFormulaCount = 211
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

function Release-ComObject {
    param($Object)
    if ($null -ne $Object -and [System.Runtime.InteropServices.Marshal]::IsComObject($Object)) {
        [void][System.Runtime.InteropServices.Marshal]::FinalReleaseComObject($Object)
    }
}

$word = $null
$document = $null
$records = New-Object 'System.Collections.Generic.List[object]'

try {
    $word = New-Object -ComObject Word.Application
    $word.Visible = $false
    $word.DisplayAlerts = 0
    $document = $word.Documents.Open($InputPath, $false, $true)

    for ($commentIndex = 1; $commentIndex -le $document.Comments.Count; $commentIndex++) {
        $comment = $null
        $commentRange = $null
        $maths = $null
        try {
            $comment = $document.Comments.Item($commentIndex)
            $commentRange = $comment.Range
            $maths = $commentRange.OMaths
            for ($formulaIndex = 1; $formulaIndex -le $maths.Count; $formulaIndex++) {
                $math = $null
                $range = $null
                try {
                    $math = $maths.Item($formulaIndex)
                    $range = $math.Range
                    $records.Add([pscustomobject]@{
                        comment_index = $commentIndex
                        formula_index = $formulaIndex
                        text = ($range.Text -replace "[\r\a]", '')
                        font_name = [string]$range.Font.Name
                        font_name_ascii = [string]$range.Font.NameAscii
                        font_size = [double]$range.Font.Size
                    })
                }
                finally {
                    Release-ComObject $range
                    Release-ComObject $math
                }
            }
        }
        finally {
            Release-ComObject $maths
            Release-ComObject $commentRange
            Release-ComObject $comment
        }
    }
}
finally {
    if ($null -ne $document) {
        $document.Close($false)
        Release-ComObject $document
    }
    if ($null -ne $word) {
        $word.Quit()
        Release-ComObject $word
    }
    [GC]::Collect()
    [GC]::WaitForPendingFinalizers()
}

$fontGroups = @($records | Group-Object font_name | ForEach-Object { [ordered]@{ value = $_.Name; count = $_.Count } })
$asciiFontGroups = @($records | Group-Object font_name_ascii | ForEach-Object { [ordered]@{ value = $_.Name; count = $_.Count } })
$sizeGroups = @($records | Group-Object font_size | ForEach-Object { [ordered]@{ value = $_.Name; count = $_.Count } })
$report = [ordered]@{
    input = $InputPath
    formula_count = $records.Count
    font_names = $fontGroups
    ascii_font_names = $asciiFontGroups
    font_sizes = $sizeGroups
    wrong_font_count = @($records | Where-Object { $_.font_name_ascii -ne 'Cambria Math' }).Count
    wrong_size_count = @($records | Where-Object { [Math]::Abs($_.font_size - 10.5) -gt 0.01 }).Count
}
$report.passed = ($report.formula_count -eq $ExpectedFormulaCount -and $report.wrong_font_count -eq 0 -and $report.wrong_size_count -eq 0)
$report | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $OutputPath -Encoding UTF8
$report | ConvertTo-Json -Depth 8
if (-not $report.passed) { exit 1 }
