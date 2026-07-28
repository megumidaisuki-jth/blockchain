param(
    [Parameter(Mandatory=$true)][string]$DocumentPath,
    [Parameter(Mandatory=$true)][string]$OutputDirectory
)

$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

New-Item -ItemType Directory -Force -Path $OutputDirectory | Out-Null
$word = $null
$doc = $null
try {
    $word = New-Object -ComObject Word.Application
    $word.Visible = $false
    $word.DisplayAlerts = 0
    $word.AutomationSecurity = 3
    $word.Options.UpdateLinksAtOpen = $false
    $doc = $word.Documents.Open($DocumentPath, $false, $true)
    $pageCount = $doc.ComputeStatistics(2)
    for ($page = 1; $page -le $pageCount; $page++) {
        $start = $doc.GoTo(1, 1, $page).Start
        if ($page -lt $pageCount) {
            $end = $doc.GoTo(1, 1, $page + 1).Start - 1
        } else {
            $end = $doc.Content.End - 1
        }
        $range = $doc.Range($start, $end)
        $range.CopyAsPicture()
        Start-Sleep -Milliseconds 250
        $image = [System.Windows.Forms.Clipboard]::GetImage()
        if ($null -eq $image) {
            $dataObject = [System.Windows.Forms.Clipboard]::GetDataObject()
            $formats = $dataObject.GetFormats()
            if ($formats -contains 'EnhancedMetafile') {
                $image = $dataObject.GetData('EnhancedMetafile')
            }
            if ($null -eq $image -or -not ($image -is [System.Drawing.Image])) {
                Write-Output ("clipboard_formats=" + ($formats -join ','))
                if ($null -ne $image) { Write-Output ("enhanced_metafile_type=" + $image.GetType().FullName) }
                throw "Clipboard did not contain a usable image for page $page"
            }
        }
        $target = Join-Path $OutputDirectory ("page-{0:D2}.png" -f $page)
        $bitmap = New-Object System.Drawing.Bitmap $image
        $bitmap.Save($target, [System.Drawing.Imaging.ImageFormat]::Png)
        $bitmap.Dispose()
        $image.Dispose()
        [System.Windows.Forms.Clipboard]::Clear()
        [System.Runtime.InteropServices.Marshal]::FinalReleaseComObject($range) | Out-Null
    }
    Write-Output "pages=$pageCount"
} finally {
    if ($doc) {
        $doc.Close($false)
        [System.Runtime.InteropServices.Marshal]::FinalReleaseComObject($doc) | Out-Null
    }
    if ($word) {
        $word.Quit() | Out-Null
        [System.Runtime.InteropServices.Marshal]::FinalReleaseComObject($word) | Out-Null
    }
}
