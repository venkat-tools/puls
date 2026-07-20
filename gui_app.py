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
import shutil
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

class VenkatPulseApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Window configuration
        self.title("Venkat Windows Tool Kit OS Recovery Suite")
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
                text="Venkat Windows Tool Kit", 
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
            ("AiAssistant", "💬 AI Assistant"),
            ("WinPEBuilder", "💾 WinPE USB Builder"),
            ("DiskSecurity", "💾 Disk & Password Tools"),
            ("StandaloneTools", "🧰 Standalone Tools")
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
        self.create_winpe_builder_frame()
        self.create_disk_security_frame()
        self.create_standalone_tools_frame()
        
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
            text="Welcome to Venkat Windows Tool Kit Suite", 
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
            command=lambda: self.run_cmd('start cmd /k "if not exist C:\\PulseBackup mkdir C:\\PulseBackup && C:\\Windows\\System32\\Spool\\Tools\\PrintBrm.exe -b -f C:\\PulseBackup\\PrinterBackup.printerExport"', "Printer Backup")
        ).grid(row=1, column=0, padx=15, pady=8, sticky="ew")
        
        ctk.CTkButton(
            g4, 
            text="Restore Printer Backup", 
            command=lambda: self.run_cmd('start cmd /k C:\\Windows\\System32\\Spool\\Tools\\PrintBrm.exe -r -f C:\\PulseBackup\\PrinterBackup.printerExport', "Printer Restore")
        ).grid(row=2, column=0, padx=15, pady=8, sticky="ew")

        # Group 5: Full PC Migration & App Backup
        g5 = ctk.CTkFrame(frame, corner_radius=10)
        g5.grid(row=4, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        g5.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(g5, text="Full PC Migration & App Backup", font=ctk.CTkFont(size=15, weight="bold")).grid(row=0, column=0, columnspan=2, padx=15, pady=15, sticky="w")
        
        # Path Entry and Browse button
        path_frame = ctk.CTkFrame(g5, fg_color="transparent")
        path_frame.grid(row=1, column=0, columnspan=2, padx=15, pady=5, sticky="ew")
        path_frame.grid_columnconfigure(0, weight=1)
        
        dest_entry = ctk.CTkEntry(path_frame, placeholder_text="Enter Backup Destination Directory (e.g. C:\\PulseBackup)...")
        dest_entry.grid(row=0, column=0, padx=(0, 10), sticky="ew")
        dest_entry.insert(0, "C:\\PulseBackup")
        
        def browse_dest():
            from tkinter import filedialog
            selected = filedialog.askdirectory(title="Select Backup Destination")
            if selected:
                dest_entry.delete(0, "end")
                dest_entry.insert(0, selected)
                
        ctk.CTkButton(path_frame, text="Browse", width=80, command=browse_dest).grid(row=0, column=1, sticky="e")
        
        # Action buttons
        btn_frame = ctk.CTkFrame(g5, fg_color="transparent")
        btn_frame.grid(row=2, column=0, columnspan=2, padx=15, pady=(10, 15), sticky="ew")
        btn_frame.grid_columnconfigure(0, weight=1)
        btn_frame.grid_columnconfigure(1, weight=1)
        btn_frame.grid_columnconfigure(2, weight=1)
        
        def run_profile_backup():
            path = dest_entry.get().strip()
            if not path:
                from tkinter import messagebox
                messagebox.showerror("Error", "Please select a backup destination path first.")
                return
            # Robocopy script to copy User folders: Desktop, Documents, Downloads, Pictures, Music, Videos
            cmd = f'start cmd /k powershell -NoExit -Command "$dest = \'{path}\'; $folders = @(\'Desktop\', \'Documents\', \'Downloads\', \'Pictures\', \'Music\', \'Videos\'); foreach ($f in $folders) {{ $src = Join-Path $env:USERPROFILE $f; $tgt = Join-Path $dest $f; if (Test-Path $src) {{ robocopy $src $tgt /E /MT:8 /R:1 /W:1 /XJD }} }}"'
            self.run_cmd(cmd, "User Profile Backup")
            
        def run_winget_export():
            path = dest_entry.get().strip()
            if not path:
                export_path = "C:\\PulseBackup\\winget_apps.json"
            else:
                export_path = f"{path}\\winget_apps.json"
            
            import os
            dir_path = os.path.dirname(export_path)
            if not os.path.exists(dir_path):
                try:
                    os.makedirs(dir_path, exist_ok=True)
                except Exception:
                    pass
            
            cmd = f'start cmd /k winget export -o "{export_path}" --accept-source-agreements'
            self.run_cmd(cmd, "Winget Apps Export")
            
        def run_winget_import():
            from tkinter import filedialog
            selected_file = filedialog.askopenfilename(
                title="Select Winget Apps JSON File",
                filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")]
            )
            if selected_file:
                cmd = f'start cmd /k winget import -i "{selected_file}" --accept-package-agreements --accept-source-agreements'
                self.run_cmd(cmd, "Winget Apps Import")
        
        ctk.CTkButton(
            btn_frame, 
            text="Backup User Profile", 
            command=run_profile_backup,
            fg_color="#7c3aed",
            hover_color="#6d28d9"
        ).grid(row=0, column=0, padx=5, sticky="ew")
        
        ctk.CTkButton(
            btn_frame, 
            text="Export Apps List", 
            command=run_winget_export
        ).grid(row=0, column=1, padx=5, sticky="ew")
        
        ctk.CTkButton(
            btn_frame, 
            text="Import Apps List", 
            command=run_winget_import
        ).grid(row=0, column=2, padx=5, sticky="ew")

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

        # Performance Optimizer Card
        opt_title = ctk.CTkLabel(frame, text="Performance & Maintenance Tweaks", font=ctk.CTkFont(size=16, weight="bold"))
        opt_title.grid(row=3, column=0, columnspan=2, padx=10, pady=(20, 5), sticky="w")
        
        card2 = ctk.CTkFrame(frame, corner_radius=12)
        card2.grid(row=4, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        card2.grid_columnconfigure(0, weight=1)
        card2.grid_columnconfigure(1, weight=1)
        
        # Left column of Performance Tweaks
        ctk.CTkButton(
            card2,
            text="Enable Ultimate Performance Power Plan",
            command=lambda: self.run_cmd('powercfg -duplicatescheme e9a42b02-d5df-448d-aa00-03f14749eb61 && powercfg -setactive e9a42b02-d5df-448d-aa00-03f14749eb61', "Enable Ultimate Performance")
        ).grid(row=0, column=0, padx=25, pady=15, sticky="ew")
        
        ctk.CTkButton(
            card2,
            text="Disable Bing Suggestions in Start Search",
            command=lambda: self.run_cmd('reg add "HKCU\\Software\\Policies\\Microsoft\\Windows\\Explorer" /v DisableSearchBoxSuggestions /t REG_DWORD /d 1 /f && reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Search" /v BingSearchEnabled /t REG_DWORD /d 0 /f', "Disable Bing Start Search")
        ).grid(row=1, column=0, padx=25, pady=15, sticky="ew")
        
        ctk.CTkButton(
            card2,
            text="Optimize Visual Effects (Responsive UI)",
            command=lambda: self.run_cmd('reg add "HKCU\\Control Panel\\Desktop" /v MenuShowDelay /t REG_SZ /d 0 /f && reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\VisualEffects" /v VisualFXSetting /t REG_DWORD /d 2 /f', "Optimize Visual Effects")
        ).grid(row=2, column=0, padx=25, pady=15, sticky="ew")
        
        # Right column of Performance Tweaks
        ctk.CTkButton(
            card2,
            text="Deep Temporary Cache Cleaner",
            command=lambda: self.run_cmd('start cmd /k powershell -NoExit -Command "Write-Host \'Cleaning Temporary folders...\'; Remove-Item -Path $env:TEMP\\* -Recurse -Force -ErrorAction SilentlyContinue; Remove-Item -Path \'C:\\Windows\\Temp\\*\' -Recurse -Force -ErrorAction SilentlyContinue; Remove-Item -Path \'C:\\Windows\\Prefetch\\*\' -Recurse -Force -ErrorAction SilentlyContinue; Write-Host \'Temporary folders cleared successfully!\'"', "Deep Temp Clean")
        ).grid(row=0, column=1, padx=25, pady=15, sticky="ew")
        
        ctk.CTkButton(
            card2,
            text="Reset Windows Update Components Cache",
            command=lambda: self.run_cmd('start cmd /k powershell -NoExit -Command "Write-Host \'Stopping Windows Update services...\'; Stop-Service -Name wuauserv, bits, cryptsvc -Force; Write-Host \'Clearing cache...\'; Remove-Item -Path \'C:\\Windows\\SoftwareDistribution\\*\' -Recurse -Force -ErrorAction SilentlyContinue; Write-Host \'Restarting services...\'; Start-Service -Name wuauserv, bits, cryptsvc; Write-Host \'Windows Update Cache reset successfully!\'"', "Reset Update Cache")
        ).grid(row=1, column=1, padx=25, pady=15, sticky="ew")
        
        ctk.CTkButton(
            card2,
            text="Full Network Socket & DNS Flush Reset",
            command=lambda: self.run_cmd('start cmd /k "ipconfig /release && ipconfig /renew && ipconfig /flushdns && netsh winsock reset && netsh int ip reset"', "Network Socket Reset")
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
        frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
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

        # Bottom Panel: Windows Edition Changer
        edition_card = ctk.CTkFrame(frame, corner_radius=12)
        edition_card.grid(row=2, column=0, columnspan=2, padx=10, pady=15, sticky="nsew")
        edition_card.grid_columnconfigure(0, weight=1)
        edition_card.grid_columnconfigure(1, weight=2)
        edition_card.grid_columnconfigure(2, weight=1)
        
        ctk.CTkLabel(edition_card, text="Windows Edition Changer", font=ctk.CTkFont(size=15, weight="bold")).grid(row=0, column=0, columnspan=3, padx=15, pady=10, sticky="w")
        
        # Options mapping
        edition_keys = {
            "Windows 10/11 Pro": "VK7JG-NPHTM-C97JM-9MPGT-3V66T",
            "Windows 10/11 Enterprise": "XGVPP-NMH47-7TTHJ-W3FW7-8DEC2",
            "Windows 10/11 Pro Education": "6TP4R-GNPTD-KYYHQ-7B7DP-F4A3C",
            "Windows 10/11 Education": "NW6C2-QMPVW-D7KKK-3GKT6-VCFB2",
            "Custom Product Key...": ""
        }
        
        # Dropdown
        edition_combo = ctk.CTkComboBox(
            edition_card, 
            values=list(edition_keys.keys()),
            width=220
        )
        edition_combo.grid(row=1, column=0, padx=15, pady=15, sticky="ew")
        edition_combo.set("Windows 10/11 Pro")
        
        # Product key text box
        key_entry = ctk.CTkEntry(
            edition_card,
            placeholder_text="Product Key (XXXXX-XXXXX-XXXXX-XXXXX-XXXXX)",
            font=ctk.CTkFont(family="Consolas")
        )
        key_entry.grid(row=1, column=1, padx=10, pady=15, sticky="ew")
        key_entry.insert(0, edition_keys["Windows 10/11 Pro"])
        
        # Combo selection callback
        def on_edition_combo_change(val):
            key = edition_keys.get(val, "")
            key_entry.delete(0, "end")
            if val == "Custom Product Key...":
                key_entry.configure(placeholder_text="Enter custom product key...")
            else:
                key_entry.insert(0, key)
                
        edition_combo.configure(command=on_edition_combo_change)
        
        def run_edition_change():
            from tkinter import messagebox
            key = key_entry.get().strip()
            if not key or len(key) < 20:
                messagebox.showerror("Error", "Please enter a valid 25-character Windows Product Key.")
                return
            if messagebox.askyesno("Confirm Edition Change", f"Are you sure you want to change your Windows edition? This will invoke the Windows upgrade wizard using the key: {key}. Your PC might restart during the process."):
                self.run_cmd(f"start changepk.exe /ProductKey {key}", "Windows Edition Changer")
                
        ctk.CTkButton(
            edition_card,
            text="Change Edition",
            command=run_edition_change,
            fg_color="#7c3aed",
            hover_color="#6d28d9"
        ).grid(row=1, column=2, padx=15, pady=15, sticky="ew")

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

        # Row 2, span both columns: Windows Update Manager
        c3 = ctk.CTkFrame(frame, corner_radius=10)
        c3.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        c3.grid_columnconfigure(0, weight=1)
        c3.grid_columnconfigure(1, weight=1)
        c3.grid_columnconfigure(2, weight=1)
        
        ctk.CTkLabel(c3, text="Windows Update Manager", font=ctk.CTkFont(size=15, weight="bold")).grid(row=0, column=0, columnspan=3, padx=15, pady=10, sticky="w")
        
        # Stop updates button
        ctk.CTkButton(
            c3,
            text="🛑 Stop Windows Updates",
            fg_color="#b91c1c",
            hover_color="#991b1b",
            font=ctk.CTkFont(weight="bold"),
            command=lambda: self.run_cmd('start powershell -NoExit -Command "Write-Host \'Stopping and disabling Windows Update services...\'; Stop-Service -Name wuauserv, bits, UsoSvc -Force; Set-Service -Name wuauserv, bits, UsoSvc -StartupType Disabled; reg add \\"HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\WindowsUpdate\\AU\\" /v NoAutoUpdate /t REG_DWORD /d 1 /f; reg add \\"HKLM\\SYSTEM\\CurrentControlSet\\Services\\WaaSMedicSvc\\" /v Start /t REG_DWORD /d 4 /f; Write-Host \'Windows Updates have been fully disabled.\'"', "Stop Updates")
        ).grid(row=1, column=0, padx=15, pady=15, sticky="ew")
        
        # Resume updates button
        ctk.CTkButton(
            c3,
            text="▶️ Resume Windows Updates",
            fg_color="#059669",
            hover_color="#047857",
            font=ctk.CTkFont(weight="bold"),
            command=lambda: self.run_cmd('start powershell -NoExit -Command "Write-Host \'Enabling and restarting Windows Update services...\'; reg delete \\"HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\WindowsUpdate\\AU\\" /v NoAutoUpdate /f; reg add \\"HKLM\\SYSTEM\\CurrentControlSet\\Services\\WaaSMedicSvc\\" /v Start /t REG_DWORD /d 3 /f; Set-Service -Name wuauserv, bits, UsoSvc -StartupType Manual; Start-Service -Name wuauserv, bits, UsoSvc; Write-Host \'Windows Updates have been enabled and restarted.\'"', "Resume Updates")
        ).grid(row=1, column=1, padx=15, pady=15, sticky="ew")
        
        # Security updates only button
        ctk.CTkButton(
            c3,
            text="🛡️ Security Updates Only",
            command=lambda: self.run_cmd('start powershell -NoExit -Command "Write-Host \'Configuring Windows Update for Security Patches Only...\'; reg add \\"HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\WindowsUpdate\\" /v ExcludeWUDriversInQualityUpdate /t REG_DWORD /d 1 /f; reg add \\"HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\WindowsUpdate\\" /v DeferFeatureUpdates /t REG_DWORD /d 1 /f; reg add \\"HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\WindowsUpdate\\" /v DeferFeatureUpdatesPeriodInDays /t REG_DWORD /d 365 /f; reg add \\"HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\WindowsUpdate\\" /v DeferQualityUpdates /t REG_DWORD /d 1 /f; reg add \\"HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\WindowsUpdate\\" /v DeferQualityUpdatesPeriodInDays /t REG_DWORD /d 4 /f; reg delete \\"HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\WindowsUpdate\\AU\\" /v NoAutoUpdate /f; reg add \\"HKLM\\SYSTEM\\CurrentControlSet\\Services\\WaaSMedicSvc\\" /v Start /t REG_DWORD /d 3 /f; Set-Service -Name wuauserv, bits, UsoSvc -StartupType Manual; Start-Service -Name wuauserv, bits, UsoSvc; Write-Host \'Windows Update configured for Security Updates Only (Features deferred 365 days, drivers disabled, updates enabled).\'"', "Security Updates Only")
        ).grid(row=1, column=2, padx=15, pady=15, sticky="ew")

        # Row 3, span both columns: Driver & Hardware Management
        c4 = ctk.CTkFrame(frame, corner_radius=10)
        c4.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        c4.grid_columnconfigure(0, weight=1)
        c4.grid_columnconfigure(1, weight=1)
        c4.grid_columnconfigure(2, weight=1)
        
        ctk.CTkLabel(c4, text="Driver & Hardware Management", font=ctk.CTkFont(size=15, weight="bold")).grid(row=0, column=0, columnspan=3, padx=15, pady=10, sticky="w")
        
        # Scan for Driver Updates via Windows Update
        ctk.CTkButton(
            c4,
            text="🔍 Scan Missing Drivers (PnP)",
            command=lambda: self.run_cmd("pnputil /scan-devices", "Scan Missing Drivers")
        ).grid(row=1, column=0, padx=15, pady=15, sticky="ew")
        
        # Backup System Drivers
        ctk.CTkButton(
            c4,
            text="📦 Backup Drivers to C:\\PulseBackup",
            command=lambda: self.run_cmd('start cmd /k "if not exist C:\\PulseBackup\\Drivers mkdir C:\\PulseBackup\\Drivers && pnputil /export-driver * C:\\PulseBackup\\Drivers && echo Drivers successfully backed up to C:\\PulseBackup\\Drivers && pause"', "Backup Drivers")
        ).grid(row=1, column=1, padx=15, pady=15, sticky="ew")
        
        # Restore System Drivers
        ctk.CTkButton(
            c4,
            text="🚚 Restore Drivers from Backup",
            command=lambda: self.run_cmd('start cmd /k "if not exist C:\\PulseBackup\\Drivers (echo Backup folder C:\\PulseBackup\\Drivers not found! && pause) else (pnputil /add-driver C:\\PulseBackup\\Drivers\\*.inf /subdirs /install /reboot)"', "Restore Drivers")
        ).grid(row=1, column=2, padx=15, pady=15, sticky="ew")
        
        # Row 2 inside c4: Device Manager & Rapr
        ctk.CTkButton(
            c4,
            text="⚙ Launch Windows Device Manager",
            command=lambda: self.run_cmd("start devmgmt.msc", "Launch Device Manager")
        ).grid(row=2, column=0, padx=15, pady=(0, 15), sticky="ew")
        
        ctk.CTkButton(
            c4,
            text="📥 Force Install Driver Upgrades",
            fg_color="#059669",
            hover_color="#047857",
            font=ctk.CTkFont(weight="bold"),
            command=lambda: self.run_cmd('start powershell -ExecutionPolicy Bypass -Command "try { Write-Host \'Setting up PSWindowsUpdate module...\' -ForegroundColor Cyan; [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Set-PSRepository -Name PSGallery -InstallationPolicy Trusted -ErrorAction SilentlyContinue; Install-PackageProvider -Name NuGet -MinimumVersion 2.8.5.201 -Force -ErrorAction SilentlyContinue; Install-Module -Name PSWindowsUpdate -Force -SkipPublisherCheck -ErrorAction SilentlyContinue; Import-Module PSWindowsUpdate -ErrorAction Stop; Write-Host \'Enabling and starting Windows Update service...\' -ForegroundColor Cyan; Set-Service -Name wuauserv -StartupType Manual -ErrorAction SilentlyContinue; Start-Service -Name wuauserv -ErrorAction SilentlyContinue; Write-Host \'Checking for driver updates...\' -ForegroundColor Cyan; $updates = Get-WindowsUpdate -Category \'Drivers\' -ErrorAction SilentlyContinue; if ($updates) { Write-Host \'Driver updates found! Installing...\' -ForegroundColor Green; Get-WindowsUpdate -Category \'Drivers\' -Install -AcceptAll -AutoReboot; } else { Write-Host \'All system drivers are already up to date.\' -ForegroundColor Green; } } catch { Write-Host \'Error: \' $_.Exception.Message -ForegroundColor Red; Write-Host \'Failed to run PSWindowsUpdate. Make sure you are connected to the Internet.\' -ForegroundColor Red; } Write-Host \'Process complete. Press Enter to close this window...\' -ForegroundColor Cyan; [void]$Host.UI.RawUI.ReadKey(\'NoEcho,IncludeKeyDown\');"', "Force Driver Upgrades")
        ).grid(row=2, column=1, padx=15, pady=(0, 15), sticky="ew")
        
        ctk.CTkButton(
            c4,
            text="🌐 Download DriverStore Explorer (Rapr)",
            command=lambda: self.run_cmd("start https://github.com/lostindark/DriverStoreExplorer/releases", "Download Rapr")
        ).grid(row=2, column=2, padx=15, pady=(0, 15), sticky="ew")

        # Row 4, span both columns: Advanced System & Security Tools
        c5 = ctk.CTkFrame(frame, corner_radius=10)
        c5.grid(row=4, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        c5.grid_columnconfigure(0, weight=1)
        c5.grid_columnconfigure(1, weight=1)
        c5.grid_columnconfigure(2, weight=1)
        
        ctk.CTkLabel(c5, text="Advanced System & Security Utilities", font=ctk.CTkFont(size=15, weight="bold")).grid(row=0, column=0, columnspan=3, padx=15, pady=10, sticky="w")
        
        # Defender Disable / Enable
        ctk.CTkButton(
            c5,
            text="🛡️ Disable Defender Realtime",
            fg_color="#dc2626",
            hover_color="#b91c1c",
            command=lambda: self.run_cmd('start powershell -NoExit -Command "Write-Host \'Disabling Windows Defender Real-time Monitoring...\' -ForegroundColor Yellow; Set-MpPreference -DisableRealtimeMonitoring $true; Write-Host \'Real-time monitoring temporarily disabled.\' -ForegroundColor Green"', "Disable Defender")
        ).grid(row=1, column=0, padx=15, pady=15, sticky="ew")
        
        ctk.CTkButton(
            c5,
            text="🛡️ Enable Defender Realtime",
            fg_color="#2563eb",
            hover_color="#1d4ed8",
            command=lambda: self.run_cmd('start powershell -NoExit -Command "Write-Host \'Enabling Windows Defender Real-time Monitoring...\' -ForegroundColor Cyan; Set-MpPreference -DisableRealtimeMonitoring $false; Write-Host \'Real-time monitoring re-enabled.\' -ForegroundColor Green"', "Enable Defender")
        ).grid(row=1, column=1, padx=15, pady=15, sticky="ew")
        
        # Scan Listening Ports
        ctk.CTkButton(
            c5,
            text="🔌 Scan Active Listening Ports",
            command=lambda: self.run_cmd('start cmd /k "echo Scanning active listening network ports... && echo. && netstat -ano | findstr LISTENING && echo. && echo Port list complete. Locate the PID inside Windows Task Manager details. && pause"', "Port Scanner")
        ).grid(row=1, column=2, padx=15, pady=15, sticky="ew")
        
        # Row 2 inside c5
        # Browser Cache Purge
        ctk.CTkButton(
            c5,
            text="🧹 Purge Browser Caches (Edge/Chrome)",
            command=lambda: self.run_cmd('start powershell -NoExit -Command "Write-Host \'Closing active browser processes...\' -ForegroundColor Yellow; Stop-Process -Name chrome, msedge, firefox -Force -ErrorAction SilentlyContinue; Start-Sleep -Seconds 1; Write-Host \'Purging Google Chrome local temporary cache...\' -ForegroundColor Cyan; Remove-Item -Path \'$env:LOCALAPPDATA\\Google\\Chrome\\User Data\\Default\\Cache\\*\' -Recurse -Force -ErrorAction SilentlyContinue; Write-Host \'Purging Microsoft Edge local temporary cache...\' -ForegroundColor Cyan; Remove-Item -Path \'$env:LOCALAPPDATA\\Microsoft\\Edge\\User Data\\Default\\Cache\\*\' -Recurse -Force -ErrorAction SilentlyContinue; Write-Host \'Cache purge complete!\' -ForegroundColor Green"', "Browser Cache Purge")
        ).grid(row=2, column=0, padx=15, pady=(0, 15), sticky="ew")
        
        # Windows Sandbox & Hyper-V Toggles
        ctk.CTkButton(
            c5,
            text="📦 Enable Windows Sandbox Feature",
            command=lambda: self.run_cmd('start cmd /k "dism /online /Enable-Feature /FeatureName:Containers-DisposableVM /All /NoRestart && echo. && echo Windows Sandbox has been enabled successfully. Restart computer to apply changes. && pause"', "Enable Sandbox")
        ).grid(row=2, column=1, padx=15, pady=(0, 15), sticky="ew")
        
        ctk.CTkButton(
            c5,
            text="💻 Enable Hyper-V Platform",
            command=lambda: self.run_cmd('start cmd /k "dism /online /Enable-Feature /FeatureName:Microsoft-Hyper-V /All /NoRestart && echo. && echo Hyper-V Virtualization has been enabled successfully. Restart computer to apply changes. && pause"', "Enable Hyper-V")
        ).grid(row=2, column=2, padx=15, pady=(0, 15), sticky="ew")
        
        # Row 3 inside c5
        # Startup apps manager
        ctk.CTkButton(
            c5,
            text="⚡ Launch Startup Apps Manager (TaskMgr)",
            command=lambda: self.run_cmd("start taskmgr /0 /startup", "Startup Manager")
        ).grid(row=3, column=0, padx=15, pady=(0, 15), sticky="ew")
        
        # Event Viewer
        ctk.CTkButton(
            c5,
            text="📜 Open System Event Viewer Console",
            command=lambda: self.run_cmd("start eventvwr.msc", "Event Viewer")
        ).grid(row=3, column=1, padx=15, pady=(0, 15), sticky="ew")
        
        # DxDiag
        ctk.CTkButton(
            c5,
            text="🎮 Open DirectX Diagnostics (DxDiag)",
            command=lambda: self.run_cmd("start dxdiag.exe", "DxDiag")
        ).grid(row=3, column=2, padx=15, pady=(0, 15), sticky="ew")

    # --- 7. AI ASSISTANT FRAME ---
    def create_ai_assistant_frame(self):
        frame = ctk.CTkFrame(self, fg_color="transparent")
        self.frames["AiAssistant"] = frame
        
        frame.grid_rowconfigure(2, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        
        # Header Info
        header_container = ctk.CTkFrame(frame, fg_color="transparent")
        header_container.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        
        title = ctk.CTkLabel(header_container, text="Venkat Windows Tool Kit Assistant", font=ctk.CTkFont(size=20, weight="bold"))
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
                    "text": f"You are a helpful IT System administrator helper called Venkat Windows Tool Kit. A user is asking help for system diagnosis: '{prompt_text}'. Keep response concise and offer actionable Windows commands or tips."
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

    def create_winpe_builder_frame(self):
        frame = ctk.CTkFrame(self, fg_color="transparent")
        self.frames["WinPEBuilder"] = frame
        
        frame.grid_rowconfigure(8, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        
        # Title
        title = ctk.CTkLabel(frame, text="Windows PE Bootable USB Builder", font=ctk.CTkFont(size=20, weight="bold"))
        title.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")
        
        desc = ctk.CTkLabel(
            frame, 
            text="Configure and build a standalone bootable WinPE USB diagnostics drive. Embeds Venkat Windows Tool Kit tools to run offline.",
            text_color="gray",
            font=ctk.CTkFont(size=12)
        )
        desc.grid(row=1, column=0, padx=10, pady=(0, 20), sticky="w")
        
        # 1. Drive Selection Row
        drive_frame = ctk.CTkFrame(frame, fg_color="transparent")
        drive_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        
        lbl_drive = ctk.CTkLabel(drive_frame, text="Select Target USB Drive:", font=ctk.CTkFont(weight="bold"))
        lbl_drive.pack(side="left", padx=(0, 10))
        
        self.usb_dropdown = ctk.CTkOptionMenu(drive_frame, width=250, values=["Click Refresh to scan..."])
        self.usb_dropdown.pack(side="left", padx=(0, 10))
        
        btn_refresh = ctk.CTkButton(drive_frame, text="🔄 Refresh Drives", width=120, command=self.refresh_usb_drives)
        btn_refresh.pack(side="left")
        
        # 2. ISO Selection Row
        iso_frame = ctk.CTkFrame(frame, fg_color="transparent")
        iso_frame.grid(row=3, column=0, padx=10, pady=10, sticky="ew")
        
        lbl_iso = ctk.CTkLabel(iso_frame, text="Select WinPE Source ISO:", font=ctk.CTkFont(weight="bold"))
        lbl_iso.pack(side="left", padx=(0, 10))
        
        self.iso_entry = ctk.CTkEntry(iso_frame, placeholder_text="Browse to path of a WinPE ISO...", width=400)
        self.iso_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        btn_browse = ctk.CTkButton(iso_frame, text="📁 Browse ISO", width=120, command=self.browse_iso)
        btn_browse.pack(side="left")
        
        # 3. Checkbox options
        options_frame = ctk.CTkFrame(frame, fg_color="transparent")
        options_frame.grid(row=4, column=0, padx=10, pady=10, sticky="ew")
        
        self.embed_chk = ctk.CTkCheckBox(options_frame, text="Embed Venkat Windows Tool Kit diagnostic suite on USB root", hover=True)
        self.embed_chk.select()  # checked by default
        self.embed_chk.pack(side="left")
        
        # 4. Progress Area
        progress_frame = ctk.CTkFrame(frame, fg_color="transparent")
        progress_frame.grid(row=5, column=0, padx=10, pady=15, sticky="ew")
        
        self.winpe_progress = ctk.CTkProgressBar(progress_frame, orientation="horizontal", height=15)
        self.winpe_progress.set(0)
        self.winpe_progress.pack(fill="x", expand=True, pady=(0, 5))
        
        self.lbl_winpe_status = ctk.CTkLabel(progress_frame, text="Ready to build.", font=ctk.CTkFont(size=12))
        self.lbl_winpe_status.pack(side="left")
        
        # 5. Build Button Row
        build_btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
        build_btn_frame.grid(row=6, column=0, padx=10, pady=10, sticky="ew")
        
        self.btn_build_winpe = ctk.CTkButton(
            build_btn_frame, 
            text="🚀 Build Bootable USB", 
            height=45, 
            fg_color=["#10b981", "#059669"],
            hover_color=["#059669", "#047857"],
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self.start_winpe_build
        )
        self.btn_build_winpe.pack(fill="x", expand=True)
        
        # 6. Log Console
        lbl_logs = ctk.CTkLabel(frame, text="Build Output & Logs:", font=ctk.CTkFont(weight="bold"))
        lbl_logs.grid(row=7, column=0, padx=10, pady=(15, 5), sticky="w")
        
        self.winpe_log_text = ctk.CTkTextbox(frame, height=180, wrap="word", corner_radius=10, state="disabled")
        self.winpe_log_text.grid(row=8, column=0, padx=10, pady=(0, 10), sticky="nsew")
        
        # Initial drive scan
        self.refresh_usb_drives()

    def browse_iso(self):
        from tkinter import filedialog
        path = filedialog.askopenfilename(
            title="Select Windows PE ISO Image",
            filetypes=[("ISO Files", "*.iso")]
        )
        if path:
            self.iso_entry.delete(0, "end")
            self.iso_entry.insert(0, path)

    def refresh_usb_drives(self):
        drives = self.get_usb_drives()
        if not drives:
            drives = ["No USB Drives Detected"]
        
        self.usb_dropdown.configure(values=drives)
        self.usb_dropdown.set(drives[0])

    def get_usb_drives(self):
        try:
            ps_script = (
                "$drives = @(); "
                "$volumes = Get-Volume | Where-Object { $_.DriveLetter -and ($_.DriveType -eq 'Removable' -or (Get-Partition -DriveLetter $_.DriveLetter -ErrorAction SilentlyContinue | Get-Disk -ErrorAction SilentlyContinue | Where-Object { $_.BusType -eq 'USB' })) }; "
                "foreach ($v in $volumes) { "
                "    if ($v.DriveLetter) { "
                "        $label = $v.FileSystemLabel; "
                "        if (!$label) { $label = 'External Disk' }; "
                "        $drives += [PSCustomObject]@{ Letter = [string]$v.DriveLetter; Label = [string]$label; Type = 'Removable' }; "
                "    } "
                "}; "
                "$usbDisks = Get-Disk | Where-Object { $_.BusType -eq 'USB' -or $_.FriendlyName -like '*USB*' -or $_.FriendlyName -like '*SanDisk*' }; "
                "foreach ($d in $usbDisks) { "
                "    $parts = Get-Partition -DiskNumber $d.Number -ErrorAction SilentlyContinue | Where-Object { $_.DriveLetter }; "
                "    if (!$parts) { "
                "        $freeLetter = (69..90 | ForEach-Object { [char]$_ } | Where-Object { !(Get-Volume -DriveLetter $_ -ErrorAction SilentlyContinue) })[0]; "
                "        if ($freeLetter) { "
                "            $drives += [PSCustomObject]@{ Letter = [string]$freeLetter; Label = 'Unpartitioned: ' + $d.FriendlyName; Type = 'Removable' }; "
                "        } "
                "    } "
                "}; "
                "$drives | ConvertTo-Json"
            )
            cmd = ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_script]
            process = subprocess.run(cmd, capture_output=True, text=True)
            output = process.stdout.strip()
            if not output:
                return []
                
            data = json.loads(output)
            if not isinstance(data, list):
                data = [data]
                
            drives = []
            for vol in data:
                letter = vol.get("Letter")
                label = vol.get("Label") or "External Disk"
                dtype = vol.get("Type") or "Removable"
                if letter:
                    drives.append(f"{letter}: [{label}] ({dtype})")
            return drives
        except Exception as e:
            print(f"Error checking USB drives: {e}")
            return []

    def log_build(self, text):
        def append():
            self.winpe_log_text.configure(state="normal")
            self.winpe_log_text.insert("end", f"{text}\n")
            self.winpe_log_text.configure(state="disabled")
            self.winpe_log_text.see("end")
        self.after(0, append)

    def start_winpe_build(self):
        try:
            usb_val = self.usb_dropdown.get()
            if usb_val == "No USB Drives Detected" or not usb_val:
                self.show_toast("❌ Error: No valid target USB drive selected!")
                return
                
            iso_val = self.iso_entry.get().strip()
            if not iso_val or not os.path.exists(iso_val):
                self.show_toast("❌ Error: WinPE ISO file not found! Please browse to a valid file.")
                return
                
            usb_letter = usb_val.split(":")[0].strip()
            embed_tool = self.embed_chk.get()
            
            # Disable inputs
            self.btn_build_winpe.configure(state="disabled", text="🔨 Building USB...")
            self.usb_dropdown.configure(state="disabled")
            self.iso_entry.configure(state="disabled")
            self.embed_chk.configure(state="disabled")
            
            self.winpe_progress.set(0.0)
            self.lbl_winpe_status.configure(text="Build starting...")
            
            # Clear logs
            self.winpe_log_text.configure(state="normal")
            self.winpe_log_text.delete("1.0", "end")
            self.winpe_log_text.configure(state="disabled")
            
            # Start build thread
            threading.Thread(
                target=self.build_winpe_worker, 
                args=(usb_letter, iso_val, embed_tool), 
                daemon=True
            ).start()
        except Exception as e:
            import traceback
            err_msg = traceback.format_exc()
            self.show_toast(f"❌ Launch Error: {e}")
            from tkinter import messagebox
            messagebox.showerror("Launch Error", f"An error occurred while starting the build:\n\n{err_msg}")

    def build_winpe_worker(self, usb_letter, iso_path, embed_tool):
        self.log_build("=== WINPE USB BUILD STARTED ===")
        self.log_build(f"Target USB: {usb_letter}:")
        self.log_build(f"Source ISO: {iso_path}")
        self.log_build(f"Embed Tools: {embed_tool}")
        
        try:
            # Pre-check: Terminate any running diagnostic processes to release file locks
            self.log_build("\nChecking for running diagnostic processes to prevent file lock...")
            try:
                import psutil
                current_pid = os.getpid()
                for proc in psutil.process_iter(['pid', 'name']):
                    try:
                        pid = proc.info['pid']
                        name = proc.info['name']
                        if name:
                            name_lower = name.lower()
                            if name_lower == "main.exe" or (name_lower == "venkatpulse.exe" and pid != current_pid):
                                self.log_build(f"Terminating process {name} (PID: {pid})...")
                                proc.kill()
                                proc.wait(timeout=2)
                    except Exception:
                        pass
                time.sleep(1) # wait for process resource cleanup
            except Exception as e:
                self.log_build(f"Warning process termination: {e}")

            # Get the disk number and size of the target USB drive before doing anything
            disk_number = None
            disk_size_gb = 0
            try:
                # Query disk number of partition if it exists
                cmd = ["powershell", "-Command", f"(Get-Partition -DriveLetter {usb_letter} -ErrorAction SilentlyContinue).DiskNumber"]
                proc = subprocess.run(cmd, capture_output=True, text=True)
                if proc.returncode == 0 and proc.stdout.strip().isdigit():
                    disk_number = int(proc.stdout.strip())
                else:
                    # If partition does not exist, look for first USB physical disk
                    cmd_disk = ["powershell", "-Command", "Get-Disk | Where-Object { $_.BusType -eq 'USB' } | Select-Object -ExpandProperty Number"]
                    proc_disk = subprocess.run(cmd_disk, capture_output=True, text=True)
                    if proc_disk.returncode == 0:
                        numbers = [int(n) for n in proc_disk.stdout.split() if n.strip().isdigit()]
                        if numbers:
                            disk_number = numbers[0]
                
                if disk_number is not None:
                    cmd_size = ["powershell", "-Command", f"(Get-Disk -Number {disk_number}).Size"]
                    proc_size = subprocess.run(cmd_size, capture_output=True, text=True)
                    if proc_size.returncode == 0 and proc_size.stdout.strip().isdigit():
                        disk_size_gb = int(proc_size.stdout.strip()) / (1024 * 1024 * 1024)
            except Exception as e:
                self.log_build(f"Warning: could not resolve disk number: {e}")

            # 1. Format USB to FAT32
            self.after(0, lambda: self.lbl_winpe_status.configure(text="Step 1/5: Formatting USB drive..."))
            self.winpe_progress.set(0.1)
            self.log_build("\n[1/5] Formatting USB drive using Diskpart (partitioning to 32GB FAT32)...")
            
            format_success = False
            
            if disk_number is not None:
                self.log_build(f"USB Disk {disk_number} resolved (Size: {disk_size_gb:.1f} GB).")
                try:
                    size_param = "size=32000" if disk_size_gb > 32 else ""
                    script_path = os.path.join(os.environ["TEMP"], "diskpart_pulse.txt")
                    with open(script_path, "w") as f:
                        f.write(
                            f"select disk {disk_number}\n"
                            "clean\n"
                            "convert mbr\n"
                            f"create partition primary {size_param}\n"
                            "format fs=fat32 quick label=\"WINPE\"\n"
                            f"assign letter={usb_letter}\n"
                            "active\n"
                        )
                    self.log_build("> Running Diskpart script...")
                    proc = subprocess.run(f"diskpart /s \"{script_path}\"", shell=True, capture_output=True, text=True)
                    output_log_dp = (proc.stdout or "") + (proc.stderr or "")
                    self.log_build(output_log_dp)
                    
                    # Verify partition exists
                    test_part = subprocess.run(["powershell", "-Command", f"Get-Partition -DriveLetter {usb_letter} -ErrorAction SilentlyContinue"], capture_output=True, text=True)
                    if test_part.returncode == 0:
                        format_success = True
                    else:
                        self.log_build("Diskpart partition verification failed.")
                except Exception as dp_err:
                    self.log_build(f"Diskpart partitioning failed: {dp_err}")
            
            if not format_success:
                self.log_build("\n[!] Diskpart partitioning failed or disk number not resolved. Attempting standard quick format fallback...")
                fmt_cmd = f"format {usb_letter}: /FS:FAT32 /Q /V:WINPE /Y"
                self.log_build(f"> Running command: {fmt_cmd}")
                proc = subprocess.run(fmt_cmd, shell=True, capture_output=True, text=True)
                output_log = (proc.stdout or "") + (proc.stderr or "")
                self.log_build(output_log)
                
                format_failed = proc.returncode != 0 or "failed" in output_log.lower() or "too big" in output_log.lower()
                if format_failed:
                    self.log_build("\n[!] FAT32 formatting failed. Attempting fallback to NTFS formatting...")
                    fmt_cmd_ntfs = f"format {usb_letter}: /FS:NTFS /Q /V:WINPE /Y"
                    self.log_build(f"> Running command: {fmt_cmd_ntfs}")
                    proc = subprocess.run(fmt_cmd_ntfs, shell=True, capture_output=True, text=True)
                    output_log_ntfs = (proc.stdout or "") + (proc.stderr or "")
                    self.log_build(output_log_ntfs)
                    if proc.returncode != 0 or "failed" in output_log_ntfs.lower():
                        raise Exception(f"Format failed: {output_log_ntfs}")
            self.log_build("USB Formatted successfully.")
            
            # 2. Mount ISO
            self.after(0, lambda: self.lbl_winpe_status.configure(text="Step 2/5: Mounting source ISO image..."))
            self.winpe_progress.set(0.3)
            self.log_build("\n[2/5] Mounting source WinPE ISO...")
            
            mount_cmd = ["powershell", "-Command", f"(Mount-DiskImage -ImagePath '{iso_path}' -PassThru | Get-Volume).DriveLetter"]
            self.log_build(f"> Running: Mount-DiskImage")
            proc = subprocess.run(mount_cmd, capture_output=True, text=True)
            iso_letter = proc.stdout.strip()
            
            if not iso_letter or len(iso_letter) != 1:
                raise Exception(f"Failed to retrieve mounted ISO drive letter. Output: {proc.stdout}")
                
            self.log_build(f"ISO mounted successfully as drive letter: {iso_letter}:")
            
            # 3. Copy Files using Robocopy
            self.after(0, lambda: self.lbl_winpe_status.configure(text="Step 3/5: Copying WinPE boot files..."))
            self.winpe_progress.set(0.5)
            self.log_build("\n[3/5] Copying all files from ISO to USB via Robocopy (this might take a minute)...")
            
            # Robocopy E:\ F:\ /E /R:2 /W:2 /MT:8
            robocopy_cmd = f"robocopy {iso_letter}:\\ {usb_letter}:\\ /E /R:2 /W:2 /MT:8"
            self.log_build(f"> Running command: {robocopy_cmd}")
            # Robocopy exits with code 1 or 3 on success (which indicate files copied successfully)
            proc = subprocess.run(robocopy_cmd, shell=True, capture_output=True, text=True)
            self.log_build(f"Robocopy finished (Exit Code: {proc.returncode})")
            
            if proc.returncode > 7:  # Robocopy return codes 0-7 are success/minor warnings, >=8 is failure
                raise Exception(f"Robocopy failed with exit code {proc.returncode}: {proc.stderr}")
                
            self.log_build("Files copied successfully.")
            
            # Patch boot.wim on USB to auto-launch PrintPulse
            try:
                self.log_build("\nUpdating boot.wim on USB to auto-launch PrintPulse on boot...")
                usb_wim = os.path.join(f"{usb_letter}:\\", "sources", "boot.wim")
                mount_dir = os.path.join(os.environ.get("TEMP", "C:\\temp"), "PrintPulse_Mount")
                
                # Clean up old mount directory
                if os.path.exists(mount_dir):
                    subprocess.run(["dism.exe", "/Cleanup-Mountpoints"], capture_output=True)
                    shutil.rmtree(mount_dir, ignore_errors=True)
                os.makedirs(mount_dir, exist_ok=True)
                
                # Mount boot.wim
                self.log_build("> Mounting USB boot.wim...")
                mount_cmd = ["dism.exe", "/Mount-Image", f"/ImageFile:{usb_wim}", "/Index:1", f"/MountDir:{mount_dir}"]
                proc = subprocess.run(mount_cmd, capture_output=True, text=True)
                self.log_build(proc.stdout)
                
                # Update startnet.cmd
                startnet_path = os.path.join(mount_dir, "Windows", "System32", "startnet.cmd")
                if os.path.exists(startnet_path):
                    self.log_build("> Modifying startnet.cmd inside boot.wim...")
                    startnet_content = (
                        "wpeinit\n"
                        "@echo off\n"
                        "echo ========================================================\n"
                        "echo   Venkat Windows Tool Kit OS Recovery Suite - Auto-Launch\n"
                        "echo ========================================================\n"
                        "echo.\n"
                        "echo Searching for PrintPulse.exe on external drives...\n"
                        "for %%d in (C D E F G H I J K L M N O P Q R S T U V W X Y Z) do (\n"
                        "    if exist %%d:\\PrintPulse\\PrintPulse.exe (\n"
                        "        echo Found PrintPulse on drive %%d:\n"
                        "        cd /d %%d:\\PrintPulse\n"
                        "        PrintPulse.exe\n"
                        "        echo.\n"
                        "        echo PrintPulse exited. Error Level: %%errorlevel%%\n"
                        "        pause\n"
                        "    )\n"
                        "    if exist %%d:\\VenkatPulse\\VenkatPulse.exe (\n"
                        "        echo Found VenkatPulse on drive %%d:\n"
                        "        cd /d %%d:\\VenkatPulse\n"
                        "        VenkatPulse.exe\n"
                        "        echo.\n"
                        "        echo VenkatPulse exited. Error Level: %%errorlevel%%\n"
                        "        pause\n"
                        "    )\n"
                        ")\n"
                        "echo.\n"
                        "echo WARNING: PrintPulse.exe was not found or has exited.\n"
                        "echo You can run commands manually below.\n"
                        "cmd.exe\n"
                    )
                    with open(startnet_path, "w") as f:
                        f.write(startnet_content)
                        
                # Unmount and commit
                self.log_build("> Unmounting and committing USB boot.wim...")
                unmount_cmd = ["dism.exe", "/Unmount-Image", f"/MountDir:{mount_dir}", "/Commit"]
                proc = subprocess.run(unmount_cmd, capture_output=True, text=True)
                self.log_build(proc.stdout)
                
                # Clean up mount directory
                shutil.rmtree(mount_dir, ignore_errors=True)
                self.log_build("boot.wim successfully patched!")
            except Exception as patch_err:
                self.log_build(f"Warning: Failed to patch boot.wim for auto-launch: {patch_err}")
                self.log_build("You can still boot and run it manually from the Command Prompt.")
            
            # 4. Dismount ISO
            self.after(0, lambda: self.lbl_winpe_status.configure(text="Step 4/5: Dismounting ISO image..."))
            self.winpe_progress.set(0.8)
            self.log_build("\n[4/5] Dismounting WinPE ISO image...")
            
            dismount_cmd = ["powershell", "-Command", f"Dismount-DiskImage -ImagePath '{iso_path}'"]
            self.log_build(f"> Running: Dismount-DiskImage")
            proc = subprocess.run(dismount_cmd, capture_output=True, text=True)
            self.log_build("ISO Dismounted successfully.")
            
            # 5. Embed PrintPulse / Venkat Windows Tool Kit tools
            if embed_tool:
                self.after(0, lambda: self.lbl_winpe_status.configure(text="Step 5/5: Embedding tools..."))
                self.winpe_progress.set(0.9)
                self.log_build("\n[5/5] Embedding diagnostics suite to the USB...")
                
                # Check for any source executable
                src_exe = None
                for candidate in ["dist/PrintPulse.exe", "PrintPulse.exe", "dist/VenkatPulse.exe", "VenkatPulse.exe"]:
                    if os.path.exists(candidate):
                        src_exe = candidate
                        break
                        
                for folder_name, exe_name in [("PrintPulse", "PrintPulse.exe"), ("VenkatPulse", "VenkatPulse.exe")]:
                    dest_dir = os.path.join(f"{usb_letter}:\\", folder_name)
                    os.makedirs(dest_dir, exist_ok=True)
                    
                    if src_exe:
                        self.log_build(f"Copying {src_exe} to {dest_dir}\\{exe_name}...")
                        try:
                            shutil.copy2(src_exe, os.path.join(dest_dir, exe_name))
                        except Exception as ce:
                            self.log_build(f"Warning: Could not copy {exe_name} ({ce}).")
                    else:
                        self.log_build("Warning: Diagnostics executable not found. Please build PrintPulse first.")
                        
                    # Copy web server and assets
                    for file_name in ["main.exe", "index.html", "app.js", "styles.css", "logo.png"]:
                        src_path = os.path.join("dist", file_name) if os.path.exists(os.path.join("dist", file_name)) else file_name
                        if os.path.exists(src_path):
                            self.log_build(f"Copying {file_name} to {dest_dir}...")
                            try:
                                shutil.copy2(src_path, os.path.join(dest_dir, file_name))
                            except Exception as ce:
                                self.log_build(f"Warning: Could not copy {file_name} ({ce}).")
                
                self.log_build("Diagnostics suite embedded successfully!")
                
            self.winpe_progress.set(1.0)
            self.after(0, lambda: self.lbl_winpe_status.configure(text="Completed! WinPE bootable USB created successfully."))
            self.log_build("\n=== WINPE USB BUILD COMPLETED SUCCESSFULLY ===")
            self.after(0, lambda: self.show_toast("✅ Success: WinPE bootable USB created successfully!"))
            
        except Exception as e:
            self.winpe_progress.set(0.0)
            self.after(0, lambda: self.lbl_winpe_status.configure(text="Failed! See logs."))
            self.log_build(f"\n❌ ERROR: {e}")
            self.log_build("\n=== WINPE USB BUILD FAILED ===")
            self.after(0, lambda: self.show_toast(f"❌ Error: Build failed: {e}"))
            
            # Make sure we try to dismount the ISO in case of error
            try:
                subprocess.run(["powershell", "-Command", f"Dismount-DiskImage -ImagePath '{iso_path}'"], capture_output=True)
            except:
                pass
                
        finally:
            # Re-enable inputs
            def enable_inputs():
                self.btn_build_winpe.configure(state="normal", text="🚀 Build Bootable USB")
                self.usb_dropdown.configure(state="normal")
                self.iso_entry.configure(state="normal")
                self.embed_chk.configure(state="normal")
            self.after(0, enable_inputs)

    def create_disk_security_frame(self):
        frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.frames["DiskSecurity"] = frame
        
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=1)
        
        title = ctk.CTkLabel(frame, text="Disk Management, Boot Recovery & Security Suite", font=ctk.CTkFont(size=20, weight="bold"))
        title.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="w")
        
        # -------------------------------------------------------------
        # Left Column: Disk Converters, Passwords, and Boot Repairs
        # -------------------------------------------------------------
        left_column = ctk.CTkFrame(frame, fg_color="transparent")
        left_column.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        left_column.grid_columnconfigure(0, weight=1)
        
        # Panel 1: Windows Password Recovery (SAM / Utilman Bypass)
        p1 = ctk.CTkFrame(left_column, corner_radius=10)
        p1.grid(row=0, column=0, padx=5, pady=8, sticky="ew")
        p1.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(p1, text="🔑 Offline Windows Password Recovery", font=ctk.CTkFont(size=14, weight="bold")).grid(row=0, column=0, padx=15, pady=(10, 5), sticky="w")
        ctk.CTkLabel(p1, text="Bypasses Windows Login screen by replacing Utility Manager (Ease of Access) with cmd.exe.", text_color="gray", font=ctk.CTkFont(size=11)).grid(row=1, column=0, padx=15, pady=(0, 10), sticky="w")
        
        p1_action_frame = ctk.CTkFrame(p1, fg_color="transparent")
        p1_action_frame.grid(row=2, column=0, padx=15, pady=(0, 15), sticky="ew")
        
        ctk.CTkLabel(p1_action_frame, text="Windows Drive:").pack(side="left", padx=(0, 5))
        self.win_drive_dropdown = ctk.CTkOptionMenu(p1_action_frame, width=90, values=["C"])
        self.win_drive_dropdown.pack(side="left", padx=(0, 10))
        
        btn_apply_bypass = ctk.CTkButton(
            p1_action_frame, 
            text="Apply Bypass", 
            width=110,
            fg_color="#b91c1c",
            hover_color="#991b1b",
            font=ctk.CTkFont(weight="bold"),
            command=lambda: self.apply_utilman_bypass(self.win_drive_dropdown.get())
        )
        btn_apply_bypass.pack(side="left", padx=(0, 5))
        
        btn_restore_bypass = ctk.CTkButton(
            p1_action_frame, 
            text="Restore Original", 
            width=110,
            command=lambda: self.restore_utilman(self.win_drive_dropdown.get())
        )
        btn_restore_bypass.pack(side="left")
        
        # Panel 2: Lossless Disk File System & Partition Style Converters
        p2 = ctk.CTkFrame(left_column, corner_radius=10)
        p2.grid(row=1, column=0, padx=5, pady=8, sticky="ew")
        p2.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(p2, text="💽 Lossless Drive & Disk Style Converters", font=ctk.CTkFont(size=14, weight="bold")).grid(row=0, column=0, padx=15, pady=(10, 5), sticky="w")
        ctk.CTkLabel(p2, text="Perform conversions of file systems and partition tables without losing any data.", text_color="gray", font=ctk.CTkFont(size=11)).grid(row=1, column=0, padx=15, pady=(0, 10), sticky="w")
        
        # Section A: FAT32 to NTFS
        fs_frame = ctk.CTkFrame(p2, fg_color="transparent")
        fs_frame.grid(row=2, column=0, padx=15, pady=(0, 10), sticky="ew")
        ctk.CTkLabel(fs_frame, text="FAT32 Drive Letter:").pack(side="left", padx=(0, 5))
        self.fat32_drive_dropdown = ctk.CTkOptionMenu(fs_frame, width=90, values=["D"])
        self.fat32_drive_dropdown.pack(side="left", padx=(0, 10))
        btn_conv_fs = ctk.CTkButton(
            fs_frame,
            text="Convert to NTFS",
            command=lambda: self.run_fat32_to_ntfs(self.fat32_drive_dropdown.get())
        )
        btn_conv_fs.pack(side="left", fill="x", expand=True)
        
        # Section B: MBR to GPT
        pt_frame = ctk.CTkFrame(p2, fg_color="transparent")
        pt_frame.grid(row=3, column=0, padx=15, pady=(0, 15), sticky="ew")
        ctk.CTkLabel(pt_frame, text="Select Disk Style:").pack(side="left", padx=(0, 5))
        self.mbr_disk_dropdown = ctk.CTkOptionMenu(pt_frame, width=150, values=["Disk 0"])
        self.mbr_disk_dropdown.pack(side="left", padx=(0, 10))
        btn_conv_pt = ctk.CTkButton(
            pt_frame,
            text="Convert MBR to GPT",
            fg_color="#059669",
            hover_color="#047857",
            font=ctk.CTkFont(weight="bold"),
            command=lambda: self.run_mbr_to_gpt(self.mbr_disk_dropdown.get())
        )
        btn_conv_pt.pack(side="left", fill="x", expand=True)
        
        # Panel 3: Boot Sector & BCD Recovery Tools
        p3 = ctk.CTkFrame(left_column, corner_radius=10)
        p3.grid(row=2, column=0, padx=5, pady=8, sticky="ew")
        p3.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(p3, text="🛠️ Boot Sector & BCD Recovery Suite", font=ctk.CTkFont(size=14, weight="bold")).grid(row=0, column=0, padx=15, pady=(10, 5), sticky="w")
        ctk.CTkLabel(p3, text="Repair corrupt Boot Configuration Data (BCD), MBR boot records, and recreate bootloaders.", text_color="gray", font=ctk.CTkFont(size=11)).grid(row=1, column=0, padx=15, pady=(0, 10), sticky="w")
        
        # Simple commands
        p3_cmds_frame = ctk.CTkFrame(p3, fg_color="transparent")
        p3_cmds_frame.grid(row=2, column=0, padx=15, pady=(0, 10), sticky="ew")
        p3_cmds_frame.grid_columnconfigure(0, weight=1)
        p3_cmds_frame.grid_columnconfigure(1, weight=1)
        p3_cmds_frame.grid_columnconfigure(2, weight=1)
        
        ctk.CTkButton(p3_cmds_frame, text="bootrec /fixmbr", command=lambda: self.run_boot_repair("fixmbr", None)).grid(row=0, column=0, padx=3, pady=5, sticky="ew")
        ctk.CTkButton(p3_cmds_frame, text="bootrec /fixboot", command=lambda: self.run_boot_repair("fixboot", None)).grid(row=0, column=1, padx=3, pady=5, sticky="ew")
        ctk.CTkButton(p3_cmds_frame, text="rebuildbcd", command=lambda: self.run_boot_repair("rebuildbcd", None)).grid(row=0, column=2, padx=3, pady=5, sticky="ew")
        
        # BCDBoot command builder
        p3_bcdboot_frame = ctk.CTkFrame(p3, fg_color="transparent")
        p3_bcdboot_frame.grid(row=3, column=0, padx=15, pady=(5, 15), sticky="ew")
        
        ctk.CTkLabel(p3_bcdboot_frame, text="Windows Part:").pack(side="left", padx=(0, 3))
        self.bcd_win_dropdown = ctk.CTkOptionMenu(p3_bcdboot_frame, width=70, values=["C"])
        self.bcd_win_dropdown.pack(side="left", padx=(0, 8))
        
        ctk.CTkLabel(p3_bcdboot_frame, text="Boot Part:").pack(side="left", padx=(0, 3))
        self.bcd_boot_dropdown = ctk.CTkOptionMenu(p3_bcdboot_frame, width=70, values=["S"])
        self.bcd_boot_dropdown.pack(side="left", padx=(0, 8))
        
        btn_bcdboot = ctk.CTkButton(
            p3_bcdboot_frame,
            text="Recreate Bootloader (BCDBoot)",
            fg_color="#059669",
            hover_color="#047857",
            font=ctk.CTkFont(weight="bold"),
            command=lambda: self.run_boot_repair("bcdboot", self.bcd_win_dropdown.get(), self.bcd_boot_dropdown.get())
        )
        btn_bcdboot.pack(side="left", fill="x", expand=True)
        
        # -------------------------------------------------------------
        # Right Column: OS Installation Error Fixer
        # -------------------------------------------------------------
        right_column = ctk.CTkFrame(frame, fg_color="transparent")
        right_column.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
        right_column.grid_columnconfigure(0, weight=1)
        
        p4 = ctk.CTkFrame(right_column, corner_radius=10)
        p4.grid(row=0, column=0, padx=5, pady=8, sticky="nsew")
        p4.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(p4, text="🚀 OS Installation Error & Setup Fixer", font=ctk.CTkFont(size=15, weight="bold")).grid(row=0, column=0, padx=15, pady=(12, 5), sticky="w")
        ctk.CTkLabel(p4, text="Select a common error encountered during Windows Setup to see diagnostics and launch fixes.", text_color="gray", font=ctk.CTkFont(size=11)).grid(row=1, column=0, padx=15, pady=(0, 15), sticky="w")
        
        # Error Dropdown Selection
        self.os_errors = {
            "Select an installation error to troubleshoot...": {
                "desc": "Select an error from the dropdown to see detailed causes, guides, and automated scripting solutions.",
                "fix_type": None
            },
            "MBR Mismatch: EFI system requires GPT partition style": {
                "desc": "Cause: You booted the Windows installer in UEFI mode, but your hard drive is partitioned in the older MBR style.\n\n"
                        "Solution 1 (Lossless): Use our 'Convert MBR to GPT' tool on the left to convert the disk without losing any files.\n\n"
                        "Solution 2 (Destructive): Wipe the disk and convert to GPT via Diskpart. This will delete all partitions and data on the selected disk.",
                "fix_type": "wipe_gpt"
            },
            "GPT Mismatch: Legacy BIOS requires MBR partition style": {
                "desc": "Cause: You booted the Windows installer in Legacy/CSM BIOS mode, but your hard drive is partitioned in the GPT style.\n\n"
                        "Solution: Wipe the disk and convert to MBR via Diskpart. This will delete all partitions and data on the selected disk.",
                "fix_type": "wipe_mbr"
            },
            "Disk contains dynamic volumes (dynamic disks not supported)": {
                "desc": "Cause: The target hard drive was converted to a dynamic disk, which Windows Setup cannot install to.\n\n"
                        "Solution: Wipe the disk and convert it back to a basic partition style. WARNING: This deletes all data on the disk.",
                "fix_type": "wipe_basic"
            },
            "Windows is unable to install (Error 0x80300024)": {
                "desc": "Cause: This can happen if multiple hard drives are plugged in, causing drive number confusion, or if the partition layout is corrupt.\n\n"
                        "Solution 1: Unplug all other internal/external hard drives except the target drive.\n\n"
                        "Solution 2: Run a quick Diskpart clean on the target disk to reset its partition structure.",
                "fix_type": "wipe_clean"
            },
            "Windows cannot install required files (Error 0x80070570)": {
                "desc": "Cause: This error indicates file corruption, usually caused by bad sectors on the hard drive, corrupted USB installation files, or faulty RAM.\n\n"
                        "Solution 1: Run a disk integrity check (chkdsk /f) on the target partition using the tool below to repair system sectors.\n\n"
                        "Solution 2: Re-create your Windows bootable USB drive using a new USB stick or download.",
                "fix_type": "chkdsk"
            }
        }
        
        self.error_dropdown = ctk.CTkOptionMenu(
            p4, 
            values=list(self.os_errors.keys()),
            command=self.on_installation_error_select
        )
        self.error_dropdown.grid(row=2, column=0, padx=15, pady=(0, 15), sticky="ew")
        
        # Details Panel
        self.details_textbox = ctk.CTkTextbox(p4, height=180, wrap="word", corner_radius=10)
        self.details_textbox.grid(row=3, column=0, padx=15, pady=(0, 15), sticky="ew")
        self.details_textbox.insert("1.0", "Select an error from the dropdown to see detailed causes, guides, and automated scripting solutions.")
        self.details_textbox.configure(state="disabled")
        
        # Automated Fix Inputs Row
        self.fix_inputs_frame = ctk.CTkFrame(p4, fg_color="transparent")
        self.fix_inputs_frame.grid(row=4, column=0, padx=15, pady=(0, 15), sticky="ew")
        
        ctk.CTkLabel(self.fix_inputs_frame, text="Target Disk:").pack(side="left", padx=(0, 5))
        self.install_disk_dropdown = ctk.CTkOptionMenu(self.fix_inputs_frame, width=120, values=["Disk 0"])
        self.install_disk_dropdown.pack(side="left", padx=(0, 15))
        
        ctk.CTkLabel(self.fix_inputs_frame, text="Partition:").pack(side="left", padx=(0, 5))
        self.install_partition_dropdown = ctk.CTkOptionMenu(self.fix_inputs_frame, width=90, values=["C"])
        self.install_partition_dropdown.pack(side="left")
        
        # Apply Fix Button
        self.btn_run_install_fix = ctk.CTkButton(
            p4,
            text="🔨 Apply Automated Setup Fix",
            height=40,
            fg_color="#b91c1c",
            hover_color="#991b1b",
            font=ctk.CTkFont(weight="bold"),
            command=self.run_installation_error_fix
        )
        self.btn_run_install_fix.grid(row=5, column=0, padx=15, pady=(0, 15), sticky="ew")
        
        # Panel 5: System Recovery & Boot Management
        p5 = ctk.CTkFrame(right_column, corner_radius=10)
        p5.grid(row=1, column=0, padx=5, pady=8, sticky="ew")
        p5.grid_columnconfigure(0, weight=1)
        p5.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(p5, text="💾 System Recovery & Boot Management", font=ctk.CTkFont(size=14, weight="bold")).grid(row=0, column=0, columnspan=2, padx=15, pady=(10, 5), sticky="w")
        ctk.CTkLabel(p5, text="Manage Windows Recovery Environment (WinRE) and advanced boot styles.", text_color="gray", font=ctk.CTkFont(size=11)).grid(row=1, column=0, columnspan=2, padx=15, pady=(0, 10), sticky="w")
        
        btn_winre_enable = ctk.CTkButton(
            p5,
            text="Enable WinRE",
            command=lambda: self.run_system_recovery_command("winre_enable")
        )
        btn_winre_enable.grid(row=2, column=0, padx=10, pady=5, sticky="ew")
        
        btn_winre_status = ctk.CTkButton(
            p5,
            text="Check WinRE Status",
            command=lambda: self.run_system_recovery_command("winre_status")
        )
        btn_winre_status.grid(row=2, column=1, padx=10, pady=5, sticky="ew")
        
        btn_safemode_on = ctk.CTkButton(
            p5,
            text="Boot to Safe Mode",
            fg_color="#b91c1c",
            hover_color="#991b1b",
            font=ctk.CTkFont(weight="bold"),
            command=lambda: self.run_system_recovery_command("safemode_on")
        )
        btn_safemode_on.grid(row=3, column=0, padx=10, pady=5, sticky="ew")
        
        btn_safemode_off = ctk.CTkButton(
            p5,
            text="Restore Normal Boot",
            fg_color="#059669",
            hover_color="#047857",
            font=ctk.CTkFont(weight="bold"),
            command=lambda: self.run_system_recovery_command("safemode_off")
        )
        btn_safemode_off.grid(row=3, column=1, padx=10, pady=5, sticky="ew")
        
        # Initial scan & population
        self.refresh_disk_security_selectors()

    def create_standalone_tools_frame(self):
        frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.frames["StandaloneTools"] = frame
        
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=1)
        
        title = ctk.CTkLabel(frame, text="🧰 Standalone Diagnostic & Recovery Utilities", font=ctk.CTkFont(size=20, weight="bold"))
        title.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="w")
        
        subtitle = ctk.CTkLabel(frame, text="Quick-launch portable diagnostics, hardware monitors, and file/password recovery tools.", text_color="gray", font=ctk.CTkFont(size=12))
        subtitle.grid(row=1, column=0, columnspan=2, padx=10, pady=(0, 15), sticky="w")
        
        self.tool_buttons = {}
        
        left_col = ctk.CTkFrame(frame, fg_color="transparent")
        left_col.grid(row=2, column=0, padx=10, pady=5, sticky="nsew")
        left_col.grid_columnconfigure(0, weight=1)
        
        right_col = ctk.CTkFrame(frame, fg_color="transparent")
        right_col.grid(row=2, column=1, padx=10, pady=5, sticky="nsew")
        right_col.grid_columnconfigure(0, weight=1)
        
        tools_list = [
            ("NTPWEdit Password Editor", "recovery", "NTPWEdit\\ntpwedit64.exe", "NTPWEdit", "Edit Windows local SAM passwords offline."),
            ("Recuva Data Recovery", "recovery", "Recuva\\recuva64.exe", "Recuva", "Recover deleted files, photos, and archives."),
            ("WizTree Disk Space Analyzer", "diag", "WizTree\\WizTree64.exe", "WizTree", "Ultra-fast disk usage visualizer."),
            ("CPU-Z System Hardware Info", "diag", "CPU-Z\\cpuz_x64.exe", "CPU-Z", "Detailed processor and RAM specifications."),
            ("HWMonitor Sensor Monitor", "diag", "HWMonitor\\HWMonitor_x64.exe", "HWMonitor", "Live temperature, voltage, and fan speed monitor."),
            ("CrystalDiskInfo HDD/SSD Health", "diag", "CrystalDiskInfo\\CrystalDiskInfoPortable.exe", "CrystalDiskInfo", "Check hard drive S.M.A.R.T. health and temperature."),
            ("Angry IP Scanner", "net", "Angry_IP_Scanner.exe", "AngryIPScanner", "Network device and IP scanner."),
            ("Notepad++ Code Editor", "net", "NotepadPlusPlus\\notepad++.exe", "NotepadPlusPlus", "Advanced portable text and code editor."),
            ("Rufus USB Formatter", "net", "Rufus_Portable.exe", "Rufus", "Create bootable USB drives from ISO files.")
        ]
        
        self.panels = {
            "recovery": ctk.CTkFrame(left_col, corner_radius=10),
            "net": ctk.CTkFrame(left_col, corner_radius=10),
            "diag": ctk.CTkFrame(right_col, corner_radius=10)
        }
        
        self.panels["recovery"].pack(fill="x", pady=8)
        self.panels["net"].pack(fill="x", pady=8)
        self.panels["diag"].pack(fill="both", expand=True, pady=8)
        
        ctk.CTkLabel(self.panels["recovery"], text="🔑 Password & File Recovery", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=15, pady=(10, 5))
        ctk.CTkLabel(self.panels["net"], text="🌐 Network & Text Utilities", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=15, pady=(10, 5))
        ctk.CTkLabel(self.panels["diag"], text="📊 Hardware & Disk Diagnostics", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=15, pady=(10, 5))
        
        for name, cat, rel_path, dl_key, desc in tools_list:
            panel = self.panels[cat]
            
            tool_frame = ctk.CTkFrame(panel, fg_color="transparent")
            tool_frame.pack(fill="x", padx=15, pady=8)
            
            text_frame = ctk.CTkFrame(tool_frame, fg_color="transparent")
            text_frame.pack(side="left", fill="x", expand=True)
            
            lbl_name = ctk.CTkLabel(text_frame, text=name, font=ctk.CTkFont(size=12, weight="bold"))
            lbl_name.pack(anchor="w")
            lbl_desc = ctk.CTkLabel(text_frame, text=desc, text_color="gray", font=ctk.CTkFont(size=11))
            lbl_desc.pack(anchor="w")
            
            btn = ctk.CTkButton(tool_frame, width=120, text="Launch")
            btn.pack(side="right", padx=(10, 0))
            
            self.tool_buttons[dl_key] = {
                "button": btn,
                "rel_path": rel_path,
                "dl_key": dl_key,
                "name": name
            }
            
        self.refresh_standalone_tools_ui()
        
    def refresh_standalone_tools_ui(self):
        base_dir = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
        tools_dir = os.path.join(base_dir, "tools")
        
        for dl_key, info in self.tool_buttons.items():
            full_path = os.path.join(tools_dir, info["rel_path"])
            btn = info["button"]
            
            if os.path.exists(full_path):
                btn.configure(
                    text="🚀 Launch",
                    fg_color="#059669",
                    hover_color="#047857",
                    command=lambda p=full_path, n=info["name"]: self.launch_standalone_tool(p, n)
                )
            else:
                btn.configure(
                    text="📥 Download",
                    fg_color="#d97706",
                    hover_color="#b45309",
                    command=lambda k=dl_key: self.start_tool_download(k)
                )
                
    def launch_standalone_tool(self, path, name):
        self.log_build(f"Launching {name} from {path}...")
        try:
            # Run in a detached process so it doesn't block the GUI
            subprocess.Popen(f'"{path}"', shell=True)
        except Exception as e:
            self.show_toast(f"❌ Failed to launch {name}: {e}")
            
    def start_tool_download(self, tool_name):
        threading.Thread(target=self.download_tool_worker, args=(tool_name,), daemon=True).start()
        
    def download_tool_worker(self, tool_name):
        self.show_toast(f"⏳ Downloading {tool_name}...")
        try:
            import urllib.request
            import ssl
            import zipfile
            context = ssl._create_unverified_context()
            
            base_dir = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
            tools_dir = os.path.join(base_dir, "tools")
            os.makedirs(tools_dir, exist_ok=True)
            
            links = {
                "NTPWEdit": ("http://cdslow.org.ru/files/ntpwedit/ntpwed07.zip", "ntpwedit.zip", "NTPWEdit"),
                "CrystalDiskInfo": ("https://downloads.sourceforge.net/portableapps/CrystalDiskInfoPortable_9.3.0.paf.exe", "cdi_setup.exe", "CrystalDiskInfo"),
                "WizTree": ("https://diskanalyzer.com/files/wiztree_4_20_portable.zip", "wiztree.zip", "WizTree"),
                "CPU-Z": ("https://download.cpuid.com/cpu-z/cpu-z_2.09-en.zip", "cpuz.zip", "CPU-Z"),
                "HWMonitor": ("https://download.cpuid.com/hwmonitor/hwmonitor_1.52.zip", "hwmonitor.zip", "HWMonitor"),
                "NotepadPlusPlus": ("https://github.com/notepad-plus-plus/notepad-plus-plus/releases/download/v8.6.8/npp.8.6.8.portable.x64.zip", "npp.zip", "NotepadPlusPlus"),
                "Recuva": ("https://download.ccleaner.com/rcsetup154.exe", "rcsetup.exe", "Recuva"),
                "Rufus": ("https://github.com/pbatard/rufus/releases/download/v4.5/rufus-4.5.exe", "Rufus_Portable.exe", ""),
                "AngryIPScanner": ("https://github.com/angryip/ipscan/releases/download/3.9.1/ipscan-win64-3.9.1.exe", "Angry_IP_Scanner.exe", "")
            }
            
            if tool_name not in links:
                return
                
            url, filename, folder = links[tool_name]
            file_path = os.path.join(tools_dir, filename)
            
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, context=context) as response:
                with open(file_path, 'wb') as out_file:
                    out_file.write(response.read())
            
            if folder:
                dest_dir = os.path.join(tools_dir, folder)
                os.makedirs(dest_dir, exist_ok=True)
                
                if filename.endswith(".zip"):
                    with zipfile.ZipFile(file_path, 'r') as zip_ref:
                        zip_ref.extractall(dest_dir)
                    os.remove(file_path)
                elif filename.endswith(".exe") and tool_name == "Recuva":
                    sz_path = "C:\\Program Files\\7-Zip\\7z.exe"
                    if os.path.exists(sz_path):
                        subprocess.run(f'"{sz_path}" x "{file_path}" -o"{dest_dir}" -y', shell=True, capture_output=True)
                    os.remove(file_path)
                elif filename.endswith(".exe") and tool_name == "CrystalDiskInfo":
                    sz_path = "C:\\Program Files\\7-Zip\\7z.exe"
                    if os.path.exists(sz_path):
                        subprocess.run(f'"{sz_path}" x "{file_path}" -o"{dest_dir}" -y', shell=True, capture_output=True)
                    os.remove(file_path)
            
            self.show_toast(f"✅ {tool_name} downloaded successfully!")
            self.after(0, self.refresh_standalone_tools_ui)
        except Exception as e:
            self.show_toast(f"❌ Failed to download {tool_name}: {e}")

    def refresh_disk_security_selectors(self):
        # 1. Detect drives containing Windows OS
        win_drives = self.detect_windows_drives()
        if not win_drives:
            win_drives = ["C", "D", "E"]
        self.win_drive_dropdown.configure(values=win_drives)
        self.win_drive_dropdown.set(win_drives[0])
        
        # 2. Get all drive letters currently connected
        all_drives = self.get_all_drive_letters()
        if not all_drives:
            all_drives = ["C", "D", "E"]
        self.fat32_drive_dropdown.configure(values=all_drives)
        self.fat32_drive_dropdown.set(all_drives[0])
        
        self.bcd_win_dropdown.configure(values=all_drives)
        self.bcd_win_dropdown.set(all_drives[0])
        
        self.bcd_boot_dropdown.configure(values=all_drives)
        self.bcd_boot_dropdown.set(all_drives[0])
        
        self.install_partition_dropdown.configure(values=all_drives)
        self.install_partition_dropdown.set(all_drives[0])
        
        # 3. Get system physical disks
        disks = self.get_system_disks()
        if not disks:
            disks = ["Disk 0: Local Disk (MBR)"]
        self.mbr_disk_dropdown.configure(values=disks)
        self.mbr_disk_dropdown.set(disks[0])
        
        self.install_disk_dropdown.configure(values=disks)
        self.install_disk_dropdown.set(disks[0])

    def detect_windows_drives(self):
        import string
        drives = []
        for letter in string.ascii_uppercase:
            path = f"{letter}:\\Windows\\System32\\utilman.exe"
            if os.path.exists(path):
                drives.append(letter)
        return drives

    def get_all_drive_letters(self):
        import string
        drives = []
        for letter in string.ascii_uppercase:
            if os.path.exists(f"{letter}:\\"):
                drives.append(letter)
        return drives

    def get_system_disks(self):
        try:
            cmd = ["powershell", "-Command", "Get-Disk | Select-Object Number, FriendlyName, PartitionStyle | ConvertTo-Json"]
            process = subprocess.run(cmd, capture_output=True, text=True)
            output = process.stdout.strip()
            if not output:
                return []
            data = json.loads(output)
            if not isinstance(data, list):
                data = [data]
            disks = []
            for d in data:
                num = d.get("Number")
                name = d.get("FriendlyName") or "Disk"
                style = d.get("PartitionStyle") or "MBR"
                disks.append(f"Disk {num}: {name} ({style})")
            return disks
        except Exception as e:
            print(f"Error checking disks: {e}")
            return []

    def apply_utilman_bypass(self, win_drive):
        if not win_drive or len(win_drive) != 1:
            self.show_toast("❌ Error: Select a valid Windows drive letter!")
            return
            
        def worker():
            try:
                utilman_path = f"{win_drive}:\\Windows\\System32\\utilman.exe"
                cmd_path = f"{win_drive}:\\Windows\\System32\\cmd.exe"
                utilman_bak = f"{win_drive}:\\Windows\\System32\\utilman.exe.bak"
                
                if not os.path.exists(utilman_path):
                    self.show_toast(f"❌ Error: utilman.exe not found on {win_drive}:")
                    return
                    
                self.show_toast("Taking ownership of utilman.exe...")
                # Take ownership and grant permission (TrustedInstaller override)
                subprocess.run(f'takeown /f "{utilman_path}"', shell=True, capture_output=True)
                subprocess.run(f'icacls "{utilman_path}" /grant administrators:F', shell=True, capture_output=True)
                
                if os.path.exists(utilman_bak):
                    os.remove(utilman_bak)
                    
                os.rename(utilman_path, utilman_bak)
                shutil.copy2(cmd_path, utilman_path)
                self.show_toast(f"✅ Success: utilman.exe bypass applied on drive {win_drive}:")
            except Exception as e:
                self.show_toast(f"❌ Error: {e}")
        
        threading.Thread(target=worker, daemon=True).start()

    def restore_utilman(self, win_drive):
        if not win_drive or len(win_drive) != 1:
            self.show_toast("❌ Error: Select a valid Windows drive letter!")
            return
            
        def worker():
            try:
                utilman_path = f"{win_drive}:\\Windows\\System32\\utilman.exe"
                utilman_bak = f"{win_drive}:\\Windows\\System32\\utilman.exe.bak"
                
                if not os.path.exists(utilman_bak):
                    self.show_toast(f"❌ Error: utilman.exe.bak not found on {win_drive}:")
                    return
                    
                if os.path.exists(utilman_path):
                    os.remove(utilman_path)
                    
                os.rename(utilman_bak, utilman_path)
                self.show_toast(f"✅ Success: original utilman.exe restored on drive {win_drive}:")
            except Exception as e:
                self.show_toast(f"❌ Error: {e}")
                
        threading.Thread(target=worker, daemon=True).start()

    def run_fat32_to_ntfs(self, drive_letter):
        if not drive_letter or len(drive_letter) != 1:
            self.show_toast("❌ Error: Select a target drive letter!")
            return
        # convert D: /FS:NTFS
        self.run_cmd(f"start cmd /k convert {drive_letter}: /FS:NTFS", f"FAT32 to NTFS Converter on {drive_letter}:")

    def run_mbr_to_gpt(self, disk_info):
        if not disk_info or "Disk" not in disk_info:
            self.show_toast("❌ Error: Select a target disk!")
            return
        disk_num = disk_info.split(":")[0].replace("Disk", "").strip()
        # MBR2GPT lossless conversion
        self.run_cmd(f"start cmd /k mbr2gpt /convert /disk:{disk_num} /allowFullOS", f"MBR to GPT Converter on Disk {disk_num}")

    def run_boot_repair(self, action, win_drive, boot_drive=None):
        if action == "fixmbr":
            self.run_cmd("start cmd /k bootrec /fixmbr", "Write MBR")
        elif action == "fixboot":
            self.run_cmd("start cmd /k bootrec /fixboot", "Write Boot Sector")
        elif action == "rebuildbcd":
            self.run_cmd("start cmd /k bootrec /rebuildbcd", "Rebuild BCD")
        elif action == "bcdboot":
            if not win_drive or len(win_drive) != 1:
                self.show_toast("❌ Error: Select target Windows drive!")
                return
            if not boot_drive or len(boot_drive) != 1:
                self.show_toast("❌ Error: Select boot target partition drive!")
                return
            # bcdboot C:\Windows /s S: /f ALL
            cmd = f"start cmd /k bcdboot {win_drive}:\\Windows /s {boot_drive}: /f ALL"
            self.run_cmd(cmd, "BCDBoot Recovery")

    def on_installation_error_select(self, val):
        info = self.os_errors.get(val)
        if info:
            self.details_textbox.configure(state="normal")
            self.details_textbox.delete("1.0", "end")
            self.details_textbox.insert("1.0", info.get("desc", ""))
            self.details_textbox.configure(state="disabled")

    def run_installation_error_fix(self):
        err = self.error_dropdown.get()
        info = self.os_errors.get(err)
        if not info or not info.get("fix_type"):
            self.show_toast("❌ Error: No automated fix for this selection.")
            return
            
        fix_type = info["fix_type"]
        
        if fix_type in ["wipe_gpt", "wipe_mbr", "wipe_basic", "wipe_clean"]:
            disk_info = self.install_disk_dropdown.get()
            if not disk_info or "Disk" not in disk_info:
                self.show_toast("❌ Error: Select a target physical disk!")
                return
            disk_num = disk_info.split(":")[0].replace("Disk", "").strip()
            
            from tkinter import messagebox
            confirm = messagebox.askyesno(
                "CRITICAL WARNING",
                f"You are about to completely WIPE Disk {disk_num} via Diskpart.\n"
                "All partition structures, volumes, and files on this disk will be permanently DELETED.\n\n"
                "Do you want to proceed?",
                icon="warning"
            )
            if not confirm:
                return
                
            style = "gpt" if fix_type == "wipe_gpt" else ("mbr" if fix_type == "wipe_mbr" else ("basic" if fix_type == "wipe_basic" else None))
            self.run_diskpart_wipe_convert(disk_num, style)
            
        elif fix_type == "chkdsk":
            drive = self.install_partition_dropdown.get()
            if not drive or len(drive) != 1:
                self.show_toast("❌ Error: Select a target partition drive letter!")
                return
            self.run_cmd(f"start cmd /k chkdsk {drive}: /f", f"chkdsk /f on {drive}:")

    def run_diskpart_wipe_convert(self, disk_num, style=None):
        import tempfile
        script_content = f"select disk {disk_num}\nclean\n"
        if style == "gpt":
            script_content += "convert gpt\n"
        elif style == "mbr" or style == "basic":
            script_content += "convert mbr\n"
            
        try:
            fd, path = tempfile.mkstemp(suffix=".txt", prefix="diskpart_")
            with os.open(fd, os.O_WRONLY | os.O_CREAT) as f:
                os.write(f, script_content.encode('utf-8'))
            
            # Execute diskpart with script
            self.run_cmd(f"start cmd /k diskpart /s \"{path}\"", f"Wipe & Convert Disk {disk_num}")
        except Exception as e:
            self.show_toast(f"❌ Error creating diskpart script: {e}")

    def run_system_recovery_command(self, action):
        if action == "winre_enable":
            self.run_cmd("start cmd /k reagentc /enable", "Enable WinRE")
        elif action == "winre_status":
            self.run_cmd("start cmd /k reagentc /info", "WinRE Status")
        elif action == "safemode_on":
            self.run_cmd('start cmd /k "bcdedit /set {default} safeboot minimal"', "Enable Safe Mode")
        elif action == "safemode_off":
            self.run_cmd('start cmd /k "bcdedit /deletevalue {default} safeboot"', "Disable Safe Mode")

    def on_closing(self):
        self.telemetry_running = False
        self.destroy()

if __name__ == "__main__":
    app = VenkatPulseApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
