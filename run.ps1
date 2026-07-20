# 1. Elevate to Administrator
if (-not ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole(544)) {
    Start-Process powershell "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`"" -Verb RunAs; exit
}

$dir = "C:\VenkatPulse"

# 2. Check if already installed for instant launch option
if (Test-Path "$dir\puls-main\main.exe") {
    Write-Host "Launching local cache instantly..." -ForegroundColor Green
    Stop-Process -Name main, PrintPulse -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 1
    cd "$dir\puls-main"
    Start-Process "main.exe" -WindowStyle Hidden
    Start-Sleep -Seconds 2
    Start-Process "http://localhost:3000"
    exit
}

# 3. Stop running instances to unlock files for updating
Write-Host "Stopping active instances of VenkatPulse..." -ForegroundColor Yellow
Stop-Process -Name main, PrintPulse -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 1

# 4. Setup Directory
if (Test-Path "$dir\puls-main") { Remove-Item "$dir\puls-main" -Recurse -Force -ErrorAction SilentlyContinue }
New-Item -ItemType Directory -Path $dir -Force | Out-Null

# 5. Download & Extract Suite
Write-Host "Downloading VenkatPulse AI Suite..." -ForegroundColor Green
Invoke-WebRequest "https://github.com/venkat-tools/puls/archive/refs/heads/main.zip" -OutFile "$dir\temp.zip" -UseBasicParsing
Expand-Archive "$dir\temp.zip" $dir -Force
Remove-Item "$dir\temp.zip" -Force

# 6. Unblock Files
cd "$dir\puls-main"
Get-ChildItem -Recurse | Unblock-File

# 7. Create Desktop Shortcut for one-click launches
try {
    $desktopPath = [System.IO.Path]::Combine([Environment]::GetFolderPath("Desktop"), "VenkatPulse AI.lnk")
    $WshShell = New-Object -ComObject WScript.Shell
    $Shortcut = $WshShell.CreateShortcut($desktopPath)
    $Shortcut.TargetPath = "$dir\puls-main\Start-Admin-Server.bat"
    $Shortcut.WorkingDirectory = "$dir\puls-main"
    $Shortcut.Description = "Launch VenkatPulse AI Suite"
    $Shortcut.IconLocation = "shell32.dll, 137" # Security shield icon
    $Shortcut.Save()
    Write-Host "Desktop Shortcut 'VenkatPulse AI' created successfully!" -ForegroundColor Green
} catch {
    Write-Host "Failed to create desktop shortcut: $_" -ForegroundColor Yellow
}

# 8. Run Server
Write-Host "Launching local socket server..." -ForegroundColor Cyan
Start-Process "main.exe" -WindowStyle Hidden
Start-Sleep -Seconds 2
Start-Process "http://localhost:3000"
