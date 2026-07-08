# Build-WinPE-ISO.ps1
# Run this script as Administrator in PowerShell to build a custom PrintPulse WinPE ISO

# 1. Check if running as Admin (Self-elevate if not)
$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (!$isAdmin) {
    Start-Process powershell -ArgumentList "-NoExit -ExecutionPolicy Bypass -File `"$PSCommandPath`"" -Verb RunAs
    Exit
}

# 2. Detect oscdimg.exe (from Windows ADK)
Write-Host "Detecting Windows ADK Deployment Tools (oscdimg.exe)..." -ForegroundColor Cyan
$oscdimg = "C:\Program Files (x86)\Windows Kits\10\Assessment and Deployment Kit\Deployment Tools\amd64\Oscdimg\oscdimg.exe"
if (!(Test-Path $oscdimg)) {
    # Search in standard Windows Kits path
    $oscdimg = (Get-ChildItem -Path "C:\Program Files (x86)\Windows Kits" -Filter "oscdimg.exe" -Recurse -ErrorAction SilentlyContinue | Select-Object -First 1).FullName
}

if (!$oscdimg) {
    Write-Host ""
    Write-Host "[ERROR] oscdimg.exe not found on this system!" -ForegroundColor Red
    Write-Host "Creating a bootable ISO requires the Windows ADK Deployment Tools." -ForegroundColor Yellow
    Write-Host "Please download and install 'Deployment Tools' from: " -ForegroundColor Yellow
    Write-Host "https://learn.microsoft.com/en-us/windows-hardware/get-started/adk-install" -ForegroundColor Blue
    Write-Host ""
    Exit
}
Write-Host "Found ADK compiler at: $oscdimg" -ForegroundColor Green

# 3. Create temp structure
$tempDir = "C:\VenkatPulse_ISO_Temp"
if (Test-Path $tempDir) { 
    Write-Host "Cleaning up old temp directory..."
    Remove-Item -Path $tempDir -Recurse -Force -ErrorAction SilentlyContinue
}
New-Item -ItemType Directory -Path "$tempDir\media\sources" -Force | Out-Null
New-Item -ItemType Directory -Path "$tempDir\media\VenkatPulse" -Force | Out-Null

# 4. Copy Bootloader Files first (so they don't overwrite boot.wim later)
Write-Host "Copying boot loader files from Windows ADK PE templates..." -ForegroundColor Cyan
$copiedBootloader = $false

# Standard ADK Windows PE media path
$adkMediaDir = "C:\Program Files (x86)\Windows Kits\10\Assessment and Deployment Kit\Windows Preinstallation Environment\amd64\Media"
if (!(Test-Path $adkMediaDir)) {
    # Search for Media folder in Windows Kits
    $adkMediaDir = (Get-ChildItem -Path "C:\Program Files (x86)\Windows Kits" -Filter "Media" -Recurse -ErrorAction SilentlyContinue | Where-Object { $_.FullName -like "*Windows Preinstallation Environment\amd64\Media" } | Select-Object -First 1).FullName
}

if ($adkMediaDir -and (Test-Path $adkMediaDir)) {
    Write-Host "Found ADK Windows PE Media templates at: $adkMediaDir" -ForegroundColor Green
    Copy-Item "$adkMediaDir\*" "$tempDir\media" -Recurse -Force
    $copiedBootloader = $true
}

# Ensure boot directories exist
if (!(Test-Path "$tempDir\media\boot")) { New-Item -ItemType Directory -Path "$tempDir\media\boot" -Force | Out-Null }
if (!(Test-Path "$tempDir\media\EFI\Microsoft\Boot")) { New-Item -ItemType Directory -Path "$tempDir\media\EFI\Microsoft\Boot" -Force | Out-Null }

# Locate and copy etfsboot.com and efisys.bin (required for ISO boot sector)
Write-Host "Locating boot sector files (etfsboot.com / efisys.bin)..." -ForegroundColor Cyan
$etfsboot = (Get-ChildItem -Path "C:\Program Files (x86)\Windows Kits" -Filter "etfsboot.com" -Recurse -ErrorAction SilentlyContinue | Select-Object -First 1).FullName
$efisys = (Get-ChildItem -Path "C:\Program Files (x86)\Windows Kits" -Filter "efisys.bin" -Recurse -ErrorAction SilentlyContinue | Select-Object -First 1).FullName

if ($etfsboot) { 
    Copy-Item $etfsboot "$tempDir\media\boot\etfsboot.com" -Force 
    Write-Host "Found and copied etfsboot.com" -ForegroundColor Green
}
if ($efisys) { 
    Copy-Item $efisys "$tempDir\media\EFI\Microsoft\Boot\efisys.bin" -Force 
    Write-Host "Found and copied efisys.bin" -ForegroundColor Green
}

# If the ADK media dir wasn't found, try to copy default fallback files from local Windows
if (!$copiedBootloader) {
    Write-Warning "Standard ADK Media folder not found. Fetching system boot files from C:\Windows\Boot..."
    
    # Ensure boot folders exist
    New-Item -ItemType Directory -Path "$tempDir\media\boot" -Force | Out-Null
    New-Item -ItemType Directory -Path "$tempDir\media\sources" -Force | Out-Null
    New-Item -ItemType Directory -Path "$tempDir\media\EFI\Boot" -Force | Out-Null
    New-Item -ItemType Directory -Path "$tempDir\media\EFI\Microsoft\Boot" -Force | Out-Null
    
    # Copy boot managers
    Copy-Item "C:\Windows\Boot\EFI\bootmgfw.efi" "$tempDir\media\bootmgr.efi" -Force -ErrorAction SilentlyContinue
    Copy-Item "C:\Windows\Boot\PCAT\bootmgr" "$tempDir\media\bootmgr" -Force -ErrorAction SilentlyContinue
    Copy-Item "C:\Windows\Boot\EFI\bootmgfw.efi" "$tempDir\media\EFI\Boot\bootx64.efi" -Force -ErrorAction SilentlyContinue
    Copy-Item "C:\Windows\Boot\EFI\bootmgfw.efi" "$tempDir\media\EFI\Microsoft\Boot\bootmgfw.efi" -Force -ErrorAction SilentlyContinue
    
    # Copy boot.sdi
    if (Test-Path "C:\Windows\Boot\DVD\EFI\boot.sdi") {
        Copy-Item "C:\Windows\Boot\DVD\EFI\boot.sdi" "$tempDir\media\boot\boot.sdi" -Force
    } else {
        $bootSdi = (Get-ChildItem -Path "C:\Windows\Boot" -Filter "boot.sdi" -Recurse -ErrorAction SilentlyContinue | Select-Object -First 1).FullName
        if ($bootSdi) { Copy-Item $bootSdi "$tempDir\media\boot\boot.sdi" -Force }
    }
}

# 4b. Ensure a valid BCD boot Configuration Data store exists
if (!(Test-Path "$tempDir\media\EFI\Microsoft\Boot\BCD")) {
    Write-Host "Creating fresh BCD store programmatically..." -ForegroundColor Cyan
    
    # Ensure folder structure exists
    New-Item -ItemType Directory -Path "$tempDir\media\EFI\Microsoft\Boot" -Force | Out-Null
    
    $bcdPath = "$tempDir\media\EFI\Microsoft\Boot\BCD"
    if (Test-Path $bcdPath) { Remove-Item $bcdPath -Force }
    
    # Create the store using bcdedit.exe
    & bcdedit.exe /createstore $bcdPath
    & bcdedit.exe /store $bcdPath /create '{bootmgr}' /d "Windows Boot Manager"
    & bcdedit.exe /store $bcdPath /set '{bootmgr}' device boot
    & bcdedit.exe /store $bcdPath /create '{76127c59-ac0e-44a3-9543-25a12d0865c0}' /d "Ramdisk Options" /device
    & bcdedit.exe /store $bcdPath /set '{76127c59-ac0e-44a3-9543-25a12d0865c0}' ramdisksdidevice boot
    & bcdedit.exe /store $bcdPath /set '{76127c59-ac0e-44a3-9543-25a12d0865c0}' ramdisksdipath "\boot\boot.sdi"
    
    # Create the OS loader entry and parse its GUID
    $createOutput = & bcdedit.exe /store $bcdPath /create /d "Windows PE" /application osloader
    $guid = ($createOutput | Select-String -Pattern '{[a-f0-9-]{36}}').Matches.Value
    
    # Configure the OS loader entry
    & bcdedit.exe /store $bcdPath /set $guid device "ramdisk=[boot]\sources\boot.wim,{76127c59-ac0e-44a3-9543-25a12d0865c0}"
    & bcdedit.exe /store $bcdPath /set $guid osdevice "ramdisk=[boot]\sources\boot.wim,{76127c59-ac0e-44a3-9543-25a12d0865c0}"
    & bcdedit.exe /store $bcdPath /set $guid path "\windows\system32\boot\winload.efi"
    & bcdedit.exe /store $bcdPath /set $guid systemroot "\windows"
    & bcdedit.exe /store $bcdPath /set $guid detecthal Yes
    & bcdedit.exe /store $bcdPath /set $guid winpe Yes
    & bcdedit.exe /store $bcdPath /displayorder $guid /addfirst
}

# Double check critical boot files exist
if (!(Test-Path "$tempDir\media\boot\etfsboot.com") -or !(Test-Path "$tempDir\media\EFI\Microsoft\Boot\efisys.bin")) {
    Write-Error "Could not locate boot sector files (etfsboot.com / efisys.bin) required for bootable media creation."
    Exit
}

# 5. Extract/Locate WIM file (winre.wim or winpe.wim) and copy as boot.wim
Write-Host "Extracting/Locating base WIM file..." -ForegroundColor Cyan
$baseWimCopied = $false

# Try local WinRE.wim first
reagentc /disable | Out-Null
$winrePath = "C:\Windows\System32\Recovery\winre.wim"
if (Test-Path $winrePath) {
    Copy-Item $winrePath "$tempDir\media\sources\boot.wim" -Force
    reagentc /enable | Out-Null
    Write-Host "Local recovery image (WinRE) successfully extracted and copied." -ForegroundColor Green
    $baseWimCopied = $true
} else {
    reagentc /enable | Out-Null
    Write-Host "[INFO] Local WinRE.wim could not be extracted (Windows Recovery might be disabled/missing)." -ForegroundColor Yellow
    Write-Host "Searching for Windows ADK Windows PE add-on (winpe.wim)..." -ForegroundColor Cyan
    
    # Standard ADK WinPE path
    $adkPEPath = "C:\Program Files (x86)\Windows Kits\10\Assessment and Deployment Kit\Windows Preinstallation Environment\amd64\en-us\winpe.wim"
    if (!(Test-Path $adkPEPath)) {
        # Search for any winpe.wim in Windows Kits directory
        $adkPEPath = (Get-ChildItem -Path "C:\Program Files (x86)\Windows Kits" -Filter "winpe.wim" -Recurse -ErrorAction SilentlyContinue | Select-Object -First 1).FullName
    }
    
    if ($adkPEPath -and (Test-Path $adkPEPath)) {
        Write-Host "Found ADK Windows PE base image at: $adkPEPath" -ForegroundColor Green
        Copy-Item $adkPEPath "$tempDir\media\sources\boot.wim" -Force
        $baseWimCopied = $true
    }
}

if (!$baseWimCopied) {
    Write-Host ""
    Write-Host "[ERROR] Could not locate any base WIM file (winre.wim or winpe.wim)!" -ForegroundColor Red
    Write-Host "Ensure the Windows PE add-on is installed from the Microsoft ADK page." -ForegroundColor Yellow
    Exit
}

# 5b. Modify boot.wim startnet.cmd to auto-launch VenkatPulse
Write-Host "Cleaning up any stale DISM mount points..." -ForegroundColor Cyan
& dism.exe /Cleanup-Mountpoints | Out-Null

Write-Host "Mounting boot.wim to edit startnet.cmd..." -ForegroundColor Cyan
$mountDir = "$tempDir\mount"
if (Test-Path $mountDir) {
    Remove-Item -Path $mountDir -Recurse -Force -ErrorAction SilentlyContinue
}
New-Item -ItemType Directory -Path $mountDir -Force | Out-Null

$mountCmd = "dism.exe /Mount-Image /ImageFile:`"$tempDir\media\sources\boot.wim`" /Index:1 /MountDir:`"$mountDir`""
Write-Host "Running: $mountCmd"
& cmd.exe /c $mountCmd

$startnetPath = "$mountDir\Windows\System32\startnet.cmd"
if (Test-Path $startnetPath) {
    Write-Host "Updating startnet.cmd to auto-launch VenkatPulse on boot..." -ForegroundColor Green
    $startnetContent = @"
wpeinit
@echo off
echo ========================================================
echo   Venkat Pulse AI OS Recovery Suite - Auto-Launch
echo ========================================================
echo.
echo Searching for VenkatPulse.exe on external drives...
for %%d in (C D E F G H I J K L M N O P Q R S T U V W X Y Z) do (
    if exist %%d:\VenkatPulse\VenkatPulse.exe (
        echo Found VenkatPulse on drive %%d:
        cd /d %%d:\VenkatPulse
        VenkatPulse.exe
        echo.
        echo VenkatPulse exited. Error Level: %%errorlevel%%
        pause
        exit
    )
)
echo WARNING: VenkatPulse.exe was not found on any external drive!
echo You can run it manually if you know its location.
cmd.exe

"@
    Set-Content -Path $startnetPath -Value $startnetContent -Force
} else {
    Write-Warning "Could not find startnet.cmd inside boot.wim!"
}

Write-Host "Unmounting boot.wim and committing changes..." -ForegroundColor Cyan
$unmountCmd = "dism.exe /Unmount-Image /MountDir:`"$mountDir`" /Commit"
Write-Host "Running: $unmountCmd"
& cmd.exe /c $unmountCmd

Remove-Item -Path $mountDir -Recurse -Force -ErrorAction SilentlyContinue

# 6. Copy VenkatPulse files
Write-Host "Copying VenkatPulse program files..." -ForegroundColor Cyan
$currentDir = Get-Location
Copy-Item "$currentDir\*" "$tempDir\media\VenkatPulse" -Recurse -Exclude "dist","build",".git","*.iso","*.old","*.old_*","*.spec" -Force

# 7. Generate bootable ISO using oscdimg
Write-Host "Compiling bootable WinPE ISO image (UEFI & BIOS Dual Mode)..." -ForegroundColor Cyan
$isoPath = Join-Path $currentDir "VenkatPulse_WinPE.iso"

# oscdimg arguments for BIOS & UEFI dual boot layout
$args = '-m -o -u2 -udfver102 -bootdata:2#p0,e,b"'+$tempDir+'\media\boot\etfsboot.com"#pEF,e,b"'+$tempDir+'\media\EFI\Microsoft\Boot\efisys.bin"' + " `"$tempDir\media`" `"$isoPath`""

Start-Process -FilePath $oscdimg -ArgumentList $args -Wait -NoNewWindow

if (Test-Path $isoPath) {
    Write-Host ""
    Write-Host "==========================================================" -ForegroundColor Green
    Write-Host "SUCCESS! VenkatPulse custom WinPE ISO created successfully!" -ForegroundColor Green
    Write-Host "ISO Path: $isoPath" -ForegroundColor Green
    Write-Host "==========================================================" -ForegroundColor Green
    Write-Host ""
} else {
    Write-Error "Failed to compile the ISO image. Please check logs above."
}

# Cleanup
Write-Host "Cleaning up temporary files..."
Remove-Item -Path $tempDir -Recurse -Force -ErrorAction SilentlyContinue
