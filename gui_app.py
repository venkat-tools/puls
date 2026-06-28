import os
import sys
import ctypes
import socket
import platform
import subprocess
import threading
import time
import urllib.request
import json
from PIL import Image
import customtkinter as ctk
import psutil

# Auto-Elevation to Administrator
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if not is_admin():
    # Re-launch with administrator privileges
    try:
        # sys.executable contains the path to python.exe or the compiled exe
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    except Exception as e:
        print(f"Failed to elevate: {e}")
    sys.exit(0)

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

# Configure CustomTkinter appearance
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("green")

class PrintPulseApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Window configuration
        self.title("VenkatPulse AI // Windows Repair & Optimization Suite")
        self.geometry("1100x680")
        self.minsize(950, 600)
        
        # System variables
        self.DEFAULT_GEMINI_KEY = "AQ.Ab8RN6LR7pTxNb8J3H4ffw4MS_wdIt3yL53of1EOauvrlylhrA"
        self.gemini_key = self.load_gemini_key()
        self.telemetry_running = True
        
        # Grid layout (1 row, 2 columns)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        # Load logo image
        self.logo_image = None
        logo_path = resource_path("logo.png")
        if os.path.exists(logo_path):
            try:
                self.logo_image = ctk.CTkImage(
                    light_image=Image.open(logo_path),
                    dark_image=Image.open(logo_path),
                    size=(180, 70)
                )
            except Exception as e:
                print(f"Error loading logo: {e}")
                
        # 1. Create Left Sidebar
        self.sidebar_frame = ctk.CTkFrame(self, corner_radius=0, width=220)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(10, weight=1)
        
        # Sidebar Logo or Text
        if self.logo_image:
            self.logo_label = ctk.CTkLabel(self.sidebar_frame, image=self.logo_image, text="")
            self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        else:
            self.logo_title = ctk.CTkLabel(
                self.sidebar_frame, 
                text="VenkatPulse AI", 
                font=ctk.CTkFont(size=20, weight="bold")
            )
            self.logo_title.grid(row=0, column=0, padx=20, pady=(20, 5))
            
        self.logo_sub = ctk.CTkLabel(
            self.sidebar_frame, 
            text="Repair & Debloat Suite", 
            text_color="#10b981",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        self.logo_sub.grid(row=1, column=0, padx=20, pady=(0, 20))
        
        # Sidebar navigation buttons
        self.nav_buttons = {}
        nav_items = [
            ("Dashboard", "📊 Dashboard"),
            ("Repairs", "🔧 System Repairs"),
            ("Debloater", "🧹 Win Debloater"),
            ("AppDownloader", "📥 App Downloader"),
            ("OfficeActivation", "🔑 Office & Activation"),
            ("AdminTools", "🛠️ Admin Tools"),
            ("AiAssistant", "💬 AI Assistant")
        ]
        
        for idx, (key, text) in enumerate(nav_items):
            btn = ctk.CTkButton(
                self.sidebar_frame,
                text=text,
                corner_radius=8,
                height=40,
                border_spacing=10,
                fg_color="transparent",
                text_color=("gray10", "gray90"),
                hover_color=("gray70", "gray30"),
                anchor="w",
                font=ctk.CTkFont(size=13, weight="bold"),
                command=lambda k=key: self.select_frame(k)
            )
            btn.grid(row=idx+2, column=0, padx=15, pady=5, sticky="ew")
            self.nav_buttons[key] = btn
            
        # Admin elevation status in sidebar
        self.admin_badge = ctk.CTkLabel(
            self.sidebar_frame,
            text="🛡️ ADMIN ELEVATED",
            fg_color="#065f46",
            text_color="#34d399",
            corner_radius=4,
            height=26,
            font=ctk.CTkFont(size=10, weight="bold")
        )
        self.admin_badge.grid(row=11, column=0, padx=15, pady=20, sticky="s")
        
        # 2. Create right-side main container frames
        self.frames = {}
        
        # Initialize all views/frames
        self.create_dashboard_frame()
        self.create_repairs_frame()
        self.create_debloater_frame()
        self.create_app_downloader_frame()
        self.create_office_activation_frame()
        self.create_admin_tools_frame()
        self.create_ai_assistant_frame()
        
        # Show Dashboard initially
        self.select_frame("Dashboard")
        
        # Start Background Thread for telemetry
        self.telemetry_thread = threading.Thread(target=self.update_telemetry_loop, daemon=True)
        self.telemetry_thread.start()

    def select_frame(self, name):
        # Reset navigation button colors
        for key, btn in self.nav_buttons.items():
            if key == name:
                btn.configure(fg_color=["#10b981", "#059669"], text_color="white")
            else:
                btn.configure(fg_color="transparent", text_color=("gray10", "gray90"))
                
        # Hide all frames and show selected
        for frame in self.frames.values():
            frame.grid_forget()
            
        self.frames[name].grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

    # Helper function to execute local command and show feedback
    def run_cmd(self, cmd_str, title="Executing Action", check_output=False):
        def worker():
            try:
                # Decouple cmd starts to avoid blocking GUI
                process = subprocess.Popen(
                    cmd_str,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                # If command is instant/non-blocking, wait for it
                if "start " not in cmd_str:
                    stdout, stderr = process.communicate()
                    if process.returncode == 0:
                        self.show_toast(f"✅ Success: {title}")
                    else:
                        self.show_toast(f"❌ Failed: {title}\n{stderr.strip()}")
                else:
                    self.show_toast(f"🚀 Launched: {title}")
            except Exception as e:
                self.show_toast(f"❌ Error: {e}")
                
        threading.Thread(target=worker, daemon=True).start()

    # Dynamic notifications / toast message box
    def show_toast(self, message):
        self.after(0, lambda: self.toast_alert(message))
        
    def toast_alert(self, msg):
        # Create a small floating window or show in status label
        toast = ctk.CTkToplevel(self)
        toast.title("Alert")
        toast.geometry("380x150")
        toast.resizable(False, False)
        toast.attributes("-topmost", True)
        
        label = ctk.CTkLabel(toast, text=msg, wraplength=340, font=ctk.CTkFont(size=12))
        label.pack(expand=True, fill="both", padx=20, pady=20)
        
        btn = ctk.CTkButton(toast, text="OK", width=80, command=toast.destroy)
        btn.pack(pady=(0, 15))

    # --- TELEMETRY GATHERING LOOP ---
    def update_telemetry_loop(self):
        # Fetch static metrics once
        os_ver = f"{platform.system()} {platform.release()}"
        try:
            # Query Caption via PowerShell
            caption = subprocess.check_output(
                'powershell -Command "(Get-CimInstance Win32_OperatingSystem).Caption"',
                shell=True,
                text=True
            ).strip()
            if caption:
                os_ver = caption
        except:
            pass
            
        device_name = socket.gethostname()
        
        # Set static fields in UI
        self.after(0, lambda: self.os_val.configure(text=os_ver))
        self.after(0, lambda: self.dev_val.configure(text=device_name))
        
        # Loop for dynamic stats
        while self.telemetry_running:
            try:
                # CPU load
                cpu_load = psutil.cpu_percent(interval=None)
                
                # RAM usage
                ram = psutil.virtual_memory()
                ram_used_pct = ram.percent
                
                # Disk usage
                disk = psutil.disk_usage('C:\\')
                disk_used_pct = disk.percent
                
                # System Uptime
                uptime_sec = time.time() - psutil.boot_time()
                days = int(uptime_sec // 86400)
                hours = int((uptime_sec % 86400) // 3600)
                minutes = int((uptime_sec % 3600) // 60)
                
                if days > 0:
                    uptime_str = f"{days}d {hours}h {minutes}m"
                else:
                    uptime_str = f"{hours}h {minutes}m"
                    
                # Update UI
                self.after(0, lambda: self.cpu_bar.set(cpu_load / 100))
                self.after(0, lambda: self.cpu_lbl.configure(text=f"CPU Load: {int(cpu_load)}%"))
                
                self.after(0, lambda: self.ram_bar.set(ram_used_pct / 100))
                self.after(0, lambda: self.ram_lbl.configure(text=f"RAM Usage: {int(ram_used_pct)}%"))
                
                self.after(0, lambda: self.disk_bar.set(disk_used_pct / 100))
                self.after(0, lambda: self.disk_lbl.configure(text=f"Disk (C:): {int(disk_used_pct)}%"))
                
                self.after(0, lambda: self.upt_val.configure(text=uptime_str))
                
            except Exception as e:
                print(f"Telemetry error: {e}")
            time.sleep(1.5)

    # --- 1. DASHBOARD FRAME ---
    def create_dashboard_frame(self):
        frame = ctk.CTkFrame(self, fg_color="transparent")
        self.frames["Dashboard"] = frame
        
        # Grid configuration
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=1)
        
        # Hero Welcome Header
        welcome_lbl = ctk.CTkLabel(
            frame, 
            text="Welcome to VenkatPulse AI Suite", 
            font=ctk.CTkFont(size=24, weight="bold"),
            anchor="w"
        )
        welcome_lbl.grid(row=0, column=0, columnspan=2, padx=10, pady=(10, 5), sticky="w")
        
        subtitle_lbl = ctk.CTkLabel(
            frame,
            text="Premium local Windows diagnostics, repair, and debloating interface.",
            text_color="gray",
            font=ctk.CTkFont(size=13),
            anchor="w"
        )
        subtitle_lbl.grid(row=1, column=0, columnspan=2, padx=10, pady=(0, 20), sticky="w")
        
        # Left Panel: Windows System Health Card
        health_card = ctk.CTkFrame(frame, corner_radius=12)
        health_card.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
        health_card.grid_columnconfigure(0, weight=1)
        
        card_title = ctk.CTkLabel(
            health_card,
            text="Windows System Health",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        card_title.grid(row=0, column=0, padx=20, pady=(15, 15), sticky="w")
        
        # Spec Labels & Dynamic values
        labels = [
            ("OS Version:", "os_val"),
            ("Device Name:", "dev_val"),
            ("System Uptime:", "upt_val")
        ]
        
        for idx, (label_text, val_attr) in enumerate(labels):
            lbl = ctk.CTkLabel(health_card, text=label_text, text_color="gray", font=ctk.CTkFont(size=12))
            lbl.grid(row=idx*2+1, column=0, padx=20, pady=(5, 0), sticky="w")
            
            val = ctk.CTkLabel(health_card, text="Fetching...", font=ctk.CTkFont(size=14, weight="bold"))
            val.grid(row=idx*2+2, column=0, padx=20, pady=(0, 15), sticky="w")
            setattr(self, val_attr, val)
            
        # Quick Scan buttons in Health Card
        btn_container = ctk.CTkFrame(health_card, fg_color="transparent")
        btn_container.grid(row=7, column=0, padx=20, pady=(20, 20), sticky="ew")
        
        quick_repair_btn = ctk.CTkButton(
            btn_container,
            text="Run Quick Repair",
            fg_color="#059669",
            hover_color="#047857",
            font=ctk.CTkFont(weight="bold"),
            command=lambda: self.run_cmd(
                'powershell -Command "Stop-Service -Name Spooler -Force; Remove-Item -Path \'C:\\Windows\\System32\\spool\\PRINTERS\\*\' -Force -Recurse; Start-Service -Name Spooler"',
                "Quick Repair & Queue Cleanup"
            )
        )
        quick_repair_btn.pack(side="left", padx=(0, 10), fill="x", expand=True)
        
        # Right Panel: Resource Monitor Card
        resource_card = ctk.CTkFrame(frame, corner_radius=12)
        resource_card.grid(row=2, column=1, padx=10, pady=10, sticky="nsew")
        resource_card.grid_columnconfigure(0, weight=1)
        
        res_title = ctk.CTkLabel(
            resource_card,
            text="System Resource Monitor",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        res_title.grid(row=0, column=0, padx=20, pady=(15, 10), sticky="w")
        
        # Progress Bars for Resources
        self.cpu_lbl = ctk.CTkLabel(resource_card, text="CPU Load: --%", font=ctk.CTkFont(size=12))
        self.cpu_lbl.grid(row=1, column=0, padx=20, pady=(10, 0), sticky="w")
        self.cpu_bar = ctk.CTkProgressBar(resource_card, progress_color="#10b981")
        self.cpu_bar.set(0)
        self.cpu_bar.grid(row=2, column=0, padx=20, pady=(5, 15), sticky="ew")
        
        self.ram_lbl = ctk.CTkLabel(resource_card, text="RAM Usage: --%", font=ctk.CTkFont(size=12))
        self.ram_lbl.grid(row=3, column=0, padx=20, pady=(10, 0), sticky="w")
        self.ram_bar = ctk.CTkProgressBar(resource_card, progress_color="#10b981")
        self.ram_bar.set(0)
        self.ram_bar.grid(row=4, column=0, padx=20, pady=(5, 15), sticky="ew")
        
        self.disk_lbl = ctk.CTkLabel(resource_card, text="Disk (C:): --%", font=ctk.CTkFont(size=12))
        self.disk_lbl.grid(row=5, column=0, padx=20, pady=(10, 0), sticky="w")
        self.disk_bar = ctk.CTkProgressBar(resource_card, progress_color="#10b981")
        self.disk_bar.set(0)
        self.disk_bar.grid(row=6, column=0, padx=20, pady=(5, 15), sticky="ew")
        
        # Tips Label
        tips_card = ctk.CTkFrame(frame, corner_radius=12, fg_color=("#e6f4ea", "#064e3b"))
        tips_card.grid(row=3, column=0, columnspan=2, padx=10, pady=15, sticky="ew")
        
        tip_lbl = ctk.CTkLabel(
            tips_card,
            text="🛡️ Tip: Before running registry modifications or system repairs, always create a System Restore Point.",
            text_color=("#137333", "#34d399"),
            font=ctk.CTkFont(size=12, weight="bold")
        )
        tip_lbl.pack(padx=20, pady=15)

    # --- 2. SYSTEM REPAIRS FRAME ---
    def create_repairs_frame(self):
        frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.frames["Repairs"] = frame
        
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=1)
        
        title = ctk.CTkLabel(frame, text="System & Printer Repairs", font=ctk.CTkFont(size=20, weight="bold"))
        title.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="w")
        
        desc = ctk.CTkLabel(frame, text="Fix common spooler, registry permissions, and printer configuration issues.", text_color="gray")
        desc.grid(row=1, column=0, columnspan=2, padx=10, pady=(0, 20), sticky="w")
        
        # Group 1: Print Spooler Fixes
        g1 = ctk.CTkFrame(frame, corner_radius=10)
        g1.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
        g1.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(g1, text="Print Spooler Services", font=ctk.CTkFont(size=15, weight="bold")).grid(row=0, column=0, padx=15, pady=15, sticky="w")
        
        ctk.CTkButton(
            g1, 
            text="Restart Spooler Service", 
            command=lambda: self.run_cmd('powershell -Command "Restart-Service -Name Spooler -Force"', "Restart Spooler")
        ).grid(row=1, column=0, padx=15, pady=8, sticky="ew")
        
        ctk.CTkButton(
            g1, 
            text="Clear Print Queue Directory", 
            command=lambda: self.run_cmd('powershell -Command "Stop-Service -Name Spooler -Force; Remove-Item -Path \'C:\\Windows\\System32\\spool\\PRINTERS\\*\' -Force -Recurse; Start-Service -Name Spooler"', "Clear Queue")
        ).grid(row=2, column=0, padx=15, pady=8, sticky="ew")
        
        # Group 2: Point & Print / RPC Fixes
        g2 = ctk.CTkFrame(frame, corner_radius=10)
        g2.grid(row=2, column=1, padx=10, pady=10, sticky="nsew")
        g2.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(g2, text="Windows Registry Patches", font=ctk.CTkFont(size=15, weight="bold")).grid(row=0, column=0, padx=15, pady=15, sticky="w")
        
        ctk.CTkButton(
            g2, 
            text="Fix Point & Print Admin Block", 
            command=lambda: self.run_cmd('reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows NT\\Printers\\PointAndPrint" /v RestrictDriverInstallationToAdministrators /t REG_DWORD /d 0 /f && powershell -Command "Restart-Service -Name Spooler -Force"', "Point & Print Fix")
        ).grid(row=1, column=0, padx=15, pady=8, sticky="ew")
        
        ctk.CTkButton(
            g2, 
            text="Apply RPC named pipe fixes", 
            command=lambda: self.run_cmd('reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows NT\\Printers\\RPC" /v RpcOverNamedPipes /t REG_DWORD /d 1 /f && reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows NT\\Printers\\RPC" /v RpcUseNamedPipeShare /t REG_DWORD /d 1 /f && reg add "HKLM\\System\\CurrentControlSet\\Control\\Print" /v RpcAuthnLevelPrivacyEnabled /t REG_DWORD /d 0 /f && powershell -Command "Restart-Service -Name Spooler -Force"', "RPC Fixes")
        ).grid(row=2, column=0, padx=15, pady=8, sticky="ew")
        
        # Group 3: Network & Sharing
        g3 = ctk.CTkFrame(frame, corner_radius=10)
        g3.grid(row=3, column=0, padx=10, pady=10, sticky="nsew")
        g3.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(g3, text="Network & Protocol Sharing", font=ctk.CTkFont(size=15, weight="bold")).grid(row=0, column=0, padx=15, pady=15, sticky="w")
        
        ctk.CTkButton(
            g3, 
            text="Enable Network Discovery", 
            command=lambda: self.run_cmd('netsh advfirewall firewall set rule group="Network Discovery" new enable=Yes', "Network Discovery")
        ).grid(row=1, column=0, padx=15, pady=8, sticky="ew")
        
        ctk.CTkButton(
            g3, 
            text="Enable SMBv1 Protocol (Legacy)", 
            command=lambda: self.run_cmd('start powershell -NoExit -Command "Enable-WindowsOptionalFeature -Online -FeatureName \'SMB1Protocol\' -All -NoRestart"', "Enable SMBv1")
        ).grid(row=2, column=0, padx=15, pady=8, sticky="ew")
        
        ctk.CTkButton(
            g3, 
            text="Disable SMBv1 Protocol (Secure)", 
            command=lambda: self.run_cmd('start powershell -NoExit -Command "Disable-WindowsOptionalFeature -Online -FeatureName \'SMB1Protocol\' -Force -NoRestart"', "Disable SMBv1")
        ).grid(row=3, column=0, padx=15, pady=8, sticky="ew")

        # Group 4: Printer Migration
        g4 = ctk.CTkFrame(frame, corner_radius=10)
        g4.grid(row=3, column=1, padx=10, pady=10, sticky="nsew")
        g4.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(g4, text="Printer Migration Tool", font=ctk.CTkFont(size=15, weight="bold")).grid(row=0, column=0, padx=15, pady=15, sticky="w")
        
        ctk.CTkButton(
            g4, 
            text="Backup Installed Printers", 
            command=lambda: self.run_cmd('start cmd /k C:\\Windows\\System32\\Spool\\Tools\\PrintBrm.exe -b -f C:\\Users\\Public\\Documents\\PrinterBackup.printerExport', "Printer Backup")
        ).grid(row=1, column=0, padx=15, pady=8, sticky="ew")
        
        ctk.CTkButton(
            g4, 
            text="Restore Printer Backup", 
            command=lambda: self.run_cmd('start cmd /k C:\\Windows\\System32\\Spool\\Tools\\PrintBrm.exe -r -f C:\\Users\\Public\\Documents\\PrinterBackup.printerExport', "Printer Restore")
        ).grid(row=2, column=0, padx=15, pady=8, sticky="ew")

    # --- 3. WINDOWS DEBLOATER FRAME ---
    def create_debloater_frame(self):
        frame = ctk.CTkFrame(self, fg_color="transparent")
        self.frames["Debloater"] = frame
        
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=1)
        
        title = ctk.CTkLabel(frame, text="Windows Debloater & Privacy", font=ctk.CTkFont(size=20, weight="bold"))
        title.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="w")
        
        desc = ctk.CTkLabel(frame, text="Optimize system speed and protect telemetry privacy by disabling background bloat.", text_color="gray")
        desc.grid(row=1, column=0, columnspan=2, padx=10, pady=(0, 20), sticky="w")
        
        # Debloating Controls Card
        card = ctk.CTkFrame(frame, corner_radius=12)
        card.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        card.grid_columnconfigure(0, weight=1)
        card.grid_columnconfigure(1, weight=1)
        
        # Left column of buttons
        ctk.CTkButton(
            card,
            text="Create Restore Point (Important)",
            fg_color="#059669",
            hover_color="#047857",
            font=ctk.CTkFont(weight="bold"),
            command=lambda: self.run_cmd('start powershell -NoExit -Command "Enable-ComputerRestore -Drive C:; Checkpoint-Computer -Description \'WinPulseBeforeRepair\' -RestorePointType MODIFY_SETTINGS"', "Restore Point Creation")
        ).grid(row=0, column=0, padx=25, pady=15, sticky="ew")
        
        ctk.CTkButton(
            card,
            text="Disable Data Collection & Telemetry",
            command=lambda: self.run_cmd('reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\DataCollection" /v AllowTelemetry /t REG_DWORD /d 0 /f && powershell -Command "Stop-Service -Name DiagTrack -Force; Set-Service -Name DiagTrack -StartupType Disabled"', "Disable Telemetry")
        ).grid(row=1, column=0, padx=25, pady=15, sticky="ew")
        
        ctk.CTkButton(
            card,
            text="Disable Cortana Voice Search",
            command=lambda: self.run_cmd('reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\Windows Search" /v AllowCortana /t REG_DWORD /d 0 /f', "Disable Cortana")
        ).grid(row=2, column=0, padx=25, pady=15, sticky="ew")
        
        # Right column of buttons
        ctk.CTkButton(
            card,
            text="Disable Microsoft OneDrive Integration",
            command=lambda: self.run_cmd('reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\OneDrive" /v DisableFileSyncNGSC /t REG_DWORD /d 1 /f && taskkill /F /IM OneDrive.exe', "Disable OneDrive")
        ).grid(row=0, column=1, padx=25, pady=15, sticky="ew")
        
        ctk.CTkButton(
            card,
            text="Disable Xbox Services & Telemetry",
            command=lambda: self.run_cmd('powershell -Command "Stop-Service -Name XblAuthManager,XblGameSave,XboxNetApiSvc -Force; Set-Service -Name XblAuthManager,XblGameSave,XboxNetApiSvc -StartupType Disabled"', "Disable Xbox Services")
        ).grid(row=1, column=1, padx=25, pady=15, sticky="ew")
        
        ctk.CTkButton(
            card,
            text="Uninstall Appx Bloatware Bundle",
            command=lambda: self.run_cmd('start powershell -NoExit -Command "@(\'*XboxApp*\', \'*ZuneMusic*\', \'*BingNews*\', \'*Office.OneNote*\', \'*SolitaireCollection*\') | ForEach-Object { Get-AppxPackage -AllUsers $_ | Remove-AppxPackage -ErrorAction SilentlyContinue }"', "Uninstall Bloatware")
        ).grid(row=2, column=1, padx=25, pady=15, sticky="ew")

    # --- 4. APP DOWNLOADER FRAME ---
    def create_app_downloader_frame(self):
        frame = ctk.CTkFrame(self, fg_color="transparent")
        self.frames["AppDownloader"] = frame
        
        frame.grid_columnconfigure(0, weight=1)
        
        title = ctk.CTkLabel(frame, text="App Downloader (WinGet)", font=ctk.CTkFont(size=20, weight="bold"))
        title.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        desc = ctk.CTkLabel(frame, text="Download common desktop utility apps silently using Windows Package Manager (winget).", text_color="gray")
        desc.grid(row=1, column=0, padx=10, pady=(0, 20), sticky="w")
        
        # Download Card
        card = ctk.CTkFrame(frame, corner_radius=12)
        card.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
        card.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(card, text="Ninite-Style Quick Installers", font=ctk.CTkFont(size=15, weight="bold")).grid(row=0, column=0, padx=20, pady=15, sticky="w")
        
        ctk.CTkButton(
            card,
            text="Install Standard Web Bundle (Chrome + VLC + 7zip)",
            command=lambda: self.run_cmd('start powershell -NoExit -Command "winget install --id Google.Chrome --silent --accept-package-agreements --accept-source-agreements; winget install --id VideoLAN.VLC --silent --accept-package-agreements --accept-source-agreements; winget install --id 7zip.7zip --silent --accept-package-agreements --accept-source-agreements"', "Install Bundle")
        ).grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        
        # Search Box / Custom install
        search_label = ctk.CTkLabel(card, text="Search & Install Custom App (e.g. Git.Git, Zoom.Zoom):", font=ctk.CTkFont(size=12))
        search_label.grid(row=2, column=0, padx=20, pady=(15, 5), sticky="w")
        
        search_container = ctk.CTkFrame(card, fg_color="transparent")
        search_container.grid(row=3, column=0, padx=20, pady=(0, 20), sticky="ew")
        
        self.app_id_entry = ctk.CTkEntry(search_container, placeholder_text="Enter WinGet App ID (e.g., Notepad++.Notepad++)")
        self.app_id_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        install_btn = ctk.CTkButton(
            search_container,
            text="Install App",
            width=100,
            command=lambda: self.run_cmd(
                f"winget install --id {self.app_id_entry.get().strip()} --silent --accept-package-agreements --accept-source-agreements",
                f"Install {self.app_id_entry.get().strip()}"
            )
        )
        install_btn.pack(side="right")

    # --- 5. OFFICE & ACTIVATION FRAME ---
    def create_office_activation_frame(self):
        frame = ctk.CTkFrame(self, fg_color="transparent")
        self.frames["OfficeActivation"] = frame
        
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=1)
        
        title = ctk.CTkLabel(frame, text="Office Deploy & Activation Tool", font=ctk.CTkFont(size=20, weight="bold"))
        title.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="w")
        
        # Left Panel: Office Deployment Tool
        o_card = ctk.CTkFrame(frame, corner_radius=12)
        o_card.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        o_card.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(o_card, text="Install Microsoft Office Suites", font=ctk.CTkFont(size=15, weight="bold")).grid(row=0, column=0, padx=15, pady=15, sticky="w")
        
        ctk.CTkButton(
            o_card,
            text="Install Office 365 (M365 Cloud)",
            command=lambda: self.run_cmd('start winget install --id Microsoft.Office --silent --accept-package-agreements --accept-source-agreements', "Office 365 Installation")
        ).grid(row=1, column=0, padx=15, pady=8, sticky="ew")
        
        ctk.CTkButton(
            o_card,
            text="Install Office 2021 Volume (Silent ODT)",
            command=self.deploy_office_2021
        ).grid(row=2, column=0, padx=15, pady=8, sticky="ew")
        
        ctk.CTkButton(
            o_card,
            text="Install Office 2024 Volume (Silent ODT)",
            command=self.deploy_office_2024
        ).grid(row=3, column=0, padx=15, pady=8, sticky="ew")
        
        # Right Panel: Windows & Office Activation
        act_card = ctk.CTkFrame(frame, corner_radius=12)
        act_card.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
        act_card.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(act_card, text="OS & Office Activations (MAS)", font=ctk.CTkFont(size=15, weight="bold")).grid(row=0, column=0, padx=15, pady=15, sticky="w")
        
        ctk.CTkButton(
            act_card,
            text="Activate Windows (Permanently - HWID)",
            fg_color="#059669",
            hover_color="#047857",
            font=ctk.CTkFont(weight="bold"),
            command=lambda: self.run_cmd('start powershell -NoExit -Command "& ([ScriptBlock]::Create((irm https://get.activated.win))) /HWID"', "Windows HWID Activation")
        ).grid(row=1, column=0, padx=15, pady=8, sticky="ew")
        
        ctk.CTkButton(
            act_card,
            text="Activate Office (Local Patch - Ohook)",
            fg_color="#059669",
            hover_color="#047857",
            font=ctk.CTkFont(weight="bold"),
            command=lambda: self.run_cmd('start powershell -NoExit -Command "& ([ScriptBlock]::Create((irm https://get.activated.win))) /Ohook"', "Office Ohook Activation")
        ).grid(row=2, column=0, padx=15, pady=8, sticky="ew")
        
        ctk.CTkButton(
            act_card,
            text="KMS Windows & Office Activation (38-year)",
            command=lambda: self.run_cmd('start powershell -NoExit -Command "& ([ScriptBlock]::Create((irm https://get.activated.win))) /K-WindowsOffice"', "KMS Activation")
        ).grid(row=3, column=0, padx=15, pady=8, sticky="ew")
        
        ctk.CTkButton(
            act_card,
            text="Uninstall KMS Activations",
            command=lambda: self.run_cmd('start powershell -NoExit -Command "& ([ScriptBlock]::Create((irm https://get.activated.win))) /K-Uninstall"', "KMS Activation Uninstall")
        ).grid(row=4, column=0, padx=15, pady=8, sticky="ew")

    # Helper function to deploy Office 2021 silently via ODT
    def deploy_office_2021(self):
        import tempfile
        ps_path = os.path.join(tempfile.gettempdir(), 'install_office_2021.ps1')
        script = """$ErrorActionPreference = 'Stop'
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
"""
        with open(ps_path, 'w', encoding='utf-8') as f:
            f.write(script)
        self.run_cmd(f'start powershell -NoExit -ExecutionPolicy Bypass -File "{ps_path}"', "Office 2021 Deployment")

    # Helper function to deploy Office 2024 silently via ODT
    def deploy_office_2024(self):
        import tempfile
        ps_path = os.path.join(tempfile.gettempdir(), 'install_office_2024.ps1')
        script = """$ErrorActionPreference = 'Stop'
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
"""
        with open(ps_path, 'w', encoding='utf-8') as f:
            f.write(script)
        self.run_cmd(f'start powershell -NoExit -ExecutionPolicy Bypass -File "{ps_path}"', "Office 2024 Deployment")

    # --- 6. ADMIN TOOLS FRAME ---
    def create_admin_tools_frame(self):
        frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.frames["AdminTools"] = frame
        
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=1)
        
        title = ctk.CTkLabel(frame, text="Administrative & Cleanup Shortcuts", font=ctk.CTkFont(size=20, weight="bold"))
        title.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="w")
        
        # Column 1: Shortcuts
        c1 = ctk.CTkFrame(frame, corner_radius=10)
        c1.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        c1.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(c1, text="Windows Consoles", font=ctk.CTkFont(size=14, weight="bold")).grid(row=0, column=0, padx=15, pady=10, sticky="w")
        
        shortcuts = [
            ("Registry Editor (regedit)", "start regedit.exe"),
            ("Group Policy Editor (gpedit.msc)", "start gpedit.msc"),
            ("Computer Management (compmgmt)", "start compmgmt.msc"),
            ("Local Users and Groups (lusrmgr)", "start lusrmgr.msc"),
            ("UAC Elevation Settings Dialog", "start useraccountcontrolsettings.exe"),
            ("System Properties Console (sysdm)", "start sysdm.cpl"),
            ("Advanced Device Specifications Info", "start msinfo32.exe")
        ]
        
        for idx, (label, cmd) in enumerate(shortcuts):
            ctk.CTkButton(
                c1,
                text=label,
                command=lambda c=cmd, l=label: self.run_cmd(c, l)
            ).grid(row=idx+1, column=0, padx=15, pady=6, sticky="ew")
            
        # Column 2: Cleanup and Verify Tools
        c2 = ctk.CTkFrame(frame, corner_radius=10)
        c2.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
        c2.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(c2, text="System Maintenance & Optimization", font=ctk.CTkFont(size=14, weight="bold")).grid(row=0, column=0, padx=15, pady=10, sticky="w")
        
        ctk.CTkButton(
            c2,
            text="SFC System File Integrity Scan",
            fg_color="#059669",
            hover_color="#047857",
            font=ctk.CTkFont(weight="bold"),
            command=lambda: self.run_cmd("start cmd /k sfc /scannow", "SFC integrity Scan")
        ).grid(row=1, column=0, padx=15, pady=8, sticky="ew")
        
        ctk.CTkButton(
            c2,
            text="DISM Windows Health Repair",
            command=lambda: self.run_cmd("start cmd /k dism /online /cleanup-image /restorehealth", "DISM Restore Health")
        ).grid(row=2, column=0, padx=15, pady=8, sticky="ew")
        
        ctk.CTkButton(
            c2,
            text="Flush System DNS Cache",
            command=lambda: self.run_cmd("ipconfig /flushdns", "DNS Flush")
        ).grid(row=3, column=0, padx=15, pady=8, sticky="ew")
        
        ctk.CTkButton(
            c2,
            text="Reset TCP/IP Winsock Sockets",
            command=lambda: self.run_cmd("netsh winsock reset", "Winsock Reset")
        ).grid(row=4, column=0, padx=15, pady=8, sticky="ew")
        
        ctk.CTkButton(
            c2,
            text="Purge Temporary Temp Directories",
            command=lambda: self.run_cmd('start powershell -NoExit -Command "Remove-Item -Path \'C:\\Windows\\Temp\\*\' -Recurse -Force; Remove-Item -Path \'C:\\Users\\*\\AppData\\Local\\Temp\\*\' -Recurse -Force; Remove-Item -Path \'C:\\Windows\\Prefetch\\*\' -Recurse -Force"', "Temp Cache Cleanup")
        ).grid(row=5, column=0, padx=15, pady=8, sticky="ew")
        
        ctk.CTkButton(
            c2,
            text="Restart Windows File Explorer",
            command=lambda: self.run_cmd('start cmd /c "taskkill /f /im explorer.exe && start explorer.exe"', "Explorer Restart")
        ).grid(row=6, column=0, padx=15, pady=8, sticky="ew")

    # --- 7. AI ASSISTANT FRAME ---
    def create_ai_assistant_frame(self):
        frame = ctk.CTkFrame(self, fg_color="transparent")
        self.frames["AiAssistant"] = frame
        
        frame.grid_rowconfigure(2, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        
        # Header Info
        header_container = ctk.CTkFrame(frame, fg_color="transparent")
        header_container.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        
        title = ctk.CTkLabel(header_container, text="VenkatPulse AI Assistant", font=ctk.CTkFont(size=20, weight="bold"))
        title.pack(side="left")
        
        # Key Entry configuration
        self.key_btn = ctk.CTkButton(
            header_container,
            text="Set Gemini API Key",
            width=130,
            command=self.prompt_api_key
        )
        self.key_btn.pack(side="right")
        
        if self.gemini_key:
            self.status_lbl = ctk.CTkLabel(frame, text="🤖 Mode: Online Gemini AI Active", text_color="#10b981")
        else:
            self.status_lbl = ctk.CTkLabel(frame, text="🤖 Mode: Offline Rule Matcher (Set Gemini API Key to enable full Conversational AI)", text_color="gray")
        self.status_lbl.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="w")
        
        # Chat History Log
        self.chat_textbox = ctk.CTkTextbox(frame, state="disabled", wrap="word", corner_radius=10)
        self.chat_textbox.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
        
        # Input Box
        input_container = ctk.CTkFrame(frame, fg_color="transparent")
        input_container.grid(row=3, column=0, padx=10, pady=10, sticky="ew")
        
        self.user_entry = ctk.CTkEntry(input_container, placeholder_text="Ask about spooler issues, slow system, telemetry, etc...")
        self.user_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.user_entry.bind("<Return>", lambda event: self.send_chat_msg())
        
        send_btn = ctk.CTkButton(input_container, text="Send Message", width=120, command=self.send_chat_msg)
        send_btn.pack(side="right")
        
        # Send initial greeting
        self.append_chat("Assistant", "Hello! I am your local diagnostic assistant. How can I help you optimize or repair your computer today?")

    def prompt_api_key(self):
        dialog = ctk.CTkInputDialog(text="Enter your Google Gemini API Key:", title="Online AI Mode Activation")
        key = dialog.get_input()
        if key is not None:
            self.gemini_key = key.strip()
            self.save_gemini_key(self.gemini_key)
            if self.gemini_key:
                self.status_lbl.configure(text="🤖 Mode: Online Gemini AI Active", text_color="#10b981")
                self.append_chat("System", "Online Mode Activated successfully.")
            else:
                self.status_lbl.configure(text="🤖 Mode: Offline Rule Matcher (Set Gemini API Key to enable full Conversational AI)", text_color="gray")
                self.append_chat("System", "Gemini API Key removed. Offline Mode Active.")

    def append_chat(self, sender, text):
        self.chat_textbox.configure(state="normal")
        self.chat_textbox.insert("end", f"[{sender}]: {text}\n\n")
        self.chat_textbox.configure(state="disabled")
        self.chat_textbox.see("end")

    def send_chat_msg(self):
        msg = self.user_entry.get().strip()
        if not msg:
            return
            
        self.user_entry.delete(0, "end")
        self.append_chat("You", msg)
        
        if self.gemini_key:
            # Query Gemini API in background thread
            threading.Thread(target=self.query_gemini_api, args=(msg,), daemon=True).start()
        else:
            # Run offline rule matching
            self.run_offline_diagnosis(msg)

    def query_gemini_api(self, prompt_text):
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.gemini_key}"
        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [{
                "parts": [{
                    "text": f"You are a helpful IT System administrator helper called VenkatPulse AI. A user is asking help for system diagnosis: '{prompt_text}'. Keep response concise and offer actionable Windows commands or tips."
                }]
            }]
        }
        
        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode('utf-8'),
                headers=headers,
                method='POST'
            )
            with urllib.request.urlopen(req) as res:
                response = json.loads(res.read().decode('utf-8'))
                text_response = response['candidates'][0]['content']['parts'][0]['text']
                self.after(0, lambda: self.append_chat("Assistant", text_response.strip()))
        except Exception as e:
            self.after(0, lambda: self.append_chat("System Error", f"Gemini API request failed: {e}"))

    def run_offline_diagnosis(self, text):
        text = text.lower()
        if "spooler" in text or "printer" in text or "queue" in text:
            ans = ("I detected Spooler/Printer keywords. Actions you can take:\n"
                   "- Stop and restart the printer service.\n"
                   "- Clear the queue files under C:\\Windows\\System32\\spool\\PRINTERS.\n"
                   "You can trigger these directly in the 'System Repairs' frame.")
        elif "slow" in text or "optimize" in text or "lag" in text or "speed" in text:
            ans = ("For slow system performance:\n"
                   "- Run the 'Purge Temporary Directories' tool in Admin Tools.\n"
                   "- Run SFC /scannow or DISM system file integrity checks.\n"
                   "- Disable Windows Telemetry under 'Win Debloater'.")
        elif "internet" in text or "dns" in text or "network" in text:
            ans = ("For internet or network errors:\n"
                   "- Try flushing the DNS cache using 'Flush System DNS Cache'.\n"
                   "- Reset network winsock catalog sockets using 'Reset TCP/IP Winsock Sockets'.\n"
                   "- Ensure 'Network Discovery' is enabled for LAN sharing.")
        elif "corrupt" in text or "error" in text:
            ans = ("If you suspect system file corruption:\n"
                   "- Launch the 'SFC System File Integrity Scan' in the Admin Tools frame.\n"
                   "- Perform a 'DISM Windows Health Repair'.")
        else:
            ans = ("I am running in Offline Mode. Describe your issue with keywords like 'spooler', 'slow', 'internet', or 'corrupt' so I can give specific recommendations.\n\n"
                   "To get full conversational advice, insert a Google Gemini API Key in the top right corner.")
            
        self.after(0, lambda: self.append_chat("Assistant", ans))

    def get_config_path(self):
        return os.path.join(os.path.expanduser("~"), ".winpulse_config.json")

    def load_gemini_key(self):
        try:
            config_path = self.get_config_path()
            if os.path.exists(config_path):
                with open(config_path, "r", encoding="utf-8") as f:
                    config = json.load(f)
                    return config.get("gemini_key", "").strip()
            else:
                return self.DEFAULT_GEMINI_KEY
        except Exception as e:
            print(f"Error loading config: {e}")
        return self.DEFAULT_GEMINI_KEY

    def save_gemini_key(self, key):
        try:
            config_path = self.get_config_path()
            config = {}
            if os.path.exists(config_path):
                with open(config_path, "r", encoding="utf-8") as f:
                    try:
                        config = json.load(f)
                    except:
                        pass
            config["gemini_key"] = key
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=4)
        except Exception as e:
            print(f"Error saving config: {e}")

    def on_closing(self):
        self.telemetry_running = False
        self.destroy()

if __name__ == "__main__":
    app = PrintPulseApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
