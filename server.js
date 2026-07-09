const http = require('http');
const fs = require('fs');
const path = require('path');
const os = require('os');
const { exec, execSync, execFile } = require('child_process');

// Query OS Caption once at startup
let osName = 'Windows OS';
try {
  osName = execSync('powershell -Command "(Get-CimInstance Win32_OperatingSystem).Caption"', { encoding: 'utf8' }).trim();
} catch (e) {
  try {
    const raw = execSync('wmic os get Caption /value', { encoding: 'utf8' });
    const match = raw.match(/Caption=(.*)/);
    if (match && match[1]) osName = match[1].trim();
  } catch (err) {
    osName = `Windows (${os.release()})`;
  }
}

// Self-elevation check for Windows Administrator rights
try {
  execSync('net session', { stdio: 'ignore' });
} catch (e) {
  console.log('[Security] Server is not running as Admin. Attempting auto-elevation...');
  const scriptPath = path.resolve(__filename);
  const psCommand = `Start-Process node -ArgumentList '"${scriptPath}"' -Verb RunAs`;
  try {
    execSync(`powershell -Command "${psCommand}"`);
    process.exit(0); // Exit the current non-admin instance
  } catch (err) {
    console.warn('[Security] UAC prompt declined or failed. Running in read-only mode.');
  }
}

const PORT = 3000;
const PUBLIC_DIR = __dirname;

