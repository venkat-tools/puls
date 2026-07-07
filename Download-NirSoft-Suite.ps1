# Download-NirSoft-Suite.ps1
# Script to safely download and extract password-protected NirSoft utilities

param (
    [string]$action = "download"
)

$tempDir = Join-Path $env:TEMP "NirLauncher"
if (!(Test-Path $tempDir)) {
    New-Item -ItemType Directory -Path $tempDir -Force | Out-Null
}

if ($action -eq "download") {
    $url = "https://download.nirsoft.net/nirsoft_package_enc_1.30.24.zip"
    $zipFile = Join-Path $tempDir "nirsoft.zip"
    
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host "Downloading NirLauncher Package from: $url" -ForegroundColor Cyan
    Write-Host "============================================================" -ForegroundColor Cyan
    
    try {
        [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
        Invoke-WebRequest -Uri $url -OutFile $zipFile -UserAgent "Mozilla/5.0"
        Write-Host "Download complete. Extracting password-protected ZIP..." -ForegroundColor Green
        
        if (Test-Path "C:\Program Files\7-Zip\7z.exe") {
            & "C:\Program Files\7-Zip\7z.exe" x $zipFile -p"nirsoft9876$" -o"C:\NirLauncher" -y
            Write-Host "Successfully extracted to C:\NirLauncher" -ForegroundColor Green
        } else {
            Write-Host "7-Zip is required for password-protected ZIP extraction." -ForegroundColor Yellow
            Write-Host "Opening temporary folder. Extract with password: nirsoft9876$" -ForegroundColor Yellow
            Start-Process explorer.exe $tempDir
        }
    } catch {
        Write-Host "Error occurred during download/extraction: $_" -ForegroundColor Red
        exit 1
    }
}
elseif ($action -eq "mailpv") {
    $url = "https://www.nirsoft.net/toolsdownload/mailpv.zip"
    $zipFile = Join-Path $tempDir "mailpv.zip"
    $extractDir = "C:\NirLauncher\mailpv"
    
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host "Downloading MailPassView from: $url" -ForegroundColor Cyan
    Write-Host "============================================================" -ForegroundColor Cyan
    
    try {
        [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
        Invoke-WebRequest -Uri $url -OutFile $zipFile -UserAgent "Mozilla/5.0"
        Write-Host "Download complete. Extracting password-protected ZIP..." -ForegroundColor Green
        
        if (!(Test-Path $extractDir)) {
            New-Item -ItemType Directory -Path $extractDir -Force | Out-Null
        }
        
        if (Test-Path "C:\Program Files\7-Zip\7z.exe") {
            & "C:\Program Files\7-Zip\7z.exe" x $zipFile -p"nirsoft9876$" -o"$extractDir" -y
            Write-Host "Successfully extracted to C:\NirLauncher\mailpv" -ForegroundColor Green
            Write-Host "Launching MailPassView..." -ForegroundColor Green
            Start-Process "$extractDir\mailpv.exe"
        } else {
            Write-Host "7-Zip is required for password-protected ZIP extraction." -ForegroundColor Yellow
            Write-Host "Opening temporary folder. Extract with password: nirsoft9876$" -ForegroundColor Yellow
            Start-Process explorer.exe $tempDir
        }
    } catch {
        Write-Host "Error occurred during download/extraction: $_" -ForegroundColor Red
        exit 1
    }
}
