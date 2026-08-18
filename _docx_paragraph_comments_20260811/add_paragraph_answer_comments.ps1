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

function Convert-MathPlaceholders {
    param(
        $Document,
        $Comment,
        [string]$CommentId,
        [System.Collections.Generic.List[object]]$Failures,
        [System.Collections.Generic.List[object]]$BuildUpWarnings
    )

    $commentText = [string]$Comment.Range.Text
    $requested = [regex]::Matches($commentText, '\[\[MATH:(.*?)\]\]').Count
    $built = 0

    for ($index = 0; $index -lt $requested; $index++) {
        # Re-read the live comment range on every iteration. OMath conversion
        # changes Word story positions, so cached indexes are not reliable.
        $commentText = [string]$Comment.Range.Text
        $placeholderMatch = [regex]::Match($commentText, '\[\[MATH:(.*?)\]\]')
        if (-not $placeholderMatch.Success) {
            $Failures.Add([ordered]@{
                comment_id = $CommentId
                formula = ''
                message = "Only $built of $requested math placeholders remained addressable."
            })
            break
        }
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
            # Word keeps the replaced placeholder's old range length. Reset the
            # range on a fresh COM object so conversion cannot consume prose.
            Release-ComObject $mathRange
            $mathRange = $Comment.Range.Duplicate
            $mathRange.SetRange($start, $start + $mathText.Length)
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
        requested = $requested
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
$failures = New-Object 'System.Collections.Generic.List[object]'
$buildUpWarnings = New-Object 'System.Collections.Generic.List[object]'
$anchorRecords = New-Object 'System.Collections.Generic.List[object]'
$formulaRequested = 0
$formulaBuilt = 0
$word = $null
$document = $null
$oldUserName = $null
$oldInitials = $null
$passed = $false

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
    if ($document.Comments.Count -ne 0) {
        throw "Source document unexpectedly contains $($document.Comments.Count) comments."
    }

    foreach ($spec in ($specs | Sort-Object {[int]$_.paragraph_index})) {
        $paragraph = $null
        $paragraphRange = $null
        $anchorRange = $null
        $comment = $null
        $commentRange = $null
        try {
            $paragraphIndex = [int]$spec.paragraph_index
            if ($paragraphIndex -lt 1 -or $paragraphIndex -gt $document.Paragraphs.Count) {
                throw "Paragraph index $paragraphIndex is outside the document."
            }
            $paragraph = $document.Paragraphs.Item($paragraphIndex)
            $paragraphRange = $paragraph.Range
            $anchorRange = $paragraphRange.Duplicate
            if ($anchorRange.End -gt $anchorRange.Start) {
                $anchorRange.SetRange($anchorRange.Start, $anchorRange.End - 1)
            }
            $anchorText = ([string]$anchorRange.Text).Replace("`r", '').Replace("`a", '')
            if ([string]::IsNullOrWhiteSpace($anchorText)) {
                throw "Paragraph $paragraphIndex has an empty anchor."
            }

            $comment = $document.Comments.Add($anchorRange, ([string]$spec.text).Trim())
            $commentRange = $comment.Range
            $commentRange.Font.Name = '宋体'
            $commentRange.Font.NameFarEast = '宋体'
            $commentRange.Font.NameAscii = 'Times New Roman'
            $commentRange.Font.Size = 10.5

            $conversion = Convert-MathPlaceholders -Document $document -Comment $comment -CommentId ([string]$spec.id) -Failures $failures -BuildUpWarnings $buildUpWarnings
            $formulaRequested += [int]$conversion.requested
            $formulaBuilt += [int]$conversion.built
            $anchorRecords.Add([ordered]@{
                id = [string]$spec.id
                paragraph_index = $paragraphIndex
                anchor_text = $anchorText
                formula_count = [int]$conversion.built
            })
        }
        catch {
            $failures.Add([ordered]@{
                comment_id = [string]$spec.id
                formula = ''
                message = $_.Exception.Message
            })
        }
        finally {
            Release-ComObject $commentRange
            Release-ComObject $comment
            Release-ComObject $anchorRange
            Release-ComObject $paragraphRange
            Release-ComObject $paragraph
        }
    }

    $passed = (
        $failures.Count -eq 0 -and
        $anchorRecords.Count -eq $specs.Count -and
        $formulaRequested -eq $formulaBuilt -and
        $document.Comments.Count -eq $specs.Count
    )
    if ($passed) {
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
    comments_added = $anchorRecords.Count
    formulas_requested = $formulaRequested
    formulas_built = $formulaBuilt
    failures = @($failures | ForEach-Object { $_ })
    build_up_warnings = @($buildUpWarnings | ForEach-Object { $_ })
    anchors = @($anchorRecords | ForEach-Object { $_ })
    passed = $passed
}
$report | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $ReportPath -Encoding UTF8
$report | ConvertTo-Json -Depth 8

if (-not $passed) {
    exit 1
}
