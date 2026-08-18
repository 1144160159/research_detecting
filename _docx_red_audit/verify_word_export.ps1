param(
    [Parameter(Mandatory=$true)][string]$Source,
    [Parameter(Mandatory=$true)][string]$PdfOutput,
    [string]$ReportOutput = ''
)

$ErrorActionPreference = 'Stop'
$word = $null
$document = $null

try {
    $word = New-Object -ComObject Word.Application
    $word.Visible = $false
    $word.DisplayAlerts = 0
    $document = $word.Documents.Open($Source, $false, $true, $false)

    $pageCount = $document.ComputeStatistics(2)
    $report = [ordered]@{
        source = $Source
        pdf = $PdfOutput
        page_count = [int]$pageCount
        comment_count = [int]$document.Comments.Count
        inline_shape_count = [int]$document.InlineShapes.Count
        shape_count = [int]$document.Shapes.Count
        paragraph_count = [int]$document.Paragraphs.Count
        opened_read_only = [bool]$document.ReadOnly
    }

    $document.ExportAsFixedFormat(
        $PdfOutput,
        17,
        $false,
        0,
        0,
        1,
        $pageCount,
        0,
        $true,
        $true,
        1,
        $true,
        $true,
        $false
    )

    if ($ReportOutput) {
        $report | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath $ReportOutput -Encoding UTF8
    }
    $report | ConvertTo-Json -Depth 4
}
finally {
    if ($null -ne $document) {
        $document.Close($false)
        [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($document)
    }
    if ($null -ne $word) {
        $word.Quit()
        [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($word)
    }
    [GC]::Collect()
    [GC]::WaitForPendingFinalizers()
}
