import os
import sys
import json
import socket
import ctypes
import platform
import subprocess
import time
import webbrowser
import urllib.request
from http.server import HTTPServer, BaseHTTPRequestHandler

# 0. Background Watcher Process for Auto-Cleanup on Exit
if "--watcher" in sys.argv:
    try:
        parent_pid = int(sys.argv[sys.argv.index("--watcher") + 1])
        curr_dir = sys.argv[sys.argv.index("--watcher") + 2]
        par_dir = sys.argv[sys.argv.index("--watcher") + 3]
        fld_name = sys.argv[sys.argv.index("--watcher") + 4]
        
        # Function to check if PID is alive
        def is_alive(pid):
            handle = ctypes.windll.kernel32.OpenProcess(0x0400, False, pid)
            if handle:
                exit_code = ctypes.c_ulong()
                ctypes.windll.kernel32.GetExitCodeProcess(handle, ctypes.byref(exit_code))
                ctypes.windll.kernel32.CloseHandle(handle)
                return exit_code.value == 259  # 259 is STILL_ACTIVE
            return False
            
        # Loop until the parent process exits
        while is_alive(parent_pid):
            time.sleep(1)
            
        # Parent process has exited! Perform cleanup.
        time.sleep(1.5)  # Extra padding to ensure locks are fully released
        
        system_folders = ["desktop", "downloads", "documents", "my documents", "users", "windows", "system32"]
        if fld_name.lower() in system_folders or len(fld_name) <= 3:
            cleanup_cmd = (
                f'del /f /q /s "{curr_dir}\\main.exe" "{curr_dir}\\main.old" "{curr_dir}\\PrintPulse.exe" '
                f'"{curr_dir}\\server.js" "{curr_dir}\\server.py" "{curr_dir}\\gui_app.py" '
                f'"{curr_dir}\\Start-Admin-Server.bat" "{curr_dir}\\index.html" "{curr_dir}\\app.js" '
                f'"{curr_dir}\\styles.css" "{curr_dir}\\logo.png" "{curr_dir}\\main.spec" '
                f'"{curr_dir}\\PrintPulse.spec" "{curr_dir}\\build_exe.bat" '
                f'"{curr_dir}\\*puls*.zip" "{curr_dir}\\*pulse*.zip" "{curr_dir}\\main.zip" '
                f'"{par_dir}\\*puls*.zip" "{par_dir}\\*pulse*.zip" "{par_dir}\\main.zip" && '
                f'rmdir /s /q "{curr_dir}\\dist" "{curr_dir}\\build" "{curr_dir}\\__pycache__"'
            )
        else:
            cleanup_cmd = (
                f'cd /d "{par_dir}" && '
                f'rmdir /s /q "{curr_dir}" && '
                f'del /f /q *puls*.zip *pulse*.zip main.zip'
            )
            
        subprocess.Popen(['cmd.exe', '/c', cleanup_cmd], creationflags=0x00000008)
    except Exception as e:
        pass
    sys.exit(0)

# 1. Auto-Elevation to Administrator
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if "--no-admin" not in sys.argv and not is_admin():
    try:
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    except Exception as e:
        print(f"Failed to elevate: {e}")
    sys.exit(0)

# Resolve Public Directory for static files
if getattr(sys, 'frozen', False):
    # Compiled EXE mode: serve from directory containing the EXE
    PUBLIC_DIR = os.path.dirname(sys.executable)
else:
    # Python script mode: serve from directory containing the script
    PUBLIC_DIR = os.path.dirname(os.path.abspath(__file__))

PORT = 3000