const COMMANDS = {
  quick_repair: `powershell -Command "Stop-Service -Name Spooler -Force; Remove-Item -Path 'C:\\Windows\\System32\\spool\\PRINTERS\\*' -Force -Recurse; Start-Service -Name Spooler"`,
  clear_queue: `powershell -Command "Stop-Service -Name Spooler -Force; Remove-Item -Path 'C:\\Windows\\System32\\spool\\PRINTERS\\*' -Force -Recurse; Start-Service -Name Spooler"`,
  restart_spooler: `powershell -Command "Restart-Service -Name Spooler -Force"`,
  devices_printers: `start control printers`,
  print_management: `start printmanagement.msc`,
  sharing_center: `start control.exe /name Microsoft.NetworkAndSharingCenter`,
  point_print_fix: `reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows NT\\Printers\\PointAndPrint" /v RestrictDriverInstallationToAdministrators /t REG_DWORD /d 0 /f && powershell -Command "Restart-Service -Name Spooler -Force"`,
  rpc_fixes: `reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows NT\\Printers\\RPC" /v RpcOverNamedPipes /t REG_DWORD /d 1 /f && reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows NT\\Printers\\RPC" /v RpcUseNamedPipeShare /t REG_DWORD /d 1 /f && reg add "HKLM\\System\\CurrentControlSet\\Control\\Print" /v RpcAuthnLevelPrivacyEnabled /t REG_DWORD /d 0 /f && powershell -Command "Restart-Service -Name Spooler -Force"`,
  network_discovery: `netsh advfirewall firewall set rule group="Network Discovery" new enable=Yes`,
  enable_smb1: `start powershell -NoExit -Command "Enable-WindowsOptionalFeature -Online -FeatureName 'SMB1Protocol' -All -NoRestart"`,
  disable_smb1: `start powershell -NoExit -Command "Disable-WindowsOptionalFeature -Online -FeatureName 'SMB1Protocol' -Force -NoRestart"`,
  enable_lpd: `start powershell -NoExit -Command "Write-Host 'Enabling LPD Print Service and LPR Port Monitor...'; Enable-WindowsOptionalFeature -Online -FeatureName 'LPDPrintService' -All -NoRestart; Enable-WindowsOptionalFeature -Online -FeatureName 'LPRPortMonitor' -All -NoRestart; Write-Host 'LPD and LPR Port features enabled!'"`,

  // Windows Repairs
  sfc_scan: `start cmd /k sfc /scannow`,
  dism_restore: `start cmd /k dism /online /cleanup-image /restorehealth`,
  reset_wua: `start powershell -NoExit -Command "Stop-Service -Name wuauserv,bits,cryptsvc -Force; Remove-Item -Path C:\\Windows\\SoftwareDistribution\\* -Recurse -Force; Start-Service -Name wuauserv,bits,cryptsvc"`,
  flush_dns: `ipconfig /flushdns`,
  reset_winsock: `netsh winsock reset`,
  reset_firewall: `netsh advfirewall reset`,

  // Windows Debloater
  create_restore_point: `start powershell -NoExit -Command "Enable-ComputerRestore -Drive C:; Checkpoint-Computer -Description 'WinPulseBeforeRepair' -RestorePointType MODIFY_SETTINGS"`,
  disable_telemetry: `reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\DataCollection" /v AllowTelemetry /t REG_DWORD /d 0 /f && powershell -Command "Stop-Service -Name DiagTrack -Force; Set-Service -Name DiagTrack -StartupType Disabled"`,
  disable_cortana: `reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\Windows Search" /v AllowCortana /t REG_DWORD /d 0 /f`,
  disable_onedrive: `reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\OneDrive" /v DisableFileSyncNGSC /t REG_DWORD /d 1 /f && taskkill /F /IM OneDrive.exe`,
  disable_xbox: `powershell -Command "Stop-Service -Name XblAuthManager,XblGameSave,XboxNetApiSvc -Force; Set-Service -Name XblAuthManager -StartupType Disabled; Set-Service -Name XblGameSave -StartupType Disabled; Set-Service -Name XboxNetApiSvc -StartupType Disabled"`,
  uninstall_bloatware: `start powershell -NoExit -Command "@('*XboxApp*', '*ZuneMusic*', '*BingNews*', '*Office.OneNote*', '*SolitaireCollection*') | ForEach-Object { Get-AppxPackage -AllUsers $_ | Remove-AppxPackage -ErrorAction SilentlyContinue }"`,
  ultimate_performance: `powercfg -duplicatescheme e9a42b02-d5df-448d-aa00-03f14749eb61 && powercfg -setactive e9a42b02-d5df-448d-aa00-03f14749eb61`,
  disable_bing_search: `reg add "HKCU\\Software\\Policies\\Microsoft\\Windows\\Explorer" /v DisableSearchBoxSuggestions /t REG_DWORD /d 1 /f && reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Search" /v BingSearchEnabled /t REG_DWORD /d 0 /f`,
  optimize_visual_effects: `reg add "HKCU\\Control Panel\\Desktop" /v MenuShowDelay /t REG_SZ /d 0 /f && reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\VisualEffects" /v VisualFXSetting /t REG_DWORD /d 2 /f`,
  deep_temp_clean: `start cmd /k powershell -NoExit -Command "Write-Host 'Cleaning Temporary folders...'; Remove-Item -Path $env:TEMP\\* -Recurse -Force -ErrorAction SilentlyContinue; Remove-Item -Path 'C:\\Windows\\Temp\\*' -Recurse -Force -ErrorAction SilentlyContinue; Remove-Item -Path 'C:\\Windows\\Prefetch\\*' -Recurse -Force -ErrorAction SilentlyContinue; Write-Host 'Temporary folders cleared successfully!'"`,
  reset_update_cache: `start cmd /k powershell -NoExit -Command "Write-Host 'Stopping Windows Update services...'; Stop-Service -Name wuauserv, bits, cryptsvc -Force; Write-Host 'Clearing cache...'; Remove-Item -Path 'C:\\Windows\\SoftwareDistribution\\*' -Recurse -Force -ErrorAction SilentlyContinue; Write-Host 'Restarting services...'; Start-Service -Name wuauserv, bits, cryptsvc; Write-Host 'Windows Update Cache reset successfully!'"`,
  network_reset_dns: `start cmd /k "ipconfig /release && ipconfig /renew && ipconfig /flushdns && netsh winsock reset && netsh int ip reset"`,

  // Administrative Shortcuts (User Tools)
  lusrmgr: `start lusrmgr.msc`,
  uac_settings: `start useraccountcontrolsettings.exe`,
  sys_properties: `start sysdm.cpl`,
  comp_mgmt: `start compmgmt.msc`,
  gp_editor: `start gpedit.msc`,
  reg_editor: `start regedit.exe`,

  // Driver & Hardware Management Tools
  driver_scan: `pnputil /scan-devices`,
  driver_upgrade: `start powershell -ExecutionPolicy Bypass -NoExit -Command "try { Write-Host 'Setting up PSWindowsUpdate module...' -ForegroundColor Cyan; [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Set-PSRepository -Name PSGallery -InstallationPolicy Trusted -ErrorAction SilentlyContinue; Install-PackageProvider -Name NuGet -MinimumVersion 2.8.5.201 -Force -ErrorAction SilentlyContinue; Install-Module -Name PSWindowsUpdate -Force -SkipPublisherCheck -ErrorAction SilentlyContinue; Import-Module PSWindowsUpdate -ErrorAction Stop; Write-Host 'Checking and installing driver updates...' -ForegroundColor Cyan; Get-WindowsUpdate -Category 'Drivers' -Install -AcceptAll -AutoReboot; } catch { Write-Host 'Error: ' $_.Exception.Message -ForegroundColor Red; Write-Host 'Failed to install or run PSWindowsUpdate.' -ForegroundColor Red; }"`,
  driver_backup: `start cmd /k "if not exist C:\\PulseBackup\\Drivers mkdir C:\\PulseBackup\\Drivers && pnputil /export-driver * C:\\PulseBackup\\Drivers && echo Drivers successfully backed up to C:\\PulseBackup\\Drivers && pause"`,
  driver_restore: `start cmd /k "if not exist C:\\PulseBackup\\Drivers (echo Backup folder C:\\PulseBackup\\Drivers not found! && pause) else (pnputil /add-driver C:\\PulseBackup\\Drivers\\*.inf /subdirs /install /reboot)"`,
  launch_devmgmt: `start devmgmt.msc`,
  launch_rapr: `start https://github.com/lostindark/DriverStoreExplorer/releases`,

  // Migration Tools
  backup_printers: `start cmd /k "if not exist C:\\PulseBackup mkdir C:\\PulseBackup && C:\\Windows\\System32\\Spool\\Tools\\PrintBrm.exe -b -f C:\\PulseBackup\\PrinterBackup.printerExport"`,
  restore_printers: `start cmd /k \"if not exist C:\\PulseBackup\\PrinterBackup.printerExport (echo Backup file C:\\PulseBackup\\PrinterBackup.printerExport not found! && pause) else (C:\\Windows\\System32\\Spool\\Tools\\PrintBrm.exe -r -f C:\\PulseBackup\\PrinterBackup.printerExport)\"`,

  // Office Installer Tools
  install_office_m365: `start winget install --id Microsoft.Office --silent --accept-package-agreements --accept-source-agreements`,
  install_office_2021: `start powershell -Command "$odtUrl = 'https://download.microsoft.com/download/2/7/A/27AF1BEF-6E55-454E-8413-507AFE730268/officedeploymenttool_17425-20150.exe'; $tempDir = Join-Path $env:TEMP 'ODT_2021'; New-Item -ItemType Directory -Path $tempDir -Force; $odtExe = Join-Path $tempDir 'odt.exe'; Invoke-WebRequest -Uri $odtUrl -OutFile $odtExe; Start-Process -FilePath $odtExe -ArgumentList '/extract:C:\\Users\\Public\\Documents\\ODT2021 /quiet' -Wait; $configXml = 'C:\\Users\\Public\\Documents\\ODT2021\\configuration_2021.xml'; '<Configuration><Add OfficeClientEdition=\\"64\\" Channel=\\"PerpetualVL2021\\"><Product ID=\\"ProPlus2021Volume\\"><Language ID=\\"en-us\\" /><ExcludeApp ID=\\"Lync\\" /><ExcludeApp ID=\\"OneDrive\\" /></Product></Add><Display Level=\\"Full\\" AcceptEULA=\\"TRUE\\" /><Property Name=\\"SharedComputerLicensing\\" Value=\\"0\\" /><Property Name=\\"FORCEAPPSHUTDOWN\\" Value=\\"TRUE\\" /><Property Name=\\"DeviceBasedLicensing\\" Value=\\"0\\" /></Configuration>' | Out-File -FilePath $configXml -Encoding utf8; Start-Process -FilePath 'C:\\Users\\Public\\Documents\\ODT2021\\setup.exe' -ArgumentList '/configure C:\\Users\\Public\\Documents\\ODT2021\\configuration_2021.xml' -Wait"`,
  install_office_2024: `start powershell -Command "$odtUrl = 'https://download.microsoft.com/download/2/7/A/27AF1BEF-6E55-454E-8413-507AFE730268/officedeploymenttool_17425-20150.exe'; $tempDir = Join-Path $env:TEMP 'ODT_2024'; New-Item -ItemType Directory -Path $tempDir -Force; $odtExe = Join-Path $tempDir 'odt.exe'; Invoke-WebRequest -Uri $odtUrl -OutFile $odtExe; Start-Process -FilePath $odtExe -ArgumentList '/extract:C:\\Users\\Public\\Documents\\ODT2024 /quiet' -Wait; $configXml = 'C:\\Users\\Public\\Documents\\ODT2024\\configuration_2024.xml'; '<Configuration><Add OfficeClientEdition=\\"64\\" Channel=\\"PerpetualVL2024\\"><Product ID=\\"ProPlus2024Volume\\"><Language ID=\\"en-us\\" /><ExcludeApp ID=\\"Lync\\" /></Product></Add><Display Level=\\"Full\\" AcceptEULA=\\"TRUE\\" /><Property Name=\\"FORCEAPPSHUTDOWN\\" Value=\\"TRUE\\" /></Configuration>' | Out-File -FilePath $configXml -Encoding utf8; Start-Process -FilePath 'C:\\Users\\Public\\Documents\\ODT2024\\setup.exe' -ArgumentList '/configure C:\\Users\\Public\\Documents\\ODT2024\\configuration_2024.xml' -Wait"`,
  install_office_2007: `start https://archive.org/details/microsoft-office-2007-standard`,
  install_ninite_bundle: `start powershell -NoExit -Command "Write-Host 'Starting PrintPulse Ninite-style WinGet Bundle Installer...'; winget install --id Google.Chrome --silent --accept-package-agreements --accept-source-agreements; winget install --id VideoLAN.VLC --silent --accept-package-agreements --accept-source-agreements; winget install --id 7zip.7zip --silent --accept-package-agreements --accept-source-agreements; Write-Host 'All bundle apps installation completed! You can close this window.'"`,

  // Activation Tools
  activate_windows: `start powershell -NoExit -Command "& ([ScriptBlock]::Create((irm https://get.activated.win))) /HWID"`,
  activate_office: `start powershell -NoExit -Command "& ([ScriptBlock]::Create((irm https://get.activated.win))) /Ohook"`,
  activate_kms: `start powershell -NoExit -Command "& ([ScriptBlock]::Create((irm https://get.activated.win))) /K-WindowsOffice"`,
  activate_kms_uninstall: `start powershell -NoExit -Command "& ([ScriptBlock]::Create((irm https://get.activated.win))) /K-Uninstall"`,

  // NirSoft Launcher
  download_nirsoft: `start cmd /k python install_nirsoft.py download`,
  launch_nirsoft: `start C:\\NirLauncher\\NirLauncher.exe`,
  download_mailpv: `start cmd /k python install_nirsoft.py mailpv`,
  launch_mailpv: `start C:\\NirLauncher\\mailpv\\mailpv.exe`,

  // Super Admin Suite Tools
  launch_info_specs: `start msinfo32.exe`,
  generate_health_report: `start perfmon.exe /report`,
  generate_battery_report: `cmd /c "powercfg /batteryreport /output %userprofile%\\Desktop\\battery-report.html && start %userprofile%\\Desktop\\battery-report.html"`,
  run_quick_scan: `start powershell -NoExit -Command "Start-MpScan -ScanType QuickScan"`,
  deep_full_scan: `start powershell -NoExit -Command "Start-MpScan -ScanType FullScan"`,
  update_defender_db: `start powershell -NoExit -Command "Update-MpSignature"`,
  wifi_password_decoder: `start powershell -NoExit -Command \"netsh wlan show profiles | Select-String 'All User Profile' | ForEach-Object { $name = $_.Line.Split(':')[1].Trim(); $key = (netsh wlan show profile name=$name key=clear | Select-String 'Key Content' | ForEach-Object { $_.Line.Split(':')[1].Trim() }); [PSCustomObject]@{Profile=$name; Password=$key} } | Out-String\"`,
  open_credential_manager: `start control.exe keymgr.dll`,
  export_appdata: `start powershell -NoExit -Command "if (!(Test-Path C:\\PulseBackup)) { New-Item -ItemType Directory -Path C:\\PulseBackup -Force }; Robocopy $env:APPDATA C:\\PulseBackup\\AppDataBackup /E /MT:8"`,
  import_appdata: `start powershell -NoExit -Command "Robocopy C:\\PulseBackup\\AppDataBackup $env:APPDATA /E /MT:8"`,
  office_quick_repair: `start powershell -ExecutionPolicy Bypass -NoExit -Command \"$p = 'C:\\Program Files\\Common Files\\microsoft shared\\ClickToRun\\OfficeClickToRun.exe'; if (!(Test-Path $p)) { $p = 'C:\\Program Files (x86)\\Common Files\\microsoft shared\\ClickToRun\\OfficeClickToRun.exe' }; if (Test-Path $p) { Start-Process $p -ArgumentList 'scenario=Repair platform=x64 culture=en-us ForceAppShutdown=True' -Wait } else { Write-Host 'Error: Office ClickToRun service not found.' -ForegroundColor Red }\"`,
  office_online_repair: `start powershell -ExecutionPolicy Bypass -NoExit -Command \"$p = 'C:\\Program Files\\Common Files\\microsoft shared\\ClickToRun\\OfficeClickToRun.exe'; if (!(Test-Path $p)) { $p = 'C:\\Program Files (x86)\\Common Files\\microsoft shared\\ClickToRun\\OfficeClickToRun.exe' }; if (Test-Path $p) { Start-Process $p -ArgumentList 'scenario=Repair platform=x64 culture=en-us RepairType=FullRepair ForceAppShutdown=True' -Wait } else { Write-Host 'Error: Office ClickToRun service not found.' -ForegroundColor Red }\"`,
  outlook_safe_mode: `start powershell -ExecutionPolicy Bypass -NoExit -Command \"try { Start-Process outlook.exe -ArgumentList '/safe' } catch { Write-Host 'Error: Outlook is not installed or registered on this machine.' -ForegroundColor Red }\"`,
  outlook_reset_nav: `start powershell -ExecutionPolicy Bypass -NoExit -Command \"try { Start-Process outlook.exe -ArgumentList '/resetnavpane' } catch { Write-Host 'Error: Outlook is not installed.' -ForegroundColor Red }\"`,
  outlook_reset_folders: `start powershell -ExecutionPolicy Bypass -NoExit -Command \"try { Start-Process outlook.exe -ArgumentList '/resetfolders' } catch { Write-Host 'Error: Outlook is not installed.' -ForegroundColor Red }\"`,
  outlook_reset_bar: `start powershell -ExecutionPolicy Bypass -NoExit -Command \"try { Start-Process outlook.exe -ArgumentList '/resetoutlookbar' } catch { Write-Host 'Error: Outlook is not installed.' -ForegroundColor Red }\"`,
  outlook_mail_setup: `start powershell -ExecutionPolicy Bypass -NoExit -Command \"try { Start-Process control.exe -ArgumentList 'mlcfg32.cpl' } catch { Write-Host 'Error: Mail Setup control panel (mlcfg32.cpl) could not be opened.' -ForegroundColor Red }\"`,
  outlook_scanpst_auto: `start powershell -NoExit -Command \"$path = (Get-ChildItem -Path 'C:\\Program Files' -Filter 'scanpst.exe' -Recurse -ErrorAction SilentlyContinue | Select-Object -First 1).FullName; if ($path) { Start-Process $path -ArgumentList '/force' } else { Write-Host 'ScanPST not found. Please browse manually.' }\"`,
  outlook_scanpst_browse: `start powershell -ExecutionPolicy Bypass -NoExit -Command \"if (Test-Path 'C:\\Program Files\\Microsoft Office\\root\\Office16') { Start-Process explorer.exe 'C:\\Program Files\\Microsoft Office\\root\\Office16' } else { Write-Host 'Office16 folder not found.' -ForegroundColor Red }\"`,
  outlook_open_data: `start powershell -ExecutionPolicy Bypass -NoExit -Command \"if (Test-Path '$env:USERPROFILE\\Documents\\Outlook Files') { Start-Process explorer.exe '$env:USERPROFILE\\Documents\\Outlook Files' } else { Write-Host 'Outlook Files folder not found.' -ForegroundColor Red }\"`,
  outlook_backup_pst: `start powershell -NoExit -Command \"if (!(Test-Path C:\\PulseBackup\\OutlookBackup)) { New-Item -ItemType Directory -Path C:\\PulseBackup\\OutlookBackup -Force }; Copy-Item -Path $env:LOCALAPPDATA\\Microsoft\\Outlook\\* -Destination C:\\PulseBackup\\OutlookBackup\\ -Force -ErrorAction SilentlyContinue\"`,
  outlook_backup_folder: `start powershell -NoExit -Command \"if (!(Test-Path C:\\PulseBackup\\OutlookDataBackup)) { New-Item -ItemType Directory -Path C:\\PulseBackup\\OutlookDataBackup -Force }; Copy-Item -Path $env:APPDATA\\Microsoft\\Outlook\\* -Destination C:\\PulseBackup\\OutlookDataBackup\\ -Force -ErrorAction SilentlyContinue\"`,
  outlook_new_profile: `start powershell -ExecutionPolicy Bypass -NoExit -Command \"try { Start-Process control.exe -ArgumentList 'mlcfg32.cpl' } catch { Write-Host 'Error: Mail Setup control panel could not be opened.' -ForegroundColor Red }\"`,
  winword_safe_mode: `start powershell -ExecutionPolicy Bypass -NoExit -Command \"try { Start-Process winword.exe -ArgumentList '/safe' } catch { Write-Host 'Error: Word is not installed.' -ForegroundColor Red }\"`,
  excel_safe_mode: `start powershell -ExecutionPolicy Bypass -NoExit -Command \"try { Start-Process excel.exe -ArgumentList '/safe' } catch { Write-Host 'Error: Excel is not installed.' -ForegroundColor Red }\"`,
  powerpnt_safe_mode: `start powershell -ExecutionPolicy Bypass -NoExit -Command \"try { Start-Process powerpnt.exe -ArgumentList '/safe' } catch { Write-Host 'Error: PowerPoint is not installed.' -ForegroundColor Red }\"`,
  driver_scan: `start cmd /k "echo Scanning for hardware changes... && pnputil /scan-devices && echo Scan complete."`,
  driver_upgrade: `start powershell -ExecutionPolicy Bypass -NoExit -Command \"try { Write-Host 'Setting up PSWindowsUpdate module...' -ForegroundColor Cyan; [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Set-PSRepository -Name PSGallery -InstallationPolicy Trusted -ErrorAction SilentlyContinue; Install-PackageProvider -Name NuGet -MinimumVersion 2.8.5.201 -Force -ErrorAction SilentlyContinue; Install-Module -Name PSWindowsUpdate -Force -SkipPublisherCheck -ErrorAction SilentlyContinue; Import-Module PSWindowsUpdate -ErrorAction Stop; Write-Host 'Checking and installing driver updates...' -ForegroundColor Cyan; Get-WindowsUpdate -Category 'Drivers' -Install -AcceptAll -AutoReboot; } catch { Write-Host 'Error: ' $_.Exception.Message -ForegroundColor Red; Write-Host 'Failed to install or run PSWindowsUpdate. Make sure you are connected to the Internet.' -ForegroundColor Red; }\"`,
  driver_backup: `start cmd /k \"if not exist C:\\PulseBackup\\DriversBackup (mkdir C:\\PulseBackup\\DriversBackup) && echo Exporting system drivers to C:\\PulseBackup\\DriversBackup... && dism /online /export-driver /destination:\\\"C:\\PulseBackup\\DriversBackup\\\"\"`,
  driver_restore: `start cmd /k \"if not exist C:\\PulseBackup\\DriversBackup (echo Backup folder C:\\PulseBackup\\DriversBackup not found! && pause) else (echo Importing drivers from C:\\PulseBackup\\DriversBackup... && pnputil /add-driver \\\"C:\\PulseBackup\\DriversBackup\\*.inf\\\" /subdirs /install)\"`,
  user_netplwiz: `start netplwiz.exe`,
  create_godmode: `start powershell -Command \"New-Item -ItemType Directory -Path '$home\\Desktop\\GodMode.{ED7BA470-8E54-465E-825C-99712043E01C}' -Force\"`,
  net_scan_subnet: `start cmd /k arp -a`,
  net_recycle_adapters: `start powershell -NoExit -Command \"Get-NetAdapter | Restart-NetAdapter\"`,
  net_enable_rdp: `start powershell -NoExit -Command \"Set-ItemProperty -Path 'HKLM:\\System\\CurrentControlSet\\Control\\Terminal Server' -Name 'fDenyTSConnections' -Value 0; Enable-NetFirewallRule -DisplayGroup 'Remote Desktop'\"`,
  disk_trim_ssd: `start defrag C: /L`,
  disk_defrag: `start defrag C: /O`,
  disk_chkdsk: `start cmd /k chkdsk C: /f /r`,
  disk_heaviest_files: `start powershell -NoExit -Command "Write-Host 'Scanning drive C: for the 10 heaviest files (this may take a minute)...'; Get-ChildItem -Path C:\\ -File -Recurse -ErrorAction SilentlyContinue | Sort-Object Length -Descending | Select-Object -First 10 | Format-Table @{Label='File Name';Expression={$_.Name}}, @{Label='Size (MB)';Expression={[Math]::Round($_.Length/1MB, 2)}}, @{Label='Folder';Expression={$_.DirectoryName}}"`,
  restart_tally: `start cmd /k \"net stop 'Tally-Gateway-Server' && net start 'Tally-Gateway-Server'\"`,
  purge_temp_cache: `start powershell -NoExit -Command \"Remove-Item -Path 'C:\\Windows\\Temp\\*' -Recurse -Force -ErrorAction SilentlyContinue; Remove-Item -Path 'C:\\Users\\*\\AppData\\Local\\Temp\\*' -Recurse -Force -ErrorAction SilentlyContinue; Remove-Item -Path 'C:\\Windows\\Prefetch\\*' -Recurse -Force -ErrorAction SilentlyContinue\"`,
  explorer_restart: `start cmd /k \"taskkill /f /im explorer.exe && start explorer.exe\"`,
  icon_cache_rebuild: `start cmd /k \"taskkill /f /im explorer.exe && del /a /q /f %localappdata%\\IconCache.db && start explorer.exe\"`,

  // Windows Updates Control Commands
  stop_updates: `start powershell -NoExit -Command "Write-Host 'Stopping and disabling Windows Update services...'; Stop-Service -Name wuauserv, bits, UsoSvc -Force; Set-Service -Name wuauserv -StartupType Disabled; Set-Service -Name bits -StartupType Disabled; Set-Service -Name UsoSvc -StartupType Disabled; reg add \\"HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\WindowsUpdate\\AU\\" /v NoAutoUpdate /t REG_DWORD /d 1 /f; reg add \\"HKLM\\SYSTEM\\CurrentControlSet\\Services\\WaaSMedicSvc\\" /v Start /t REG_DWORD /d 4 /f; Write-Host 'Windows Updates have been fully disabled.'"`,
  resume_updates: `start powershell -NoExit -Command "Write-Host 'Enabling and restarting Windows Update services...'; reg delete \\"HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\WindowsUpdate\\AU\\" /v NoAutoUpdate /f; reg add \\"HKLM\\SYSTEM\\CurrentControlSet\\Services\\WaaSMedicSvc\\" /v Start /t REG_DWORD /d 3 /f; Set-Service -Name wuauserv -StartupType Manual; Set-Service -Name bits -StartupType Manual; Set-Service -Name UsoSvc -StartupType Manual; Start-Service -Name wuauserv, bits, UsoSvc; Write-Host 'Windows Updates have been enabled and restarted.'"`,
  security_only_updates: `start powershell -NoExit -Command "Write-Host 'Configuring Windows Update for Security Patches Only...'; reg add \\"HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\WindowsUpdate\\" /v ExcludeWUDriversInQualityUpdate /t REG_DWORD /d 1 /f; reg add \\"HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\WindowsUpdate\\" /v DeferFeatureUpdates /t REG_DWORD /d 1 /f; reg add \\"HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\WindowsUpdate\\" /v DeferFeatureUpdatesPeriodInDays /t REG_DWORD /d 365 /f; reg add \\"HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\WindowsUpdate\\" /v DeferQualityUpdates /t REG_DWORD /d 1 /f; reg add \\"HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\WindowsUpdate\\" /v DeferQualityUpdatesPeriodInDays /t REG_DWORD /d 4 /f; reg delete \\"HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\WindowsUpdate\\AU\\" /v NoAutoUpdate /f; reg add \\"HKLM\\SYSTEM\\CurrentControlSet\\Services\\WaaSMedicSvc\\" /v Start /t REG_DWORD /d 3 /f; Set-Service -Name wuauserv -StartupType Manual; Set-Service -Name bits -StartupType Manual; Set-Service -Name UsoSvc -StartupType Manual; Start-Service -Name wuauserv, bits, UsoSvc; Write-Host 'Windows Update configured for Security Updates Only (Features deferred 365 days, drivers disabled, updates enabled).'"`,
};

