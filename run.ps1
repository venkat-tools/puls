# 1. Elevate to Administrator
if (-not ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole(544)) {
    Start-Process powershell "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`"" -Verb RunAs; exit
}

$dir = "C:\VenkatPulse"

# 2. Stop running instances to unlock files for updating
Write-Host "Stopping active instances of Venkat Windows Tool Kit..." -ForegroundColor Yellow
Stop-Process -Name main, PrintPulse, VenkatPulse -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 1

# 3. Setup Directory & Clean Old Version
if (Test-Path "$dir\puls-main") { 
    Remove-Item "$dir\puls-main" -Recurse -Force -ErrorAction SilentlyContinue 
}
New-Item -ItemType Directory -Path $dir -Force | Out-Null

# 4. Download & Extract Suite
Write-Host "Downloading latest Venkat Windows Tool Kit..." -ForegroundColor Green
Invoke-WebRequest "https://github.com/venkat-tools/puls/archive/refs/heads/main.zip" -OutFile "$dir\temp.zip" -UseBasicParsing
Expand-Archive "$dir\temp.zip" $dir -Force
Remove-Item "$dir\temp.zip" -Force

# 5. Unblock Files
cd "$dir\puls-main"
Get-ChildItem -Recurse | Unblock-File

# 6. Create Desktop Shortcut for one-click launches
try {
    $desktopPath = [System.IO.Path]::Combine([Environment]::GetFolderPath("Desktop"), "Venkat Windows Tool Kit.lnk")
    $WshShell = New-Object -ComObject WScript.Shell
    $Shortcut = $WshShell.CreateShortcut($desktopPath)
    $Shortcut.TargetPath = "$dir\puls-main\Start-Admin-Server.bat"
    $Shortcut.WorkingDirectory = "$dir\puls-main"
    $Shortcut.Description = "Launch Venkat Windows Tool Kit"
    $Shortcut.IconLocation = "shell32.dll, 137" # Security shield icon
    $Shortcut.Save()
    Write-Host "Desktop Shortcut 'Venkat Windows Tool Kit' created successfully!" -ForegroundColor Green
} catch {
    Write-Host "Failed to create desktop shortcut: $_" -ForegroundColor Yellow
}

# 7. Run Server & Launch Dashboard
Write-Host "Launching Venkat Windows Tool Kit..." -ForegroundColor Cyan
Start-Process "main.exe" -WindowStyle Hidden
Start-Sleep -Seconds 2
Start-Process "http://localhost:3000"
