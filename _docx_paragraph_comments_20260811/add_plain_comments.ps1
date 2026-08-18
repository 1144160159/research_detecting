param(
    [Parameter(Mandatory = $true)][string]$Source,
    [Parameter(Mandatory = $true)][string]$Output,
    [Parameter(Mandatory = $true)][string]$SpecsJson,
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

$sourcePath = (Resolve-Path -LiteralPath $Source).Path
$specsPath = (Resolve-Path -LiteralPath $SpecsJson).Path
$outputParent = Split-Path -Parent $Output
if (-not (Test-Path -LiteralPath $outputParent)) {
    New-Item -ItemType Directory -Path $outputParent -Force | Out-Null
}
Copy-Item -LiteralPath $sourcePath -Destination $Output -Force
$outputPath = (Resolve-Path -LiteralPath $Output).Path
$specs = Get-Content -LiteralPath $specsPath -Raw -Encoding UTF8 | ConvertFrom-Json

$word = $null
$document = $null
$oldUserName = $null
$oldInitials = $null
$anchors = New-Object 'System.Collections.Generic.List[object]'
$passed = $false
$commentAuthor = [string]::Concat([char]0x738B, [char]0x6587, [char]0x540C)

try {
    $word = New-Object -ComObject Word.Application
    $word.Visible = $false
    $word.DisplayAlerts = 0
    $oldUserName = $word.UserName
    $oldInitials = $word.UserInitials
    $word.UserName = $commentAuthor
    $word.UserInitials = 'WWT'

    $document = $word.Documents.Open($outputPath, $false, $false)
    foreach ($spec in $specs) {
        $paragraph = $null
        $anchor = $null
        $comment = $null
        try {
            $paragraph = $document.Paragraphs.Item([int]$spec.paragraph_index)
            $anchor = $paragraph.Range.Duplicate
            if ($anchor.End -gt $anchor.Start) {
                $anchor.End = $anchor.End - 1
            }
            $anchorText = [string]$anchor.Text
            $comment = $document.Comments.Add($anchor, [string]$spec.text)
            $comment.Author = $commentAuthor
            $comment.Initial = 'WWT'
            $anchors.Add([ordered]@{
                id = [string]$spec.id
                paragraph_index = [int]$spec.paragraph_index
                anchor_text = $anchorText
            })
        }
        finally {
            Release-ComObject $comment
            Release-ComObject $anchor
            Release-ComObject $paragraph
        }
    }
    $document.Save()
    $passed = ($document.Comments.Count -eq $specs.Count)
}
finally {
    if ($null -ne $document) {
        $document.Close($false)
    }
    if ($null -ne $word) {
        if ($null -ne $oldUserName) { $word.UserName = $oldUserName }
        if ($null -ne $oldInitials) { $word.UserInitials = $oldInitials }
        $word.Quit()
    }
    Release-ComObject $document
    Release-ComObject $word
    [GC]::Collect()
    [GC]::WaitForPendingFinalizers()
}

$report = [ordered]@{
    source = $sourcePath
    output = $outputPath
    comments_added = $anchors.Count
    anchors = $anchors
    passed = $passed
}
$report | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $ReportPath -Encoding UTF8
$report | ConvertTo-Json -Depth 4

if (-not $passed) {
    exit 1
}