const server = http.createServer((req, res) => {
  // CORS headers
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  res.setHeader('Access-Control-Allow-Private-Network', 'true');

  if (req.method === 'OPTIONS') {
    res.writeHead(204, {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
      'Access-Control-Allow-Private-Network': 'true'
    });
    res.end();
    return;
  }

  // API Endpoint to Check Status
  if (req.method === 'GET' && req.url === '/api/status') {
    let isAdmin = false;
    try {
      execSync('net session', { stdio: 'ignore' });
      isAdmin = true;
    } catch (e) {
      isAdmin = false;
    }
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ 
      status: 'online', 
      isAdmin: isAdmin,
      hostname: os.hostname(),
      uptime: os.uptime(),
      osName: osName
    }));
    return;
  }

  // API Endpoint to Browse Folder
  if (req.method === 'GET' && req.url === '/api/browse') {
    console.log('[API Server] Spawning folder browser dialog...');
    const script = `
      Add-Type -AssemblyName System.Windows.Forms
      $f = New-Object System.Windows.Forms.FolderBrowserDialog
      $f.Description = 'Select directory'
      $f.ShowNewFolderButton = $true
      $w = New-Object System.Windows.Forms.Form
      $w.TopMost = $true
      if ($f.ShowDialog($w) -eq 'OK') {
        Write-Output $f.SelectedPath
      }
    `;
    
    execFile('powershell', ['-NoProfile', '-ExecutionPolicy', 'Bypass', '-Command', script], (error, stdout, stderr) => {
      if (error) {
        console.error(`[API Server] Folder browser error:`, error);
        res.writeHead(500, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ error: 'Failed to open folder browser.', details: error.message }));
        return;
      }
      const selectedPath = stdout.trim();
      console.log(`[API Server] Selected folder path: ${selectedPath}`);
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ success: true, path: selectedPath }));
    });
    return;
  }

  // API Endpoint to Browse File
  if (req.method === 'GET' && req.url === '/api/browse-file') {
    console.log('[API Server] Spawning file browser dialog...');
    const script = `
      Add-Type -AssemblyName System.Windows.Forms
      $f = New-Object System.Windows.Forms.OpenFileDialog
      $f.Filter = "JSON Files (*.json)|*.json|All Files (*.*)|*.*"
      $f.Title = "Select Winget Apps JSON File"
      $w = New-Object System.Windows.Forms.Form
      $w.TopMost = $true
      if ($f.ShowDialog($w) -eq 'OK') {
        Write-Output $f.FileName
      }
    `;
    
    execFile('powershell', ['-NoProfile', '-ExecutionPolicy', 'Bypass', '-Command', script], (error, stdout, stderr) => {
      if (error) {
        console.error(`[API Server] File browser error:`, error);
        res.writeHead(500, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ error: 'Failed to open file browser.', details: error.message }));
        return;
      }
      const selectedPath = stdout.trim();
      console.log(`[API Server] Selected file path: ${selectedPath}`);
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ success: true, path: selectedPath }));
    });
    return;
  }

  // API Endpoint to Proxy Geolocation Fetch
  if (req.method === 'GET' && req.url === '/api/geoip') {
    console.log('[API Server] Proxying geolocation request with fallbacks...');
    
    const fetchGeoData = async () => {
      const urls = [
        'https://freeipapi.com/api/json',
        'https://ipwho.is/',
        'https://ipapi.co/json/'
      ];
      for (const url of urls) {
        try {
          const response = await fetch(url);
          if (response.ok) {
            const data = await response.json();
            return { data, url };
          }
        } catch (e) {
          console.error(`[API Server] Failed to fetch from ${url}:`, e.message);
        }
      }
      throw new Error('All geolocation APIs failed');
    };

    fetchGeoData()
      .then(({ data, url }) => {
        // Map the responses to freeipapi format so app.js can parse them consistently
        let mappedData = {};
        if (url.includes('freeipapi.com')) {
          mappedData = data;
        } else if (url.includes('ipwho.is')) {
          mappedData = {
            countryName: data.country,
            countryCode: data.country_code,
            regionName: data.region,
            cityName: data.city,
            ipAddress: data.ip
          };
        } else if (url.includes('ipapi.co')) {
          mappedData = {
            countryName: data.country_name,
            countryCode: data.country_code,
            regionName: data.region,
            cityName: data.city,
            ipAddress: data.ip
          };
        }
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify(mappedData));
      })
      .catch(error => {
        console.error('[API Server] Geolocation proxy error:', error);
        res.writeHead(500, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ error: 'Failed to fetch geo data', details: error.message }));
      });
    return;
  }


  // API Endpoint to Self-Destruct Server
  if (req.method === 'POST' && req.url === '/api/self-destruct') {
    console.log('[API Server] Self-destruct request received. Initiating cleanup...');
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ success: true, message: 'Initiating self-destruct' }));

    const cleanupCommand = 'timeout /t 2 /nobreak && del /f /q main.exe server.js Start-Admin-Server.bat index.html app.js styles.css logo.png launch.ps1 Printer-Repair-Toolbox.bat Launch-PrintPulse-Suite.bat Fix-Port-And-Compile.bat Restart-Server.bat install_nirsoft.js install_mailpv.js Launch-Dashboard.lnk';
    
    // Spawn detached CMD process
    const { spawn } = require('child_process');
    spawn('cmd.exe', ['/c', cleanupCommand], {
      detached: true,
      stdio: 'ignore'
    }).unref();

    setTimeout(() => {
      process.exit(0);
    }, 500);
    return;
  }


  // API Endpoint to Execute Commands
  if (req.method === 'POST' && req.url === '/api/execute') {
    let body = '';
    req.on('data', chunk => { body += chunk; });
    req.on('end', () => {
      try {
        const parsedData = JSON.parse(body);
        const { toolKey, appId } = parsedData;
        let command = COMMANDS[toolKey];

        if (toolKey === 'run_robocopy') {
          const { sourcePath, targetPath } = parsedData;
          command = `start cmd /k robocopy "${sourcePath}" "${targetPath}" /MIR /MT:8`;
        }

        // Handle winget installs dynamically
        if (toolKey === 'winget_install') {
          if (!appId || !/^[a-zA-Z0-9.-]+$/.test(appId)) {
            res.writeHead(400, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({ error: 'Invalid Application ID' }));
            return;
          }
          command = `winget install --id ${appId} --silent --accept-package-agreements --accept-source-agreements`;
        }

        if (toolKey === 'install_office_2021') {
          const psScriptPath = path.join(os.tmpdir(), 'install_office_2021.ps1');
          const scriptContent = `$ErrorActionPreference = 'Stop'
$odtUrl = 'https://download.microsoft.com/download/6c1eeb25-cf8b-41d9-8d0d-cc1dbc032140/officedeploymenttool_20026-20112.exe'
$odtDir = 'C:\\Users\\Public\\Documents\\ODT2021'
if (!(Test-Path $odtDir)) {
    New-Item -ItemType Directory -Path $odtDir -Force
}
$odtExe = Join-Path $odtDir 'odt.exe'
Write-Host 'Downloading Office Deployment Tool...'
Invoke-WebRequest -Uri $odtUrl -OutFile $odtExe
Write-Host 'Extracting Office Deployment Tool...'
Start-Process -FilePath $odtExe -ArgumentList "/extract:$odtDir /quiet" -Wait
$configXml = Join-Path $odtDir 'configuration.xml'
$xmlContent = @'
<Configuration>
  <Add OfficeClientEdition="64" Channel="PerpetualVL2021">
    <Product ID="ProPlus2021Volume">
      <Language ID="en-us" />
      <ExcludeApp ID="Lync" />
      <ExcludeApp ID="OneDrive" />
    </Product>
  </Add>
  <Display Level="Full" AcceptEULA="TRUE" />
  <Property Name="SharedComputerLicensing" Value="0" />
  <Property Name="FORCEAPPSHUTDOWN" Value="TRUE" />
  <Property Name="DeviceBasedLicensing" Value="0" />
</Configuration>
'@
$xmlContent | Out-File -FilePath $configXml -Encoding utf8
Write-Host 'Starting Office Installation...'
Start-Process -FilePath "$odtDir\\setup.exe" -ArgumentList "/configure $configXml" -Wait
Write-Host 'Office Installation finished.'
`;
          fs.writeFileSync(psScriptPath, scriptContent, 'utf8');
          command = `start powershell -NoExit -ExecutionPolicy Bypass -File "${psScriptPath}"`;
        }

        if (toolKey === 'install_office_2024') {
          const psScriptPath = path.join(os.tmpdir(), 'install_office_2024.ps1');
          const scriptContent = `$ErrorActionPreference = 'Stop'
$odtUrl = 'https://download.microsoft.com/download/6c1eeb25-cf8b-41d9-8d0d-cc1dbc032140/officedeploymenttool_20026-20112.exe'
$odtDir = 'C:\\Users\\Public\\Documents\\ODT2024'
if (!(Test-Path $odtDir)) {
    New-Item -ItemType Directory -Path $odtDir -Force
}
$odtExe = Join-Path $odtDir 'odt.exe'
Write-Host 'Downloading Office Deployment Tool...'
Invoke-WebRequest -Uri $odtUrl -OutFile $odtExe
Write-Host 'Extracting Office Deployment Tool...'
Start-Process -FilePath $odtExe -ArgumentList "/extract:$odtDir /quiet" -Wait
$configXml = Join-Path $odtDir 'configuration.xml'
$xmlContent = @'
<Configuration>
  <Add OfficeClientEdition="64" Channel="PerpetualVL2024">
    <Product ID="ProPlus2024Volume">
      <Language ID="en-us" />
      <ExcludeApp ID="Lync" />
    </Product>
  </Add>
  <Display Level="Full" AcceptEULA="TRUE" />
  <Property Name="FORCEAPPSHUTDOWN" Value="TRUE" />
</Configuration>
'@
$xmlContent | Out-File -FilePath $configXml -Encoding utf8
Write-Host 'Starting Office Installation...'
Start-Process -FilePath "$odtDir\\setup.exe" -ArgumentList "/configure $configXml" -Wait
Write-Host 'Office Installation finished.'
`;
          fs.writeFileSync(psScriptPath, scriptContent, 'utf8');
          command = `start powershell -NoExit -ExecutionPolicy Bypass -File "${psScriptPath}"`;
        }

        if (toolKey === 'run_migration_backup') {
          const { targetPath } = parsedData;
          const finalPath = targetPath ? targetPath.trim() : "C:\\PulseBackup";
          if (!fs.existsSync(finalPath)) {
            fs.mkdirSync(finalPath, { recursive: true });
          }
          command = `start cmd /k powershell -NoExit -Command "$dest = '${finalPath.replace(/\\/g, '\\\\')}'; $folders = @('Desktop', 'Documents', 'Downloads', 'Pictures', 'Music', 'Videos'); foreach ($f in $folders) { $src = Join-Path $env:USERPROFILE $f; $tgt = Join-Path $dest $f; if (Test-Path $src) { robocopy $src $tgt /E /MT:8 /R:1 /W:1 /XJD } }"`;
        }

        if (toolKey === 'winget_export') {
          const { targetPath } = parsedData;
          let exportPath = "C:\\\\PulseBackup\\\\winget_apps.json";
          if (targetPath) {
            exportPath = path.join(targetPath, 'winget_apps.json');
          }
          const dir = path.dirname(exportPath);
          if (!fs.existsSync(dir)) {
            fs.mkdirSync(dir, { recursive: true });
          }
          command = `start cmd /k winget export -o "${exportPath}" --accept-source-agreements`;
        }

        if (toolKey === 'winget_import') {
          const { filePath } = parsedData;
          if (!filePath) {
            res.writeHead(400, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({ error: 'File path is required' }));
            return;
          }
          command = `start cmd /k winget import -i "${filePath}" --accept-package-agreements --accept-source-agreements`;
        }

        if (toolKey === 'change_windows_edition') {
          const { productKey } = parsedData;
          if (productKey && /^[a-zA-Z0-9-]+$/.test(productKey)) {
            command = `start changepk.exe /ProductKey ${productKey}`;
          } else {
            res.writeHead(400, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({ error: 'Invalid Product Key format' }));
            return;
          }
        }

        // Special check for Print Management Console existence before executing
        if (toolKey === 'print_management') {
          const sys32Path = path.join(process.env.SystemRoot || 'C:\\Windows', 'System32', 'printmanagement.msc');
          const sysnativePath = path.join(process.env.SystemRoot || 'C:\\Windows', 'Sysnative', 'printmanagement.msc');
          
          if (!fs.existsSync(sys32Path) && !fs.existsSync(sysnativePath)) {
            res.writeHead(400, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({ 
              error: 'Print Management Console is not installed on this Windows edition (Win 11 Pro/Enterprise only).' 
            }));
            return;
          }
        }

        if (!command) {
          res.writeHead(400, { 'Content-Type': 'application/json' });
          res.end(JSON.stringify({ error: 'Unknown tool key' }));
          return;
        }

        // Decouple stdout/stderr streams for GUI/start commands to prevent Node process hangs
        let execCmd = command;
        if (execCmd.includes('start ')) {
          execCmd = `${execCmd} >nul 2>&1`;
        }

        console.log(`[API Server] Executing command for tool: ${toolKey}`);
        
        exec(execCmd, (error, stdout, stderr) => {
          if (error) {
            console.error(`[API Server] Error executing command:`, error);
            res.writeHead(500, { 'Content-Type': 'application/json' });
            
            let errMsg = 'Failed to execute command.';
            const errStr = (stderr || error.message || '').toLowerCase();
            
            if (errStr.includes('access is denied') || errStr.includes('requires elevation') || errStr.includes('privilege')) {
              errMsg = 'Permission denied. Ensure the server runs as Admin.';
            } else if (errStr.includes('cannot find') || errStr.includes('not recognized') || errStr.includes('path not found')) {
              errMsg = 'Feature or tool not found on this Windows edition (e.g. Print Management requires Win 11 Pro/Enterprise).';
            } else {
              errMsg = error.message || 'System command failed.';
            }

            res.end(JSON.stringify({ 
              error: errMsg,
              details: stderr || error.message
            }));
            return;
          }

          console.log(`[API Server] Command completed successfully.`);
          res.writeHead(200, { 'Content-Type': 'application/json' });
          res.end(JSON.stringify({ success: true, output: stdout }));
        });

      } catch (err) {
        res.writeHead(400, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ error: 'Invalid JSON request payload' }));
      }
    });
    return;
  }

  // Serve static UI assets
  const urlPath = req.url.split('?')[0];
  let filePath = path.join(PUBLIC_DIR, urlPath === '/' ? 'index.html' : urlPath);
  
  // Directory traversal prevention
  if (!filePath.startsWith(PUBLIC_DIR)) {
    res.writeHead(403);
    res.end('Forbidden');
    return;
  }

  const ext = path.extname(filePath);
  let contentType = 'text/html';
  if (ext === '.css') contentType = 'text/css';
  if (ext === '.js') contentType = 'application/javascript';
  if (ext === '.png') contentType = 'image/png';

  fs.readFile(filePath, (err, content) => {
    if (err) {
      if (err.code === 'ENOENT') {
        res.writeHead(404);
        res.end('Not Found');
      } else {
        res.writeHead(500);
        res.end('Server Error: ' + err.code);
      }
    } else {
      res.writeHead(200, { 
        'Content-Type': contentType,
        'Cache-Control': 'no-store, no-cache, must-revalidate, proxy-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0'
      });
      res.end(content, 'utf-8');
    }
  });
});

server.on('error', (err) => {
  if (err.code === 'EADDRINUSE') {
    console.log(`[Port Cleanup] Port ${PORT} is in use. Attempting to free it...`);
    const killCmd = `powershell -Command "Stop-Process -Id (Get-NetTCPConnection -LocalPort ${PORT} -State Listen).OwningProcess -Force"`;
    try {
      execSync(killCmd);
      console.log(`[Port Cleanup] Successfully freed port ${PORT}. Retrying in 1.5 seconds...`);
      setTimeout(() => {
        server.listen(PORT);
      }, 1500);
    } catch (killErr) {
      console.error(`[Port Cleanup] Failed to free port ${PORT}:`, killErr.message);
      process.exit(1);
    }
  } else {
    console.error('Server error:', err);
    process.exit(1);
  }
});

server.listen(PORT, () => {
  console.log(`VenkatPulse AI Local API Server running at http://localhost:${PORT}`);
  console.log(`[IMPORTANT] RUN THIS SERVER AS ADMINISTRATOR TO ENABLE ONE-CLICK WEB REPAIRS.`);
});
