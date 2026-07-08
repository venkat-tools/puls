# 1. Check for Administrator privileges
$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "Requesting Administrator privileges to initialize VenkatPulse AI..." -ForegroundColor Cyan
    Start-Process powershell -ArgumentList "-NoProfile -ExecutionPolicy Bypass -Command `"& { $MyInvocation.ScriptName }`"" -Verb RunAs
    exit
}

# 2. Setup installation directory
$installDir = "C:\VenkatPulse"
if (-not (Test-Path $installDir)) {
    New-Item -ItemType Directory -Path $installDir -Force | Out-Null
}

Write-Host "==========================================================" -ForegroundColor Magenta
Write-Host "            Initializing VenkatPulse AI Suite            " -ForegroundColor Magenta
Write-Host "==========================================================" -ForegroundColor Magenta
Write-Host ""
Write-Host "Downloading packages from GitHub..." -ForegroundColor Green
$zipUrl = "https://github.com/venkat-tools/puls/archive/refs/heads/main.zip"
$zipPath = Join-Path $installDir "temp.zip"

# Download ZIP silently
Invoke-WebRequest -Uri $zipUrl -OutFile $zipPath -UseBasicParsing

Write-Host "Extracting application files..." -ForegroundColor Green
# Clean up old extraction directory if exists
$repoDir = Join-Path $installDir "puls-main"
if (Test-Path $repoDir) {
    Remove-Item -Path $repoDir -Recurse -Force
}
Expand-Archive -Path $zipPath -DestinationPath $installDir -Force
Remove-Item -Path $zipPath -Force

# 3. Unblock files & run server silently
if (Test-Path $repoDir) {
    Set-Location $repoDir
    
    Write-Host "Configuring Windows security policy (Unblocking files)..." -ForegroundColor Green
    # Unblock all files to bypass Smart App Control/SmartScreen blocks
    Get-ChildItem -Recurse | Unblock-File
    
    if (Test-Path "main.exe") {
        Write-Host "Launching local repair server socket..." -ForegroundColor Cyan
        Start-Process "main.exe" -WindowStyle Hidden
        Start-Sleep -Seconds 2
        Write-Host "Opening Web Dashboard..." -ForegroundColor Green
        Start-Process "http://localhost:3000"
    } else {
        Write-Host "main.exe not found. Trying to run via Python..." -ForegroundColor Yellow
        python server.py
    }
} else {
    Write-Host "[ERROR] Extraction failed or directory mismatch." -ForegroundColor Red
}