# 2. Port Cleanup (free port 3000 if occupied)
def free_port(port):
    try:
        output = subprocess.check_output(f'netstat -aon | findstr :{port}', shell=True, text=True)
        lines = output.strip().split('\n')
        pids_killed = set()
        for line in lines:
            if "LISTENING" in line:
                parts = line.split()
                if len(parts) >= 5:
                    pid = parts[-1]
                    if pid not in pids_killed and pid != "0":
                        subprocess.run(f'taskkill /F /PID {pid}', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                        pids_killed.add(pid)
        if pids_killed:
            time.sleep(1.5)  # Wait for port to clear
    except Exception:
        pass

# Query OS Name once
OS_NAME = "Windows OS"
try:
    OS_NAME = subprocess.check_output(
        'powershell -Command "(Get-CimInstance Win32_OperatingSystem).Caption"',
        shell=True,
        text=True
    ).strip()
except Exception:
    try:
        raw = subprocess.check_output('wmic os get Caption /value', shell=True, text=True)
        for line in raw.split('\n'):
            if "Caption=" in line:
                OS_NAME = line.split("=")[1].strip()
                break
    except Exception:
        OS_NAME = f"Windows ({platform.release()})"

# Static command definitions mapped exactly from server.js
COMMANDS = {
    "quick_repair": 'powershell -Command "Stop-Service -Name Spooler -Force; Remove-Item -Path \'C:\\Windows\\System32\\spool\\PRINTERS\\*\' -Force -Recurse; Start-Service -Name Spooler"',
    "clear_queue": 'powershell -Command "Stop-Service -Name Spooler -Force; Remove-Item -Path \'C:\\Windows\\System32\\spool\\PRINTERS\\*\' -Force -Recurse; Start-Service -Name Spooler"',
    "restart_spooler": 'powershell -Command "Restart-Service -Name Spooler -Force"',
    "devices_printers": "start control printers",
    "print_management": "start printmanagement.msc",
    "sharing_center": "start control.exe /name Microsoft.NetworkAndSharingCenter",
    "point_print_fix": 'reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows NT\\Printers\\PointAndPrint" /v RestrictDriverInstallationToAdministrators /t REG_DWORD /d 0 /f && powershell -Command "Restart-Service -Name Spooler -Force"',
    "rpc_fixes": 'reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows NT\\Printers\\RPC" /v RpcOverNamedPipes /t REG_DWORD /d 1 /f && reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows NT\\Printers\\RPC" /v RpcUseNamedPipeShare /t REG_DWORD /d 1 /f && reg add "HKLM\\System\\CurrentControlSet\\Control\\Print" /v RpcAuthnLevelPrivacyEnabled /t REG_DWORD /d 0 /f && powershell -Command "Restart-Service -Name Spooler -Force"',
    "network_discovery": 'netsh advfirewall firewall set rule group="Network Discovery" new enable=Yes',
    "enable_smb1": 'start powershell -NoExit -Command "Enable-WindowsOptionalFeature -Online -FeatureName \'SMB1Protocol\' -All -NoRestart"',
    "disable_smb1": 'start powershell -NoExit -Command "Disable-WindowsOptionalFeature -Online -FeatureName \'SMB1Protocol\' -Force -NoRestart"',
    "enable_lpd": 'start powershell -NoExit -Command "Write-Host \'Enabling LPD Print Service and LPR Port Monitor...\'; Enable-WindowsOptionalFeature -Online -FeatureName \'LPDPrintService\' -All -NoRestart; Enable-WindowsOptionalFeature -Online -FeatureName \'LPRPortMonitor\' -All -NoRestart; Write-Host \'LPD and LPR Port features enabled!\'"',

    # Windows Repairs
    "sfc_scan": "start cmd /k sfc /scannow",
    "dism_restore": "start cmd /k dism /online /cleanup-image /restorehealth",
    "reset_wua": 'start powershell -NoExit -Command "Stop-Service -Name wuauserv,bits,cryptsvc -Force; Remove-Item -Path C:\\Windows\\SoftwareDistribution\\* -Recurse -Force; Start-Service -Name wuauserv,bits,cryptsvc"',
    "flush_dns": "ipconfig /flushdns",
    "reset_winsock": "netsh winsock reset",
    "reset_firewall": "netsh advfirewall reset",

    # Windows Debloater
    "create_restore_point": 'start powershell -NoExit -Command "Enable-ComputerRestore -Drive C:; Checkpoint-Computer -Description \'WinPulseBeforeRepair\' -RestorePointType MODIFY_SETTINGS"',
    "disable_telemetry": 'reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\DataCollection" /v AllowTelemetry /t REG_DWORD /d 0 /f && powershell -Command "Stop-Service -Name DiagTrack -Force; Set-Service -Name DiagTrack -StartupType Disabled"',
    "disable_cortana": 'reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\Windows Search" /v AllowCortana /t REG_DWORD /d 0 /f',
    "disable_onedrive": 'reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\OneDrive" /v DisableFileSyncNGSC /t REG_DWORD /d 1 /f && taskkill /F /IM OneDrive.exe',
    "disable_xbox": 'powershell -Command "Stop-Service -Name XblAuthManager,XblGameSave,XboxNetApiSvc -Force; Set-Service -Name XblAuthManager -StartupType Disabled; Set-Service -Name XblGameSave -StartupType Disabled; Set-Service -Name XboxNetApiSvc -StartupType Disabled"',
    "uninstall_bloatware": 'start powershell -NoExit -Command "@(\'*XboxApp*\', \'*ZuneMusic*\', \'*BingNews*\', \'*Office.OneNote*\', \'*SolitaireCollection*\') | ForEach-Object { Get-AppxPackage -AllUsers $_ | Remove-AppxPackage -ErrorAction SilentlyContinue }"',
    "ultimate_performance": 'powercfg -duplicatescheme e9a42b02-d5df-448d-aa00-03f14749eb61 && powercfg -setactive e9a42b02-d5df-448d-aa00-03f14749eb61',
    "disable_bing_search": 'reg add "HKCU\\Software\\Policies\\Microsoft\\Windows\\Explorer" /v DisableSearchBoxSuggestions /t REG_DWORD /d 1 /f && reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Search" /v BingSearchEnabled /t REG_DWORD /d 0 /f',
    "optimize_visual_effects": 'reg add "HKCU\\Control Panel\\Desktop" /v MenuShowDelay /t REG_SZ /d 0 /f && reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\VisualEffects" /v VisualFXSetting /t REG_DWORD /d 2 /f',
    "deep_temp_clean": 'start cmd /k powershell -NoExit -Command "Write-Host \'Cleaning Temporary folders...\'; Remove-Item -Path $env:TEMP\\* -Recurse -Force -ErrorAction SilentlyContinue; Remove-Item -Path \'C:\\Windows\\Temp\\*\' -Recurse -Force -ErrorAction SilentlyContinue; Remove-Item -Path \'C:\\Windows\\Prefetch\\*\' -Recurse -Force -ErrorAction SilentlyContinue; Write-Host \'Temporary folders cleared successfully!\'"',
    "reset_update_cache": 'start cmd /k powershell -NoExit -Command "Write-Host \'Stopping Windows Update services...\'; Stop-Service -Name wuauserv, bits, cryptsvc -Force; Write-Host \'Clearing cache...\'; Remove-Item -Path \'C:\\Windows\\SoftwareDistribution\\*\' -Recurse -Force -ErrorAction SilentlyContinue; Write-Host \'Restarting services...\'; Start-Service -Name wuauserv, bits, cryptsvc; Write-Host \'Windows Update Cache reset successfully!\'"',
    "network_reset_dns": 'start cmd /k "ipconfig /release && ipconfig /renew && ipconfig /flushdns && netsh winsock reset && netsh int ip reset"',

    # Administrative Shortcuts
    "lusrmgr": "start lusrmgr.msc",
    "uac_settings": "start useraccountcontrolsettings.exe",
    "sys_properties": "start sysdm.cpl",
    "comp_mgmt": "start compmgmt.msc",
    "gp_editor": "start gpedit.msc",
    "reg_editor": "start regedit.exe",

    # Migration Tools
    "backup_printers": "start cmd /k \"if not exist C:\\PulseBackup mkdir C:\\PulseBackup && C:\\Windows\\System32\\Spool\\Tools\\PrintBrm.exe -b -f C:\\PulseBackup\\PrinterBackup.printerExport\"",
    "restore_printers": 'start cmd /k "if not exist C:\\PulseBackup\\PrinterBackup.printerExport (echo Backup file C:\\PulseBackup\\PrinterBackup.printerExport not found! && pause) else (C:\\Windows\\System32\\Spool\\Tools\\PrintBrm.exe -r -f C:\\PulseBackup\\PrinterBackup.printerExport)"',

    # Office Installer
    "install_office_m365": "start winget install --id Microsoft.Office --silent --accept-package-agreements --accept-source-agreements",
    "install_office_2007": "start https://archive.org/details/microsoft-office-2007-standard",
    "install_ninite_bundle": 'start powershell -NoExit -Command "Write-Host \'Starting PrintPulse Ninite-style WinGet Bundle Installer...\'; winget install --id Google.Chrome --silent --accept-package-agreements --accept-source-agreements; winget install --id VideoLAN.VLC --silent --accept-package-agreements --accept-source-agreements; winget install --id 7zip.7zip --silent --accept-package-agreements --accept-source-agreements; Write-Host \'All bundle apps installation completed! You can close this window.\'"',

    # Activation Tools
    "activate_windows": 'start powershell -NoExit -Command "& ([ScriptBlock]::Create((irm https://get.activated.win))) /HWID"',
    "activate_office": 'start powershell -NoExit -Command "& ([ScriptBlock]::Create((irm https://get.activated.win))) /Ohook"',
    "activate_kms": 'start powershell -NoExit -Command "& ([ScriptBlock]::Create((irm https://get.activated.win))) /K-WindowsOffice"',
    "activate_kms_uninstall": 'start powershell -NoExit -Command "& ([ScriptBlock]::Create((irm https://get.activated.win))) /K-Uninstall"',

    # NirSoft Launcher
    "download_nirsoft": "start cmd /k python install_nirsoft.py download",
    "launch_nirsoft": "start C:\\NirLauncher\\NirLauncher.exe",
    "download_mailpv": "start cmd /k python install_nirsoft.py mailpv",
    "launch_mailpv": "start C:\\NirLauncher\\mailpv\\mailpv.exe",

    # Super Admin Suite Tools
    "launch_info_specs": "start msinfo32.exe",
    "generate_health_report": "start perfmon.exe /report",
    "generate_battery_report": 'cmd /c "powercfg /batteryreport /output %userprofile%\\Desktop\\battery-report.html && start %userprofile%\\Desktop\\battery-report.html"',
    "run_quick_scan": 'start powershell -NoExit -Command "Start-MpScan -ScanType QuickScan"',
    "deep_full_scan": 'start powershell -NoExit -Command "Start-MpScan -ScanType FullScan"',
    "update_defender_db": 'start powershell -NoExit -Command "Update-MpSignature"',
    "wifi_password_decoder": 'start powershell -NoExit -Command "netsh wlan show profiles | Select-String \'All User Profile\' | ForEach-Object { $name = $_.Line.Split(\':\')[1].Trim(); $key = (netsh wlan show profile name=$name key=clear | Select-String \'Key Content\' | ForEach-Object { $_.Line.Split(\':\')[1].Trim() }); [PSCustomObject]@{Profile=$name; Password=$key} } | Out-String"',
    "open_credential_manager": "start control.exe keymgr.dll",
    "export_appdata": 'start powershell -NoExit -Command "if (!(Test-Path C:\\PulseBackup)) { New-Item -ItemType Directory -Path C:\\PulseBackup -Force }; Robocopy $env:APPDATA C:\\PulseBackup\\AppDataBackup /E /MT:8"',
    "import_appdata": 'start powershell -NoExit -Command "Robocopy C:\\PulseBackup\\AppDataBackup $env:APPDATA /E /MT:8"',
    "office_quick_repair": 'start powershell -ExecutionPolicy Bypass -NoExit -Command "$p = \'C:\\Program Files\\Common Files\\microsoft shared\\ClickToRun\\OfficeClickToRun.exe\'; if (!(Test-Path $p)) { $p = \'C:\\Program Files (x86)\\Common Files\\microsoft shared\\ClickToRun\\OfficeClickToRun.exe\' }; if (Test-Path $p) { Start-Process $p -ArgumentList \'scenario=Repair platform=x64 culture=en-us ForceAppShutdown=True\' -Wait } else { Write-Host \'Error: Office ClickToRun service not found.\' -ForegroundColor Red }"',
    "office_online_repair": 'start powershell -ExecutionPolicy Bypass -NoExit -Command "$p = \'C:\\Program Files\\Common Files\\microsoft shared\\ClickToRun\\OfficeClickToRun.exe\'; if (!(Test-Path $p)) { $p = \'C:\\Program Files (x86)\\Common Files\\microsoft shared\\ClickToRun\\OfficeClickToRun.exe\' }; if (Test-Path $p) { Start-Process $p -ArgumentList \'scenario=Repair platform=x64 culture=en-us RepairType=FullRepair ForceAppShutdown=True\' -Wait } else { Write-Host \'Error: Office ClickToRun service not found.\' -ForegroundColor Red }"',
    "outlook_safe_mode": 'start powershell -ExecutionPolicy Bypass -NoExit -Command "try { Start-Process outlook.exe -ArgumentList \'/safe\' } catch { Write-Host \'Error: Outlook is not installed or registered on this machine.\' -ForegroundColor Red }"',
    "outlook_reset_nav": 'start powershell -ExecutionPolicy Bypass -NoExit -Command "try { Start-Process outlook.exe -ArgumentList \'/resetnavpane\' } catch { Write-Host \'Error: Outlook is not installed.\' -ForegroundColor Red }"',
    "outlook_reset_folders": 'start powershell -ExecutionPolicy Bypass -NoExit -Command "try { Start-Process outlook.exe -ArgumentList \'/resetfolders\' } catch { Write-Host \'Error: Outlook is not installed.\' -ForegroundColor Red }"',
    "outlook_reset_bar": 'start powershell -ExecutionPolicy Bypass -NoExit -Command "try { Start-Process outlook.exe -ArgumentList \'/resetoutlookbar\' } catch { Write-Host \'Error: Outlook is not installed.\' -ForegroundColor Red }"',
    "outlook_mail_setup": 'start powershell -ExecutionPolicy Bypass -NoExit -Command "try { Start-Process control.exe -ArgumentList \'mlcfg32.cpl\' } catch { Write-Host \'Error: Mail Setup control panel (mlcfg32.cpl) could not be opened.\' -ForegroundColor Red }"',
    "outlook_scanpst_auto": 'start powershell -NoExit -Command "$path = (Get-ChildItem -Path \'C:\\Program Files\' -Filter \'scanpst.exe\' -Recurse -ErrorAction SilentlyContinue | Select-Object -First 1).FullName; if ($path) { Start-Process $path -ArgumentList \'/force\' } else { Write-Host \'ScanPST not found. Please browse manually.\' }"',
    "outlook_scanpst_browse": 'start powershell -ExecutionPolicy Bypass -NoExit -Command "if (Test-Path \'C:\\Program Files\\Microsoft Office\\root\\Office16\') { Start-Process explorer.exe \'C:\\Program Files\\Microsoft Office\\root\\Office16\' } else { Write-Host \'Office16 folder not found.\' -ForegroundColor Red }"',
    "outlook_open_data": 'start powershell -ExecutionPolicy Bypass -NoExit -Command "if (Test-Path \'$env:USERPROFILE\\Documents\\Outlook Files\') { Start-Process explorer.exe \'$env:USERPROFILE\\Documents\\Outlook Files\' } else { Write-Host \'Outlook Files folder not found.\' -ForegroundColor Red }"',
    "outlook_backup_pst": 'start powershell -NoExit -Command "if (!(Test-Path C:\\PulseBackup\\OutlookBackup)) { New-Item -ItemType Directory -Path C:\\PulseBackup\\OutlookBackup -Force }; Copy-Item -Path $env:LOCALAPPDATA\\Microsoft\\Outlook\\* -Destination C:\\PulseBackup\\OutlookBackup\\ -Force -ErrorAction SilentlyContinue"',
    "outlook_backup_folder": 'start powershell -NoExit -Command "if (!(Test-Path C:\\PulseBackup\\OutlookDataBackup)) { New-Item -ItemType Directory -Path C:\\PulseBackup\\OutlookDataBackup -Force }; Copy-Item -Path $env:APPDATA\\Microsoft\\Outlook\\* -Destination C:\\PulseBackup\\OutlookDataBackup\\ -Force -ErrorAction SilentlyContinue"',
    "outlook_new_profile": 'start powershell -ExecutionPolicy Bypass -NoExit -Command "try { Start-Process control.exe -ArgumentList \'mlcfg32.cpl\' } catch { Write-Host \'Error: Mail Setup control panel could not be opened.\' -ForegroundColor Red }"',
    "winword_safe_mode": 'start powershell -ExecutionPolicy Bypass -NoExit -Command "try { Start-Process winword.exe -ArgumentList \'/safe\' } catch { Write-Host \'Error: Word is not installed.\' -ForegroundColor Red }"',
    "excel_safe_mode": 'start powershell -ExecutionPolicy Bypass -NoExit -Command "try { Start-Process excel.exe -ArgumentList \'/safe\' } catch { Write-Host \'Error: Excel is not installed.\' -ForegroundColor Red }"',
    "powerpnt_safe_mode": 'start powershell -ExecutionPolicy Bypass -NoExit -Command "try { Start-Process powerpnt.exe -ArgumentList \'/safe\' } catch { Write-Host \'Error: PowerPoint is not installed.\' -ForegroundColor Red }"',
    "driver_scan": 'start cmd /k "echo Scanning for hardware changes... && pnputil /scan-devices && echo Scan complete."',
    "driver_upgrade": 'start powershell -ExecutionPolicy Bypass -NoExit -Command "try { Write-Host \'Setting up PSWindowsUpdate module...\' -ForegroundColor Cyan; [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Set-PSRepository -Name PSGallery -InstallationPolicy Trusted -ErrorAction SilentlyContinue; Install-PackageProvider -Name NuGet -MinimumVersion 2.8.5.201 -Force -ErrorAction SilentlyContinue; Install-Module -Name PSWindowsUpdate -Force -SkipPublisherCheck -ErrorAction SilentlyContinue; Import-Module PSWindowsUpdate -ErrorAction Stop; Write-Host \'Checking and installing driver updates...\' -ForegroundColor Cyan; Get-WindowsUpdate -Category \'Drivers\' -Install -AcceptAll -AutoReboot; } catch { Write-Host \'Error: \' $_.Exception.Message -ForegroundColor Red; Write-Host \'Failed to install or run PSWindowsUpdate. Make sure you are connected to the Internet.\' -ForegroundColor Red; }"',
    "driver_backup": 'start cmd /k "if not exist C:\\PulseBackup\\DriversBackup (mkdir C:\\PulseBackup\\DriversBackup) && echo Exporting system drivers to C:\\PulseBackup\\DriversBackup... && dism /online /export-driver /destination:\\\"C:\\PulseBackup\\DriversBackup\\\""',
    "driver_restore": 'start cmd /k "if not exist C:\\PulseBackup\\DriversBackup (echo Backup folder C:\\PulseBackup\\DriversBackup not found! && pause) else (echo Importing drivers from C:\\PulseBackup\\DriversBackup... && pnputil /add-driver \\\"C:\\PulseBackup\\DriversBackup\\*.inf\\\" /subdirs /install)"',
    "user_netplwiz": "start netplwiz.exe",
    "create_godmode": 'start powershell -Command "New-Item -ItemType Directory -Path \'$home\\Desktop\\GodMode.{ED7BA470-8E54-465E-825C-99712043E01C}\' -Force"',
    "net_scan_subnet": "start cmd /k arp -a",
    "net_recycle_adapters": 'start powershell -NoExit -Command "Get-NetAdapter | Restart-NetAdapter"',
    "net_enable_rdp": 'start powershell -NoExit -Command "Set-ItemProperty -Path \'HKLM:\\System\\CurrentControlSet\\Control\\Terminal Server\' -Name \'fDenyTSConnections\' -Value 0; Enable-NetFirewallRule -DisplayGroup \'Remote Desktop\'"',
    "disk_trim_ssd": "start defrag C: /L",
    "disk_defrag": "start defrag C: /O",
    "disk_chkdsk": "start cmd /k chkdsk C: /f /r",
    "disk_heaviest_files": 'start powershell -NoExit -Command "Write-Host \'Scanning drive C: for the 10 heaviest files (this may take a minute)...\'; Get-ChildItem -Path C:\\ -File -Recurse -ErrorAction SilentlyContinue | Sort-Object Length -Descending | Select-Object -First 10 | Format-Table @{Label=\'File Name\';Expression={$_.Name}}, @{Label=\'Size (MB)\';Expression={[Math]::Round($_.Length/1MB, 2)}}, @{Label=\'Folder\';Expression={$_.DirectoryName}}"',
    "restart_tally": 'start cmd /k "net stop \'Tally-Gateway-Server\' && net start \'Tally-Gateway-Server\'"',
    "purge_temp_cache": 'start powershell -NoExit -Command "Remove-Item -Path \'C:\\Windows\\Temp\\*\' -Recurse -Force -ErrorAction SilentlyContinue; Remove-Item -Path \'C:\\Users\\*\\AppData\\Local\\Temp\\*\' -Recurse -Force -ErrorAction SilentlyContinue; Remove-Item -Path \'C:\\Windows\\Prefetch\\*\' -Recurse -Force -ErrorAction SilentlyContinue"',
    "explorer_restart": 'start cmd /k "taskkill /f /im explorer.exe && start explorer.exe"',
    "icon_cache_rebuild": 'start cmd /k "taskkill /f /im explorer.exe && del /a /q /f %localappdata%\\IconCache.db && start explorer.exe"',
    
    # Windows Updates Control Commands
    "stop_updates": 'start powershell -NoExit -Command "Write-Host \'Stopping and disabling Windows Update services...\'; Stop-Service -Name wuauserv, bits, UsoSvc -Force; Set-Service -Name wuauserv -StartupType Disabled; Set-Service -Name bits -StartupType Disabled; Set-Service -Name UsoSvc -StartupType Disabled; reg add \\"HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\WindowsUpdate\\AU\\" /v NoAutoUpdate /t REG_DWORD /d 1 /f; reg add \\"HKLM\\SYSTEM\\CurrentControlSet\\Services\\WaaSMedicSvc\\" /v Start /t REG_DWORD /d 4 /f; Write-Host \'Windows Updates have been fully disabled.\'"',
    "resume_updates": 'start powershell -NoExit -Command "Write-Host \'Enabling and restarting Windows Update services...\'; reg delete \\"HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\WindowsUpdate\\AU\\" /v NoAutoUpdate /f; reg add \\"HKLM\\SYSTEM\\CurrentControlSet\\Services\\WaaSMedicSvc\\" /v Start /t REG_DWORD /d 3 /f; Set-Service -Name wuauserv -StartupType Manual; Set-Service -Name bits -StartupType Manual; Set-Service -Name UsoSvc -StartupType Manual; Start-Service -Name wuauserv, bits, UsoSvc; Write-Host \'Windows Updates have been enabled and restarted.\'"',
    "security_only_updates": 'start powershell -NoExit -Command "Write-Host \'Configuring Windows Update for Security Patches Only...\'; reg add \\"HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\WindowsUpdate\\" /v ExcludeWUDriversInQualityUpdate /t REG_DWORD /d 1 /f; reg add \\"HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\WindowsUpdate\\" /v DeferFeatureUpdates /t REG_DWORD /d 1 /f; reg add \\"HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\WindowsUpdate\\" /v DeferFeatureUpdatesPeriodInDays /t REG_DWORD /d 365 /f; reg add \\"HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\WindowsUpdate\\" /v DeferQualityUpdates /t REG_DWORD /d 1 /f; reg add \\"HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\WindowsUpdate\\" /v DeferQualityUpdatesPeriodInDays /t REG_DWORD /d 4 /f; reg delete \\"HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\WindowsUpdate\\AU\\" /v NoAutoUpdate /f; reg add \\"HKLM\\SYSTEM\\CurrentControlSet\\Services\\WaaSMedicSvc\\" /v Start /t REG_DWORD /d 3 /f; Set-Service -Name wuauserv -StartupType Manual; Set-Service -Name bits -StartupType Manual; Set-Service -Name UsoSvc -StartupType Manual; Start-Service -Name wuauserv, bits, UsoSvc; Write-Host \'Windows Update configured for Security Updates Only (Features deferred 365 days, drivers disabled, updates enabled).\'"'
}

class PythonAdminServer(BaseHTTPRequestHandler):
    def send_cors_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Access-Control-Allow-Private-Network', 'true')

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_cors_headers()
        self.end_headers()

    def do_GET(self):
        # 1. API Endpoint: Status Check
        if self.path == '/api/status':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_cors_headers()
            self.end_headers()
            
            uptime_ms = ctypes.windll.kernel32.GetTickCount64()
            uptime_sec = uptime_ms / 1000.0
            
            status_data = {
                "status": "online",
                "isAdmin": is_admin(),
                "hostname": socket.gethostname(),
                "uptime": uptime_sec,
                "osName": OS_NAME
            }
            self.wfile.write(json.dumps(status_data).encode('utf-8'))
            return

        # 2. API Endpoint: Folder Browser Dialog
        elif self.path == '/api/browse':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_cors_headers()
            self.end_headers()
            
            script = """
            Add-Type -AssemblyName System.Windows.Forms
            $f = New-Object System.Windows.Forms.FolderBrowserDialog
            $f.Description = 'Select directory'
            $f.ShowNewFolderButton = $true
            $w = New-Object System.Windows.Forms.Form
            $w.TopMost = $true
            if ($f.ShowDialog($w) -eq 'OK') {
                Write-Output $f.SelectedPath
            }
            """
            try:
                out = subprocess.check_output(
                    ['powershell', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-Command', script],
                    text=True
                ).strip()
                self.wfile.write(json.dumps({"success": True, "path": out}).encode('utf-8'))
            except Exception as e:
                self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
            return

        # 2.1 API Endpoint: File Browser Dialog
        elif self.path == '/api/browse-file':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_cors_headers()
            self.end_headers()
            
            script = """
            Add-Type -AssemblyName System.Windows.Forms
            $f = New-Object System.Windows.Forms.OpenFileDialog
            $f.Filter = "JSON Files (*.json)|*.json|All Files (*.*)|*.*"
            $f.Title = "Select Winget Apps JSON File"
            $w = New-Object System.Windows.Forms.Form
            $w.TopMost = $true
            if ($f.ShowDialog($w) -eq 'OK') {
                Write-Output $f.FileName
            }
            """
            try:
                out = subprocess.check_output(
                    ['powershell', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-Command', script],
                    text=True
                ).strip()
                self.wfile.write(json.dumps({"success": True, "path": out}).encode('utf-8'))
            except Exception as e:
                self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
            return

        # 2.5 API Endpoint: Get Disks and Partition Info
        elif self.path == '/api/diskinfo':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_cors_headers()
            self.end_headers()
            
            win_drives = []
            import string
            for letter in string.ascii_uppercase:
                if os.path.exists(f"{letter}:\\Windows\\System32\\utilman.exe"):
                    win_drives.append(letter)
            
            all_drives = []
            for letter in string.ascii_uppercase:
                if os.path.exists(f"{letter}:\\"):
                    all_drives.append(letter)
            
            disks = []
            try:
                cmd = ["powershell", "-Command", "Get-Disk | Select-Object Number, FriendlyName, PartitionStyle | ConvertTo-Json"]
                process = subprocess.run(cmd, capture_output=True, text=True)
                output = process.stdout.strip()
                if output:
                    data = json.loads(output)
                    if not isinstance(data, list):
                        data = [data]
                    for d in data:
                        num = d.get("Number")
                        name = d.get("FriendlyName") or "Disk"
                        style = d.get("PartitionStyle") or "MBR"
                        disks.append({"Number": num, "Name": name, "Style": style})
            except Exception:
                pass
                
            info = {
                "windowsDrives": win_drives,
                "allDrives": all_drives,
                "disks": disks
            }
            self.wfile.write(json.dumps(info).encode('utf-8'))
            return

        # 3. API Endpoint: Geolocation Proxy
        elif self.path == '/api/geoip':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_cors_headers()
            self.end_headers()
            
            urls = [
                ('https://freeipapi.com/api/json', 'freeipapi'),
                ('https://ipwho.is/', 'ipwhois'),
                ('https://ipapi.co/json/', 'ipapi')
            ]
            geo_data = {}
            for url, provider in urls:
                try:
                    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                    with urllib.request.urlopen(req, timeout=3) as res:
                        data = json.loads(res.read().decode('utf-8'))
                        if provider == 'freeipapi':
                            geo_data = data
                        elif provider == 'ipwhois':
                            geo_data = {
                                "countryName": data.get("country"),
                                "countryCode": data.get("country_code"),
                                "regionName": data.get("region"),
                                "cityName": data.get("city"),
                                "ipAddress": data.get("ip")
                            }
                        elif provider == 'ipapi':
                            geo_data = {
                                "countryName": data.get("country_name"),
                                "countryCode": data.get("country"),
                                "regionName": data.get("region"),
                                "cityName": data.get("city"),
                                "ipAddress": data.get("ip")
                            }
                        break  # Stop if successful
                except Exception:
                    continue
            self.wfile.write(json.dumps(geo_data).encode('utf-8'))
            return

        # Serve static files
        url_clean = self.path.split('?')[0]
        relative_path = 'index.html' if url_clean == '/' else url_clean.lstrip('/')
        
        file_path = os.path.join(PUBLIC_DIR, relative_path)
        
        # Directory traversal prevention
        normalized_public = os.path.abspath(PUBLIC_DIR)
        normalized_file = os.path.abspath(file_path)
        if not normalized_file.startswith(normalized_public):
            self.send_response(403)
            self.end_headers()
            self.wfile.write(b"Forbidden")
            return

        # Mime types mapping
        ext = os.path.splitext(file_path)[1].lower()
        mime_types = {
            ".html": "text/html",
            ".css": "text/css",
            ".js": "application/javascript",
            ".png": "image/png",
            ".ico": "image/x-icon",
            ".svg": "image/svg+xml"
        }
        content_type = mime_types.get(ext, "application/octet-stream")

        try:
            with open(file_path, 'rb') as f:
                content = f.read()
            self.send_response(200)
            self.send_header('Content-Type', content_type)
            self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
            self.send_cors_headers()
            self.end_headers()
            self.wfile.write(content)
        except Exception:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not Found")

    def do_POST(self):
        # 1. API Endpoint: Execute System Commands
        if self.path == '/api/execute':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            
            try:
                payload = json.loads(post_data)
                tool_key = payload.get("toolKey")
                app_id = payload.get("appId")
                
                # Special check for Print Management Console existence
                if tool_key == 'print_management':
                    windir = os.environ.get('SystemRoot', 'C:\\Windows')
                    sys32_path = os.path.join(windir, 'System32', 'printmanagement.msc')
                    sysnative_path = os.path.join(windir, 'Sysnative', 'printmanagement.msc')
                    if not os.path.exists(sys32_path) and not os.path.exists(sysnative_path):
                        self.send_response(400)
                        self.send_header('Content-Type', 'application/json')
                        self.send_cors_headers()
                        self.end_headers()
                        self.wfile.write(json.dumps({
                            "error": "Print Management Console is not installed on this Windows edition (Win 11 Pro/Enterprise only)."
                        }).encode('utf-8'))
                        return
                
                command = COMMANDS.get(tool_key)
                
                # Check for dynamic Robocopy command
                if tool_key == 'run_robocopy':
                    src = payload.get("sourcePath")
                    tgt = payload.get("targetPath")
                    command = f'start cmd /k robocopy "{src}" "{tgt}" /MIR /MT:8'
                
                # Check for dynamic Winget custom installer
                if tool_key == 'winget_install':
                    if app_id and (app_id.isalnum() or '.' in app_id or '-' in app_id):
                        command = f'winget install --id {app_id} --silent --accept-package-agreements --accept-source-agreements'
                    else:
                        self.send_response(400)
                        self.send_header('Content-Type', 'application/json')
                        self.send_cors_headers()
                        self.end_headers()
                        self.wfile.write(json.dumps({"error": "Invalid Application ID"}).encode('utf-8'))
                        return
                
                # Check for Office 2021 Silent Installer XML Script
                if tool_key == 'install_office_2021':
                    import tempfile
                    ps_path = os.path.join(tempfile.gettempdir(), 'install_office_2021.ps1')
                    script = """$ErrorActionPreference = 'Stop'
$odtUrl = 'https://download.microsoft.com/download/6c1eeb25-cf8b-41d9-8d0d-cc1dbc032140/officedeploymenttool_20026-20112.exe'
$odtDir = 'C:\\Users\\Public\\Documents\\ODT2021'
if (!(Test-Path $odtDir)) {
    New-Item -ItemType Directory -Path $odtDir -Force
}
$odtExe = Join-Path $odtDir 'odt.exe'
Invoke-WebRequest -Uri $odtUrl -OutFile $odtExe
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
  <Property Name="FORCEAPPSHUTDOWN" Value="TRUE" />
</Configuration>
'@
$xmlContent | Out-File -FilePath $configXml -Encoding utf8
Start-Process -FilePath "$odtDir\\setup.exe" -ArgumentList "/configure $configXml" -Wait
"""
                    with open(ps_path, 'w', encoding='utf-8') as f:
                        f.write(script)
                    command = f'start powershell -NoExit -ExecutionPolicy Bypass -File "{ps_path}"'
                
                # Check for Office 2024 Silent Installer XML Script
                if tool_key == 'install_office_2024':
                    import tempfile
                    ps_path = os.path.join(tempfile.gettempdir(), 'install_office_2024.ps1')
                    script = """$ErrorActionPreference = 'Stop'
$odtUrl = 'https://download.microsoft.com/download/6c1eeb25-cf8b-41d9-8d0d-cc1dbc032140/officedeploymenttool_20026-20112.exe'
$odtDir = 'C:\\Users\\Public\\Documents\\ODT2024'
if (!(Test-Path $odtDir)) {
    New-Item -ItemType Directory -Path $odtDir -Force
}
$odtExe = Join-Path $odtDir 'odt.exe'
Invoke-WebRequest -Uri $odtUrl -OutFile $odtExe
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
Start-Process -FilePath "$odtDir\\setup.exe" -ArgumentList "/configure $configXml" -Wait
"""
                    with open(ps_path, 'w', encoding='utf-8') as f:
                        f.write(script)
                    command = f'start powershell -NoExit -ExecutionPolicy Bypass -File "{ps_path}"'

                # Disk Security and Boot recovery commands
                if tool_key == 'apply_utilman_bypass':
                    win_drive = payload.get("winDrive", "C")
                    command = f'takeown /f "{win_drive}:\\Windows\\System32\\utilman.exe" && icacls "{win_drive}:\\Windows\\System32\\utilman.exe" /grant administrators:F && ren "{win_drive}:\\Windows\\System32\\utilman.exe" utilman.exe.bak && copy "{win_drive}:\\Windows\\System32\\cmd.exe" "{win_drive}:\\Windows\\System32\\utilman.exe"'
                    
                if tool_key == 'restore_utilman':
                    win_drive = payload.get("winDrive", "C")
                    command = f'del /f /q "{win_drive}:\\Windows\\System32\\utilman.exe" && ren "{win_drive}:\\Windows\\System32\\utilman.exe.bak" utilman.exe'
                    
                if tool_key == 'convert_fat32_to_ntfs':
                    drive_letter = payload.get("driveLetter", "D")
                    command = f'start cmd /k convert {drive_letter}: /FS:NTFS'
                    
                if tool_key == 'convert_mbr_to_gpt':
                    disk_num = payload.get("diskNum", "0")
                    command = f'start cmd /k mbr2gpt /convert /disk:{disk_num} /allowFullOS'
                    
                if tool_key == 'fixmbr':
                    command = 'start cmd /k bootrec /fixmbr'
                    
                if tool_key == 'fixboot':
                    command = 'start cmd /k bootrec /fixboot'
                    
                if tool_key == 'rebuildbcd':
                    command = 'start cmd /k bootrec /rebuildbcd'
                    
                if tool_key == 'bcdboot_repair':
                    win_drive = payload.get("winDrive", "C")
                    boot_drive = payload.get("bootDrive", "S")
                    command = f'start cmd /k bcdboot {win_drive}:\\Windows /s {boot_drive}: /f ALL'
                    
                if tool_key == 'wipe_disk':
                    fix_type = payload.get("fixType")
                    disk_num = payload.get("diskNum", "0")
                    import tempfile
                    script_content = f"select disk {disk_num}\nclean\n"
                    if fix_type == "wipe_gpt":
                        script_content += "convert gpt\n"
                    elif fix_type == "wipe_mbr" or fix_type == "wipe_basic":
                        script_content += "convert mbr\n"
                    
                    fd, path = tempfile.mkstemp(suffix=".txt", prefix="diskpart_")
                    with os.open(fd, os.O_WRONLY | os.O_CREAT) as f:
                        os.write(f, script_content.encode('utf-8'))
                    command = f'start cmd /k diskpart /s "{path}"'
                    
                if tool_key == 'chkdsk_repair':
                    drive_letter = payload.get("driveLetter", "C")
                    command = f'start cmd /k chkdsk {drive_letter}: /f'
                    
                if tool_key == 'winre_enable':
                    command = 'start cmd /k reagentc /enable'
                    
                if tool_key == 'winre_status':
                    command = 'start cmd /k reagentc /info'
                    
                if tool_key == 'safemode_on':
                    command = 'start cmd /k "bcdedit /set {default} safeboot minimal"'
                    
                if tool_key == 'safemode_off':
                    command = 'start cmd /k "bcdedit /deletevalue {default} safeboot"'

                # Migration and backup tools
                if tool_key == 'run_migration_backup':
                    tgt = payload.get("targetPath")
                    final_path = tgt.strip() if tgt else "C:\\PulseBackup"
                    if not os.path.exists(final_path):
                        try:
                            os.makedirs(final_path, exist_ok=True)
                        except Exception:
                            pass
                    command = f'start cmd /k powershell -NoExit -Command "$dest = \'{final_path}\'; $folders = @(\'Desktop\', \'Documents\', \'Downloads\', \'Pictures\', \'Music\', \'Videos\'); foreach ($f in $folders) {{ $src = Join-Path $env:USERPROFILE $f; $tgt = Join-Path $dest $f; if (Test-Path $src) {{ robocopy $src $tgt /E /MT:8 /R:1 /W:1 /XJD }} }}"'

                if tool_key == 'winget_export':
                    tgt = payload.get("targetPath")
                    export_path = "C:\\PulseBackup\\winget_apps.json"
                    if tgt:
                        export_path = os.path.join(tgt, 'winget_apps.json')
                    dir_path = os.path.dirname(export_path)
                    if not os.path.exists(dir_path):
                        try:
                            os.makedirs(dir_path, exist_ok=True)
                        except Exception:
                            pass
                    command = f'start cmd /k winget export -o "{export_path}" --accept-source-agreements'

                if tool_key == 'winget_import':
                    import_file = payload.get("filePath")
                    if not import_file:
                        self.send_response(400)
                        self.send_header('Content-Type', 'application/json')
                        self.send_cors_headers()
                        self.end_headers()
                        self.wfile.write(json.dumps({"error": "File path is required"}).encode('utf-8'))
                        return
                    command = f'start cmd /k winget import -i "{import_file}" --accept-package-agreements --accept-source-agreements'

                if tool_key == 'change_windows_edition':
                    product_key = payload.get("productKey")
                    if product_key and all(c in "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ-" for c in product_key.upper()):
                        command = f'start changepk.exe /ProductKey {product_key}'
                    else:
                        self.send_response(400)
                        self.send_header('Content-Type', 'application/json')
                        self.send_cors_headers()
                        self.end_headers()
                        self.wfile.write(json.dumps({"error": "Invalid Product Key format"}).encode('utf-8'))
                        return

                if not command:
                    self.send_response(400)
                    self.send_header('Content-Type', 'application/json')
                    self.send_cors_headers()
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": "Unknown tool key"}).encode('utf-8'))
                    return
                
                # Decouple stdout/stderr streams for GUI/start commands to prevent hangs
                if "start " in command.lower():
                    exec_cmd = f"{command} >nul 2>&1"
                    subprocess.Popen(exec_cmd, shell=True)
                    
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.send_cors_headers()
                    self.end_headers()
                    self.wfile.write(json.dumps({"success": True, "output": "Launched process successfully."}).encode('utf-8'))
                else:
                    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                    stdout, stderr = process.communicate()
                    
                    if process.returncode == 0:
                        self.send_response(200)
                        self.send_header('Content-Type', 'application/json')
                        self.send_cors_headers()
                        self.end_headers()
                        self.wfile.write(json.dumps({"success": True, "output": stdout}).encode('utf-8'))
                    else:
                        self.send_response(500)
                        self.send_header('Content-Type', 'application/json')
                        self.send_cors_headers()
                        self.end_headers()
                        
                        err_str = (stderr or "").lower()
                        if "access is denied" in err_str or "requires elevation" in err_str:
                            err_msg = "Permission denied. Ensure the server runs as Admin."
                        elif "cannot find" in err_str or "not recognized" in err_str:
                            err_msg = "Feature or tool not found on this Windows edition."
                        else:
                            err_msg = stderr or "System command failed."
                        
                        self.wfile.write(json.dumps({"error": err_msg, "details": stderr}).encode('utf-8'))
            
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
            return

        # 2. API Endpoint: Self-Destruct Server
        elif self.path == '/api/self-destruct':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({"success": True, "message": "Initiating self-destruct"}).encode('utf-8'))
            
            try:
                # Get current executable/script folder and parent folder
                current_dir = os.path.abspath(os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(__file__))
                parent_dir = os.path.dirname(current_dir)
                folder_name = os.path.basename(current_dir)
                
                system_folders = ["desktop", "downloads", "documents", "my documents", "users", "windows", "system32"]
                
                if folder_name.lower() in system_folders or len(folder_name) <= 3:
                    # If run from Desktop or root direct folders, only delete specific app files and zip files
                    cleanup_cmd = (
                        f'timeout /t 2 /nobreak && '
                        f'cd /d "{current_dir}" && '
                        f'del /f /q /s main.exe main.old PrintPulse.exe server.js server.py gui_app.py '
                        f'Start-Admin-Server.bat index.html app.js styles.css logo.png main.spec PrintPulse.spec '
                        f'build_exe.bat *puls*.zip *pulse*.zip main.zip ..\\*puls*.zip ..\\*pulse*.zip ..\\main.zip && '
                        f'rmdir /s /q dist build __pycache__'
                    )
                else:
                    # If run inside an extracted subfolder (like 'prrinter tool'), delete the whole folder and zip files on parent
                    cleanup_cmd = (
                        f'timeout /t 2 /nobreak && '
                        f'cd /d "{parent_dir}" && '
                        f'rmdir /s /q "{current_dir}" && '
                        f'del /f /q *puls*.zip *pulse*.zip main.zip'
                    )
                
                subprocess.Popen(['cmd.exe', '/c', cleanup_cmd])
            except Exception as e:
                print(f"Self-destruct prep failed: {e}")
            
            # Kill process after small delay
            def shutdown():
                time.sleep(0.5)
                os._exit(0)
            import threading
            threading.Thread(target=shutdown).start()
            return

# Main Execution Entrypoint
if __name__ == "__main__":
    # Spawn background watcher process for auto-cleanup on exit
    try:
        current_dir = os.path.abspath(os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(__file__))
        parent_dir = os.path.dirname(current_dir)
        folder_name = os.path.basename(current_dir)
        
        if getattr(sys, 'frozen', False):
            watcher_args = [sys.executable, "--watcher", str(os.getpid()), current_dir, parent_dir, folder_name]
        else:
            watcher_args = [sys.executable, __file__, "--watcher", str(os.getpid()), current_dir, parent_dir, folder_name]
            
        # 0x00000008 is DETACHED_PROCESS flag in Windows
        subprocess.Popen(watcher_args, creationflags=0x00000008)
    except Exception as e:
        print(f"Failed to spawn background watcher: {e}")

    # Free port 3000
    free_port(PORT)

    # Start HTTP Web Server
    server_address = ('', PORT)
    httpd = HTTPServer(server_address, PythonAdminServer)
    
    print("======================================================================")
    print("            Starting PrintPulse AI Python Admin Web Server            ")
    print("======================================================================")
    print(f"Server is launching on: http://localhost:{PORT}")
    print("One-click repairs are now active through this terminal socket.")
    print("Keep this window open while using the web application dashboard.")
    print("======================================================================")

    # Open localhost in browser
    webbrowser.open(f'http://localhost:{PORT}')

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        httpd.server_close()
