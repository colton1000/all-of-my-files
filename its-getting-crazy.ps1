function New-RandomTxtFile {
    $fileName = "$([System.IO.Path]::GetRandomFileName()).txt"
    $randomContent = -join ((48..57) + (65..90) + (97..122) | Get-Random -Count 99999 | ForEach-Object { [char]$_ })
    Set-Content -Path $fileName -Value $randomContent
    Write-Host "Created: $fileName"
}

do {
    $response = Read-Host "Create file? (Y = Yes / N = No / A = Auto)"

    if ($response -eq 'A' -or $response -eq 'a') {
        Write-Host "Auto-mode active (1 file/sec). Close window [X] or press Ctrl+C to stop." -ForegroundColor Yellow
        while ($true) {
            New-RandomTxtFile
            Start-Sleep -Seconds 1
        }
    } elseif ($response -eq 'Y' -or $response -eq 'y') {
        New-RandomTxtFile
    }
} while ($response -eq 'Y' -or $response -eq 'y')