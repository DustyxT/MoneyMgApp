$excel = New-Object -ComObject Excel.Application
$excel.Visible = $false
$excel.DisplayAlerts = $false
$workbookPath = "c:\Users\USER\Desktop\Money management app\Money-Money-101-Budget-Plan.xlsx"
$book = $excel.Workbooks.Open($workbookPath)

foreach ($sheet in $book.Worksheets) {
    $targetPath = "c:\Users\USER\Desktop\Money management app\" + $sheet.Name + ".csv"
    Write-Host "Saving $($sheet.Name) to $targetPath"
    $sheet.SaveAs($targetPath, 6) # 6 = xlCSV
}

$book.Close($false)
$excel.Quit()
[System.Runtime.Interopservices.Marshal]::ReleaseComObject($excel) | Out-Null
