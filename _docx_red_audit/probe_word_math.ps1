param(
    [Parameter(Mandatory = $true)]
    [string]$InputJson,

    [Parameter(Mandatory = $true)]
    [string]$OutputDocx,

    [Parameter(Mandatory = $true)]
    [string]$OutputPdf,

    [Parameter(Mandatory = $true)]
    [string]$OutputJson
)

$ErrorActionPreference = 'Stop'

function Release-ComObject {
    param([object]$Object)
    if ($null -ne $Object) {
        [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($Object)
    }
}

$parsedExpressions = Get-Content -LiteralPath $InputJson -Raw -Encoding UTF8 | ConvertFrom-Json
if ($parsedExpressions.PSObject.Properties.Name -contains 'expressions') {
    $expressions = @($parsedExpressions.expressions)
}
elseif ($parsedExpressions -is [System.Array]) {
    $expressions = @($parsedExpressions)
}
else {
    $expressions = @($parsedExpressions)
}

$word = $null
$document = $null
$results = @()

try {
    $word = New-Object -ComObject Word.Application
    $word.Visible = $false
    $word.DisplayAlerts = 0
    $document = $word.Documents.Add()

    for ($index = 0; $index -lt $expressions.Count; $index++) {
        $paragraph = $null
        $labelRange = $null
        $mathRange = $null
        $math = $null
        try {
            $paragraph = $document.Paragraphs.Add()
            $labelRange = $paragraph.Range
            $labelRange.Text = ('{0:D2}. ' -f ($index + 1)) + $expressions[$index]
            $mathStart = $labelRange.Start + 4
            $mathEnd = $labelRange.End - 1
            $mathRange = $document.Range($mathStart, $mathEnd)
            $mathRange.Font.Name = 'Cambria Math'
            $mathRange.Font.Size = 12
            [void]$document.OMaths.Add($mathRange)
            $math = $mathRange.OMaths.Item(1)
            $math.BuildUp()
            $results += [ordered]@{
                index = $index + 1
                source = $expressions[$index]
                built_text = ($math.Range.Text -replace "[\r\a]", '')
                xml = $math.Range.WordOpenXML
                error = $null
            }
        }
        catch {
            $message = $_.Exception.Message
            Write-Output ("PROBE_ERROR {0:D2}: {1}" -f ($index + 1), $message)
            $results += [ordered]@{
                index = $index + 1
                source = $expressions[$index]
                built_text = $null
                xml = $null
                error = $message
            }
        }
        finally {
            Release-ComObject $math
            Release-ComObject $mathRange
            Release-ComObject $labelRange
            Release-ComObject $paragraph
        }
    }

    $document.SaveAs2($OutputDocx, 16)
    $document.ExportAsFixedFormat($OutputPdf, 17)
    $results | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $OutputJson -Encoding UTF8
}
finally {
    if ($null -ne $document) {
        $document.Close($false)
    }
    if ($null -ne $word) {
        $word.Quit()
    }
    Release-ComObject $document
    Release-ComObject $word
    [GC]::Collect()
    [GC]::WaitForPendingFinalizers()
}
