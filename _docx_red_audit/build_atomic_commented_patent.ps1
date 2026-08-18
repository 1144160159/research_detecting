param(
    [Parameter(Mandatory=$true)][string]$Source,
    [Parameter(Mandatory=$true)][string]$Output,
    [Parameter(Mandatory=$true)][string]$SpecsJson,
    [string]$RunReport = '',
    [switch]$PreflightOnly
)

$ErrorActionPreference = 'Stop'

function Copy-FileShared {
    param([string]$From, [string]$To)
    $inputStream = [System.IO.File]::Open(
        $From,
        [System.IO.FileMode]::Open,
        [System.IO.FileAccess]::Read,
        [System.IO.FileShare]::ReadWrite
    )
    try {
        $outputStream = [System.IO.File]::Open(
            $To,
            [System.IO.FileMode]::Create,
            [System.IO.FileAccess]::Write,
            [System.IO.FileShare]::None
        )
        try { $inputStream.CopyTo($outputStream) }
        finally { $outputStream.Dispose() }
    }
    finally { $inputStream.Dispose() }
}

function Find-TextRange {
    param($BaseRange,[string]$Text,[int]$Occurrence = 1)
    $boundaryEnd = $BaseRange.End
    $search = $BaseRange.Duplicate
    for ($index = 1; $index -le $Occurrence; $index++) {
        $find = $search.Find
        $find.ClearFormatting()
        $find.Replacement.ClearFormatting()
        $find.Text = $Text
        $find.Forward = $true
        $find.Wrap = 0
        $find.Format = $false
        $find.MatchCase = $true
        $find.MatchWholeWord = $false
        $find.MatchWildcards = $false
        $found = $find.Execute()
        [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($find)
        if (-not $found) {
            [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($search)
            return $null
        }
        if ($index -eq $Occurrence) {
            return $search
        }
        $nextStart = $search.End
        $search.SetRange($nextStart,$boundaryEnd)
    }
    [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($search)
    return $null
}

function Find-AnchoredRange {
    param(
        $Document,
        [string]$Context,
        [string]$Anchor,
        [int]$Occurrence = 1,
        [int]$ContextOccurrence = 1
    )
    $documentRange = $Document.Content.Duplicate
    $contextRange = Find-TextRange -BaseRange $documentRange -Text $Context -Occurrence $ContextOccurrence
    [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($documentRange)

    if ($null -ne $contextRange) {
        $paragraph = $contextRange.Paragraphs.Item(1)
        $paragraphRange = $paragraph.Range.Duplicate
        [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($paragraph)
        [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($contextRange)
        $anchorRange = Find-TextRange -BaseRange $paragraphRange -Text $Anchor -Occurrence $Occurrence
        [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($paragraphRange)
        if ($null -ne $anchorRange) { return $anchorRange }
    }

    # A missing context must fail preflight. Falling back to a global repeated
    # phrase can silently attach a technically correct comment to the wrong issue.
    return $null
}

function Convert-MathPlaceholders {
    param($Document,$Comment)
    $commentText = $Comment.Range.Text
    $matches = [regex]::Matches($commentText,'\[\[MATH:(.*?)\]\]')
    for ($index = $matches.Count - 1; $index -ge 0; $index--) {
        $match = $matches[$index]
        $mathText = $match.Groups[1].Value
        $mathRange = $Comment.Range.Duplicate
        $start = $Comment.Range.Start + $match.Index
        $end = $start + $match.Length
        $mathRange.SetRange($start,$end)
        $mathRange.Text = $mathText
        $mathRange.Font.Name = 'Cambria Math'
        $mathRange.Font.NameAscii = 'Cambria Math'
        $mathRange.Font.NameOther = 'Cambria Math'
        [void]$Document.OMaths.Add($mathRange)
        $omath = $mathRange.OMaths.Item(1)
        try { $omath.BuildUp() } catch { }
        [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($omath)
        [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($mathRange)
    }
}

$specs = Get-Content -LiteralPath $SpecsJson -Raw -Encoding UTF8 | ConvertFrom-Json
$outputParent = Split-Path -Parent $Output
if (-not (Test-Path -LiteralPath $outputParent)) {
    New-Item -ItemType Directory -Path $outputParent -Force | Out-Null
}
if (Test-Path -LiteralPath $Output) { Remove-Item -LiteralPath $Output -Force }
Copy-FileShared -From $Source -To $Output

$word = $null
$document = $null
$oldUserName = $null
$oldInitials = $null
$missing = New-Object System.Collections.Generic.List[object]
$records = New-Object System.Collections.Generic.List[object]
$failed = $false

try {
    $word = New-Object -ComObject Word.Application
    $word.Visible = $false
    $word.DisplayAlerts = 0
    $oldUserName = $word.UserName
    $oldInitials = $word.UserInitials
    $word.UserName = ([char]0x738B).ToString() + ([char]0x6587).ToString() + ([char]0x540C).ToString()
    $word.UserInitials = 'WWT'

    $document = $word.Documents.Open($Output,$false,$false)
    $document.TrackRevisions = $false
    while ($document.Comments.Count -gt 0) {
        $existing = $document.Comments.Item(1)
        $existing.Delete()
        [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($existing)
    }

    foreach ($spec in $specs) {
        $anchorRange = Find-AnchoredRange `
            -Document $document `
            -Context ([string]$spec.context) `
            -Anchor ([string]$spec.anchor) `
            -Occurrence ([int]$spec.occurrence) `
            -ContextOccurrence ([int]$spec.context_occurrence)

        if ($null -eq $anchorRange) {
            $missing.Add([pscustomobject]@{
                id = [string]$spec.id
                context = [string]$spec.context
                anchor = [string]$spec.anchor
                occurrence = [int]$spec.occurrence
                context_occurrence = [int]$spec.context_occurrence
            })
            continue
        }

        $anchorText = $anchorRange.Text
        $highlight = $anchorRange.HighlightColorIndex
        $fontColor = $anchorRange.Font.Color
        $records.Add([pscustomobject]@{
            id = [string]$spec.id
            kind = [string]$spec.kind
            group = $spec.group
            anchor = [string]$spec.anchor
            anchor_text = [string]$anchorText
            highlight = [int]$highlight
            font_color = [int]$fontColor
        })
        if (-not $PreflightOnly) {
            $comment = $document.Comments.Add($anchorRange,([string]$spec.text).Trim())
            Convert-MathPlaceholders -Document $document -Comment $comment
            [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($comment)
        }
        [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($anchorRange)
    }

    $failed = $missing.Count -gt 0
    if (-not $failed -and -not $PreflightOnly) {
        $document.Save()
    }
}
finally {
    if ($null -ne $document) {
        $document.Close($false)
        [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($document)
    }
    if ($null -ne $word) {
        if ($null -ne $oldUserName) { $word.UserName = $oldUserName }
        if ($null -ne $oldInitials) { $word.UserInitials = $oldInitials }
        $word.Quit()
        [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($word)
    }
    [GC]::Collect()
    [GC]::WaitForPendingFinalizers()
}

$report = [ordered]@{
    source = $Source
    output = $Output
    specs = $SpecsJson
    expected = $specs.Count
    added = $records.Count
    missing = $missing.ToArray()
    records = $records.ToArray()
}
if ($RunReport) {
    $report | ConvertTo-Json -Depth 7 | Set-Content -LiteralPath $RunReport -Encoding UTF8
}

Write-Output ('OUTPUT=' + $Output)
Write-Output ('COMMENTS_ADDED=' + $records.Count)
Write-Output ('MISSING=' + $missing.Count)
if ($failed) {
    throw ('UNMATCHED_ANCHOR_COUNT=' + $missing.Count)
}
