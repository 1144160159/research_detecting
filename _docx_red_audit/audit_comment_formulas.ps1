param(
    [Parameter(Mandatory = $true)]
    [string]$InputPath,

    [Parameter(Mandatory = $true)]
    [string]$OutputPath
)

$ErrorActionPreference = 'Stop'

function Release-ComObject {
    param([object]$Object)
    if ($null -ne $Object) {
        [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($Object)
    }
}

$word = $null
$document = $null
$result = [ordered]@{
    input_path = $InputPath
    comments = @()
    body_formulas = @()
}

try {
    $word = New-Object -ComObject Word.Application
    $word.Visible = $false
    $word.DisplayAlerts = 0
    $document = $word.Documents.Open($InputPath, $false, $true)

    for ($commentIndex = 1; $commentIndex -le $document.Comments.Count; $commentIndex++) {
        $comment = $null
        $scope = $null
        $range = $null
        $maths = $null
        try {
            $comment = $document.Comments.Item($commentIndex)
            $scope = $comment.Scope
            $range = $comment.Range
            $maths = $range.OMaths
            $formulas = @()

            for ($formulaIndex = 1; $formulaIndex -le $maths.Count; $formulaIndex++) {
                $formula = $null
                $formulaRange = $null
                try {
                    $formula = $maths.Item($formulaIndex)
                    $formulaRange = $formula.Range
                    $formulas += [ordered]@{
                        index = $formulaIndex
                        text = ($formulaRange.Text -replace "[\r\a]", '')
                        start = $formulaRange.Start
                        end = $formulaRange.End
                        xml = $formulaRange.WordOpenXML
                    }
                }
                finally {
                    Release-ComObject $formulaRange
                    Release-ComObject $formula
                }
            }

            $result.comments += [ordered]@{
                index = $commentIndex
                author = $comment.Author
                initials = $comment.Initial
                anchor = ($scope.Text -replace "[\r\a]", '')
                text = ($range.Text -replace "[\r\a]", '')
                formula_count = $formulas.Count
                formulas = $formulas
            }
        }
        finally {
            Release-ComObject $maths
            Release-ComObject $range
            Release-ComObject $scope
            Release-ComObject $comment
        }
    }

    $bodyMaths = $document.OMaths
    try {
        for ($formulaIndex = 1; $formulaIndex -le $bodyMaths.Count; $formulaIndex++) {
            $formula = $null
            $formulaRange = $null
            try {
                $formula = $bodyMaths.Item($formulaIndex)
                $formulaRange = $formula.Range
                $result.body_formulas += [ordered]@{
                    index = $formulaIndex
                    text = ($formulaRange.Text -replace "[\r\a]", '')
                    start = $formulaRange.Start
                    end = $formulaRange.End
                    xml = $formulaRange.WordOpenXML
                }
            }
            finally {
                Release-ComObject $formulaRange
                Release-ComObject $formula
            }
        }
    }
    finally {
        Release-ComObject $bodyMaths
    }

    $commentFormulaCount = 0
    foreach ($item in $result.comments) {
        $commentFormulaCount += [int]$item['formula_count']
    }
    $result.comment_count = $document.Comments.Count
    $result.comment_formula_count = $commentFormulaCount
    $result.body_formula_count = $result.body_formulas.Count
    $result | ConvertTo-Json -Depth 12 | Set-Content -LiteralPath $OutputPath -Encoding UTF8
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
