# Set maximum character limit (e.g., 500 or 1000)
$maxCharLimit = 1000

function New-RandomFile {
    param ([int]$Limit = 1000)

    # Generate a random 3-letter file extension
    $ext = -join ((97..122) | Get-Random -Count 3 | ForEach-Object { [char]$_ })
    $fileName = "$([System.IO.Path]::GetRandomFileName().Substring(0,8)).$ext"

    # Pick a random length from 1 up to the configured limit
    $contentLength = Get-Random -Minimum 1 -Maximum ($Limit + 1)

    # Generate random alphanumeric content
    $randomContent = -join ((48..57) + (65..90) + (97..122) | Get-Random -Count $contentLength | ForEach-Object { [char]$_ })

    # Write content to the file
    Set-Content -Path $fileName -Value $randomContent
    Write-Host "Created: $fileName ($contentLength chars)"
}

# Optional prompt to set character limit (press Enter for default 1000)
$limitInput = Read-Host "Enter max content length limit (e.g., 500 or 1000) [Default: 1000]"
if ($limitInput -and [int]::TryParse($limitInput, [ref]$null)) {
    $maxCharLimit = [int]$limitInput
}

do {
    $response = Read-Host "Create file? (Y = Yes / N = No / A = Auto)"

    if ($response -eq 'A' -or $response -eq 'a') {
        Write-Host "Auto-mode active (1 file/sec, max limit $maxCharLimit chars). Close window [X] or press Ctrl+C to stop." -ForegroundColor Yellow
        while ($true) {
            New-RandomFile -Limit $maxCharLimit
            Start-Sleep -Seconds 0.1
        }
    } elseif ($response -eq 'Y' -or $response -eq 'y') {
        New-RandomFile -Limit $maxCharLimit
    }
} while ($response -eq 'Y' -or $response -eq 'y')