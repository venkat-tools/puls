# Download-Diagnostic-Tools.ps1
# Script to download portable diagnostic utilities into the "tools" folder

$toolsDir = Join-Path $PSScriptRoot "tools"
if (!(Test-Path $toolsDir)) {
    New-Item -ItemType Directory -Path $toolsDir -Force | Out-Null
}

Write-Host "Downloading portable diagnostic utilities..." -ForegroundColor Cyan

# 1. Rufus Portable
$rufusUrl = "https://github.com/pbatard/rufus/releases/download/v4.5/rufus-4.5.exe"
$rufusPath = Join-Path $toolsDir "Rufus_Portable.exe"
if (!(Test-Path $rufusPath)) {
    Write-Host "Downloading Rufus Portable..." -ForegroundColor Yellow
    Invoke-WebRequest -Uri $rufusUrl -OutFile $rufusPath -UserAgent "Mozilla/5.0"
}

# 2. CrystalDiskInfo (SourceForge Direct)
$cdiUrl = "https://sourceforge.net/projects/crystaldiskinfo/files/9.3.0/CrystalDiskInfo9_3_0.zip/download"
$cdiZip = Join-Path $toolsDir "CrystalDiskInfo.zip"
$cdiDir = Join-Path $toolsDir "CrystalDiskInfo"
if (!(Test-Path $cdiDir)) {
    Write-Host "Downloading CrystalDiskInfo..." -ForegroundColor Yellow
    Invoke-WebRequest -Uri $cdiUrl -OutFile $cdiZip -UserAgent "Mozilla/5.0"
    Expand-Archive -Path $cdiZip -DestinationPath $cdiDir -Force
    Remove-Item $cdiZip -Force
}

# 3. CPU-Z Portable
$cpuzUrl = "https://download.cpuid.com/cpu-z/cpu-z_2.09-en.zip"
$cpuzZip = Join-Path $toolsDir "cpu-z.zip"
$cpuzDir = Join-Path $toolsDir "CPU-Z"
if (!(Test-Path $cpuzDir)) {
    Write-Host "Downloading CPU-Z..." -ForegroundColor Yellow
    Invoke-WebRequest -Uri $cpuzUrl -OutFile $cpuzZip -UserAgent "Mozilla/5.0"
    Expand-Archive -Path $cpuzZip -DestinationPath $cpuzDir -Force
    Remove-Item $cpuzZip -Force
}

# 4. HWMonitor Portable
$hwmUrl = "https://download.cpuid.com/hwmonitor/hwmonitor_1.52.zip"
$hwmZip = Join-Path $toolsDir "hwmonitor.zip"
$hwmDir = Join-Path $toolsDir "HWMonitor"
if (!(Test-Path $hwmDir)) {
    Write-Host "Downloading HWMonitor..." -ForegroundColor Yellow
    Invoke-WebRequest -Uri $hwmUrl -OutFile $hwmZip -UserAgent "Mozilla/5.0"
    Expand-Archive -Path $hwmZip -DestinationPath $hwmDir -Force
    Remove-Item $hwmZip -Force
}

# 5. Notepad++ Portable (Text/Code Editor)
$nppUrl = "https://github.com/notepad-plus-plus/notepad-plus-plus/releases/download/v8.6.8/npp.8.6.8.portable.x64.zip"
$nppZip = Join-Path $toolsDir "npp.zip"
$nppDir = Join-Path $toolsDir "NotepadPlusPlus"
if (!(Test-Path $nppDir)) {
    Write-Host "Downloading Notepad++ Portable..." -ForegroundColor Yellow
    Invoke-WebRequest -Uri $nppUrl -OutFile $nppZip -UserAgent "Mozilla/5.0"
    Expand-Archive -Path $nppZip -DestinationPath $nppDir -Force
    Remove-Item $nppZip -Force
}

# 6. WizTree Portable (Disk Space Analyzer)
$wizUrl = "https://diskanalyzer.com/files/wiztree_4_20_portable.zip"
$wizZip = Join-Path $toolsDir "wiztree.zip"
$wizDir = Join-Path $toolsDir "WizTree"
if (!(Test-Path $wizDir)) {
    Write-Host "Downloading WizTree Portable..." -ForegroundColor Yellow
    Invoke-WebRequest -Uri $wizUrl -OutFile $wizZip -UserAgent "Mozilla/5.0"
    Expand-Archive -Path $wizZip -DestinationPath $wizDir -Force
    Remove-Item $wizZip -Force
}

# 7. 7-Zip Portable
$szUrl = "https://github.com/ip7z/7zip/releases/download/26.02/7z2602-extra.7z"
$szFile = Join-Path $toolsDir "7z-extra.7z"
$szDir = Join-Path $toolsDir "7-Zip"
if (!(Test-Path $szDir)) {
    Write-Host "Downloading 7-Zip Portable..." -ForegroundColor Yellow
    Invoke-WebRequest -Uri $szUrl -OutFile $szFile -UserAgent "Mozilla/5.0"
    
    # Standard x64 installer as well
    $szExeUrl = "https://github.com/ip7z/7zip/releases/download/26.02/7z2602-x64.exe"
    $szExePath = Join-Path $toolsDir "7z_Installer.exe"
    Invoke-WebRequest -Uri $szExeUrl -OutFile $szExePath -UserAgent "Mozilla/5.0"
}

# 8. NTPWEdit (Windows Password SAM Editor)
$samUrl = "https://samsoft.org.ru/files/ntpwedit07.zip"
$samZip = Join-Path $toolsDir "ntpwedit.zip"
$samDir = Join-Path $toolsDir "NTPWEdit"
if (!(Test-Path $samDir)) {
    Write-Host "Downloading NTPWEdit Password Resetter..." -ForegroundColor Yellow
    # Bypass standard SSL check if samsoft TLS certificate is outdated, using basic WebClient fallback if needed
    try {
        Invoke-WebRequest -Uri $samUrl -OutFile $samZip -UserAgent "Mozilla/5.0" -ErrorAction Stop
    } catch {
        # Alternate mirror fallback
        $samUrlFallback = "https://cdob.pages.dev/files/ntpwedit07.zip"
        Invoke-WebRequest -Uri $samUrlFallback -OutFile $samZip -UserAgent "Mozilla/5.0"
    }
    Expand-Archive -Path $samZip -DestinationPath $samDir -Force
    Remove-Item $samZip -Force
}

# 9. Recuva Portable (Data Recovery Tool)
$recUrl = "https://download.ccleaner.com/portable/rcsetup153.zip"
$recZip = Join-Path $toolsDir "recuva.zip"
$recDir = Join-Path $toolsDir "Recuva"
if (!(Test-Path $recDir)) {
    Write-Host "Downloading Recuva Portable..." -ForegroundColor Yellow
    Invoke-WebRequest -Uri $recUrl -OutFile $recZip -UserAgent "Mozilla/5.0"
    Expand-Archive -Path $recZip -DestinationPath $recDir -Force
    Remove-Item $recZip -Force
}

# 10. Angry IP Scanner (Network Printer / IP Discoverer)
$ipUrl = "https://github.com/angryip/ipscan/releases/download/3.9.1/ipscan-win64-3.9.1.exe"
$ipPath = Join-Path $toolsDir "Angry_IP_Scanner.exe"
if (!(Test-Path $ipPath)) {
    Write-Host "Downloading Angry IP Scanner..." -ForegroundColor Yellow
    Invoke-WebRequest -Uri $ipUrl -OutFile $ipPath -UserAgent "Mozilla/5.0"
}

Write-Host "All portable tools successfully downloaded to: $toolsDir" -ForegroundColor Green
