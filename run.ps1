# 1. Elevate to Administrator
if (-not ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole(544)) {
    Start-Process powershell "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`"" -Verb RunAs; exit
}

# 2. Setup Directory
$dir = "C:\VenkatPulse"
if (Test-Path "$dir\puls-main") { Remove-Item "$dir\puls-main" -Recurse -Force -ErrorAction SilentlyContinue }
New-Item -ItemType Directory -Path $dir -Force | Out-Null

# 3. Download & Extract Suite
Write-Host "Downloading VenkatPulse AI Suite..." -ForegroundColor Green
Invoke-WebRequest "https://github.com/venkat-tools/puls/archive/refs/heads/main.zip" -OutFile "$dir\temp.zip" -UseBasicParsing
Expand-Archive "$dir\temp.zip" $dir -Force
Remove-Item "$dir\temp.zip" -Force

# 4. Unblock Files & Run Server
cd "$dir\puls-main"
Get-ChildItem -Recurse | Unblock-File
Write-Host "Launching local socket server..." -ForegroundColor Cyan
Start-Process "main.exe" -WindowStyle Hidden
Start-Sleep -Seconds 2
Start-Process "http://localhost:3000"
