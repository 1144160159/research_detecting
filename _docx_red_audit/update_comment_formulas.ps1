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

function Get-CommentId {
    param([string]$Text)

    $marked = [regex]::Match($Text, '^\[[^0-9]*(\d{3})/154')
    if ($marked.Success) {
        return ('M{0:D3}' -f [int]$marked.Groups[1].Value)
    }

    $supplemental = [regex]::Match($Text, '^\[[^0-9]*(\d{2})/26')
    if ($supplemental.Success) {
        return ('S{0:D2}' -f [int]$supplemental.Groups[1].Value)
    }

    return $null
}

function Convert-MathPlaceholders {
    param(
        $Document,
        $Comment,
        [string]$CommentId,
        [System.Collections.Generic.List[object]]$Failures,
        [System.Collections.Generic.List[object]]$BuildUpWarnings
    )

    $commentText = [string]$Comment.Range.Text
    $placeholderMatches = [regex]::Matches($commentText, '\[\[MATH:(.*?)\]\]')
    $built = 0

    for ($index = $placeholderMatches.Count - 1; $index -ge 0; $index--) {
        $placeholderMatch = $placeholderMatches[$index]
        $mathText = [string]$placeholderMatch.Groups[1].Value
        $mathRange = $null
        $maths = $null
        $omath = $null
        $stage = 'prepare-range'

        try {
            $mathRange = $Comment.Range.Duplicate
            $start = $Comment.Range.Start + $placeholderMatch.Index
            $end = $start + $placeholderMatch.Length
            $mathRange.SetRange($start, $end)
            $mathRange.Text = $mathText
            $stage = 'set-font'
            $mathRange.Font.Name = 'Cambria Math'
            $mathRange.Font.NameAscii = 'Cambria Math'
            $mathRange.Font.NameOther = 'Cambria Math'
            $mathRange.Font.Size = 10.5

            $stage = 'add-omath'
            [void]$Document.OMaths.Add($mathRange)
            $stage = 'read-omath'
            $maths = $mathRange.OMaths
            if ($maths.Count -ne 1) {
                throw "Expected one OMath object, got $($maths.Count)."
            }
            $omath = $maths.Item(1)
            $built++

            if ([regex]::IsMatch($mathText, '[_\^/]')) {
                $stage = 'build-up'
                try {
                    $omath.BuildUp()
                }
                catch {
                    $BuildUpWarnings.Add([ordered]@{
                        comment_id = $CommentId
                        formula = $mathText
                        message = $_.Exception.Message
                    })
                }
            }
        }
        catch {
            $Failures.Add([ordered]@{
                comment_id = $CommentId
                formula = $mathText
                message = ($stage + ': ' + $_.Exception.Message)
            })
        }
        finally {
            Release-ComObject $omath
            Release-ComObject $maths
            Release-ComObject $mathRange
        }
    }

    return [ordered]@{
        requested = $placeholderMatches.Count
        built = $built
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
$specById = @{}
foreach ($spec in $specs) {
    $id = [string]$spec.id
    if ($specById.ContainsKey($id)) {
        throw "Duplicate specification id: $id"
    }
    $specById[$id] = $spec
}

$failures = New-Object 'System.Collections.Generic.List[object]'
$buildUpWarnings = New-Object 'System.Collections.Generic.List[object]'
$unmatchedComments = New-Object 'System.Collections.Generic.List[object]'
$seen = @{}
$updated = 0
$formulaRequested = 0
$formulaBuilt = 0
$documentCommentCount = 0
$missingSpecs = @()
$preSavePassed = $false
$word = $null
$document = $null
$oldUserName = $null
$oldInitials = $null

try {
    $word = New-Object -ComObject Word.Application
    $word.Visible = $false
    $word.DisplayAlerts = 0
    $oldUserName = $word.UserName
    $oldInitials = $word.UserInitials
    $word.UserName = ([char]0x738B).ToString() + ([char]0x6587).ToString() + ([char]0x540C).ToString()
    $word.UserInitials = 'WWT'

    $document = $word.Documents.Open($outputPath, $false, $false)
    $document.TrackRevisions = $false
    $documentCommentCount = $document.Comments.Count

    for ($commentIndex = 1; $commentIndex -le $document.Comments.Count; $commentIndex++) {
        $comment = $null
        $commentRange = $null
        try {
            $comment = $document.Comments.Item($commentIndex)
            $commentRange = $comment.Range
            $commentId = Get-CommentId -Text ([string]$commentRange.Text)
            if ($null -eq $commentId -or -not $specById.ContainsKey($commentId)) {
                $unmatchedComments.Add([ordered]@{
                    index = $commentIndex
                    prefix = ([string]$commentRange.Text).Substring(0, [Math]::Min(40, ([string]$commentRange.Text).Length))
                })
                continue
            }
            if ($seen.ContainsKey($commentId)) {
                $failures.Add([ordered]@{
                    comment_id = $commentId
                    formula = ''
                    message = 'Duplicate comment id in document.'
                })
                continue
            }

            $seen[$commentId] = $true
            $commentRange.Text = ([string]$specById[$commentId].text).Trim()
            $conversion = Convert-MathPlaceholders -Document $document -Comment $comment -CommentId $commentId -Failures $failures -BuildUpWarnings $buildUpWarnings
            $formulaRequested += [int]$conversion.requested
            $formulaBuilt += [int]$conversion.built
            $updated++
        }
        finally {
            Release-ComObject $commentRange
            Release-ComObject $comment
        }
    }

    $missingSpecs = @($specById.Keys | Where-Object { -not $seen.ContainsKey($_) } | Sort-Object)
    $preSavePassed = (
        $unmatchedComments.Count -eq 0 -and
        $missingSpecs.Count -eq 0 -and
        $failures.Count -eq 0 -and
        $updated -eq $specs.Count -and
        $formulaRequested -eq $formulaBuilt
    )
    if ($preSavePassed) {
        $document.Save()
    }
}
finally {
    if ($null -ne $document) {
        $document.Close($false)
        Release-ComObject $document
    }
    if ($null -ne $word) {
        if ($null -ne $oldUserName) { $word.UserName = $oldUserName }
        if ($null -ne $oldInitials) { $word.UserInitials = $oldInitials }
        $word.Quit()
        Release-ComObject $word
    }
    [GC]::Collect()
    [GC]::WaitForPendingFinalizers()
}

$report = [ordered]@{
    source = $sourcePath
    output = $outputPath
    specification_count = $specs.Count
    document_comment_count = $documentCommentCount
    updated_comments = $updated
    formulas_requested = $formulaRequested
    formulas_built = $formulaBuilt
    unmatched_comments = @($unmatchedComments | ForEach-Object { $_ })
    missing_specifications = @($missingSpecs)
    failures = @($failures | ForEach-Object { $_ })
    build_up_warnings = @($buildUpWarnings | ForEach-Object { $_ })
    passed = $preSavePassed
}
$report | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $ReportPath -Encoding UTF8
$report | ConvertTo-Json -Depth 8

if (-not $report.passed) {
    exit 1
}
