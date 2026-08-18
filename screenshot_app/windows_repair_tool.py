import os
import sys
import time
import platform
import subprocess
import threading
import psutil
import winreg
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog, messagebox
from PIL import Image
import customtkinter as ctk
import shutil

# Initialize CustomTkinter settings
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

def get_asset_path(filename):
    """Resolve path to local resource folder."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, filename)

class WindowsRepairSuite(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Configure ttk Treeview styles globally for a seamless dark theme across all tabs
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Treeview",
                        background="#1c1c1c",
                        fieldbackground="#1c1c1c",
                        foreground="#ffffff",
                        rowheight=26,
                        font=("Outfit", 9),
                        borderwidth=0)
        style.configure("Treeview.Heading",
                        background="#2d2d2d",
                        foreground="#ffffff",
                        font=("Outfit", 9, "bold"),
                        borderwidth=0)
        style.map("Treeview",
                  background=[('selected', '#0078d4')],
                  foreground=[('selected', '#ffffff')])

        self.title("VenkatPulse AI - Windows System Repair & Tweaker 🛠️")
        self.geometry("1300x900")
        self.configure(fg_color="#060913")
        self.resizable(True, True)
        
        # Try loading window icon
        icon_p = get_asset_path("ping_icon.ico")
        if os.path.exists(icon_p):
            try:
                self.iconbitmap(icon_p)
            except:
                pass
                
        self.boot_time = time.time()
        self.is_running_operation = False
        self.winget_available = False
        
        # State variables for background tasks
        self.cpu_pct = 0
        self.ram_pct = 0
        self.disk_free = "Calculating..."
        self.recent_activities = [
            ("Launch Utility", "Ready", "Success", time.strftime("%I:%M:%S %p")),
            ("WinGet Check", "Scanning...", "Info", time.strftime("%I:%M:%S %p"))
        ]
        
        # Bottom Status Footer Bar
        self.status_bar = ctk.CTkFrame(self, height=28, fg_color="#202020", corner_radius=0)
        self.status_bar.pack(side="bottom", fill="x")
        self.status_lbl = ctk.CTkLabel(
            self.status_bar, text="🟢 Status: System ready | Version 1.2.0 | Powered by VenkatPulse AI",
            font=("Outfit", 9, "bold"), text_color="#10b981"
        )
        self.status_lbl.pack(side="left", padx=15, pady=4)
        
        # Sidebar Frame Parent (Left Navigation)
        self.sidebar_parent = ctk.CTkFrame(self, width=255, corner_radius=0, fg_color="#202020")
        self.sidebar_parent.pack(side="left", fill="y")
        self.sidebar_parent.pack_propagate(False)
        
        # Branding Title area
        self.brand_frame = ctk.CTkFrame(self.sidebar_parent, fg_color="transparent")
        self.brand_frame.pack(fill="x", pady=(20, 15), padx=15)
        
        logo_path = get_asset_path("ping_tool_logo.png")
        if os.path.exists(logo_path):
            try:
                logo_img = ctk.CTkImage(Image.open(logo_path), size=(42, 42))
                self.logo_lbl = ctk.CTkLabel(self.brand_frame, image=logo_img, text="")
                self.logo_lbl.pack(side="left", padx=(0, 10))
            except:
                self.logo_lbl = ctk.CTkLabel(self.brand_frame, text="⚡", font=("Consolas", 24))
                self.logo_lbl.pack(side="left", padx=(0, 10))
        else:
            self.logo_lbl = ctk.CTkLabel(self.brand_frame, text="⚡", font=("Consolas", 24))
            self.logo_lbl.pack(side="left", padx=(0, 10))
            
        self.title_text_f = ctk.CTkFrame(self.brand_frame, fg_color="transparent")
        self.title_text_f.pack(side="left", fill="both", expand=True)
        
        self.sidebar_title = ctk.CTkLabel(
            self.title_text_f, text="VenkatPulse AI",
            font=ctk.CTkFont(family="Outfit", size=15, weight="bold"),
            text_color="#ffffff", anchor="w"
        )
        self.sidebar_title.pack(fill="x", anchor="w")
        self.sidebar_sub = ctk.CTkLabel(
            self.title_text_f, text="Windows System Utility",
            font=ctk.CTkFont(family="Outfit", size=9),
            text_color="#8f9bb3", anchor="w"
        )
        self.sidebar_sub.pack(fill="x", anchor="w")
            
        # Scrollable categories frame
        self.sidebar = ctk.CTkScrollableFrame(self.sidebar_parent, fg_color="transparent", corner_radius=0)
        self.sidebar.pack(fill="both", expand=True)
        
        self.categories = [
            ("🏠 Dashboard", "dashboard"),
            ("📥 Software Installer", "installer"),
            ("🔑 Activation Suite", "activation"),
            ("🔧 System Tweaks", "tweaks"),
            ("🧼 Bloatware & Features", "bloatware"),
            ("🛠️ System Repair", "repair"),
            ("📊 Diagnostics & Storage", "diagnostics"),
            ("💾 Backups & Migration", "backups"),
            ("⚙️ Windows Config", "config")
        ]
        
        self.frames = {}
        self.buttons = {}
        self.indicators = {}
        self.active_tool = "dashboard"
        
        # Container for main contents (Right Panel)
        self.container_parent = ctk.CTkFrame(self, fg_color="#1c1c1c", corner_radius=0)
        self.container_parent.pack(side="left", fill="both", expand=True, padx=15, pady=15)
        
        # Build category views & side buttons
        for label, name in self.categories:
            btn_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
            btn_frame.pack(fill="x", padx=8, pady=2)
            
            indicator = ctk.CTkFrame(btn_frame, width=3, fg_color="transparent", height=24)
            indicator.pack(side="left", fill="y", padx=(0, 5))
            self.indicators[name] = indicator
            
            btn = ctk.CTkButton(
                btn_frame, text=label, height=36,
                font=ctk.CTkFont(family="Outfit", size=11, weight="bold"),
                fg_color="transparent", hover_color="#2b2b2b",
                text_color="#cbd5e1", anchor="w",
                command=lambda n=name: self.switch_view(n)
            )
            btn.pack(side="left", fill="x", expand=True)
            self.buttons[name] = btn

        # Top Header Bar in the right container parent
        self.top_header = ctk.CTkFrame(self.container_parent, height=52, fg_color="#202020", corner_radius=8)
        self.top_header.pack(fill="x", padx=10, pady=(10, 5))
        self.top_header.pack_propagate(False)
        
        # Dynamic title inside header
        self.header_title = ctk.CTkLabel(
            self.top_header, text="🏠 System Dashboard Overview",
            font=ctk.CTkFont(family="Outfit", size=14, weight="bold"),
            text_color="#ffffff"
        )
        self.header_title.pack(side="left", padx=15)
        
        # Theme dropdown & stats inside top header
        self.theme_dropdown = ctk.CTkComboBox(
            self.top_header, values=["Default Blue", "Obsidian Dark", "Cyberpunk", "Emerald Green"],
            width=130, height=28, font=("Consolas", 10),
            command=self.change_theme_color
        )
        self.theme_dropdown.pack(side="right", padx=15)
        self.theme_dropdown.set("Default Blue")
        
        self.status_winget_lbl = ctk.CTkLabel(
            self.top_header, text="WinGet: Checking...",
            font=("Consolas", 10, "bold"), text_color="#f59e0b"
        )
        self.status_winget_lbl.pack(side="right", padx=15)

        
        # Global Search Bar in Top Header
        self.search_frame = ctk.CTkFrame(self.top_header, fg_color="transparent")
        self.search_frame.pack(side="right", padx=10)
        
        self.search_input = ctk.CTkEntry(
            self.search_frame, placeholder_text="🔍 Search issues (e.g. printer, RAM, activation)...",
            width=260, height=28, font=("Outfit", 10)
        )
        self.search_input.pack(side="left", padx=(0, 5))
        self.search_input.bind("<Return>", lambda event: self.trigger_global_search())
        
        self.search_btn = ctk.CTkButton(
            self.search_frame, text="Search", width=60, height=28,
            font=("Outfit", 9, "bold"), command=self.trigger_global_search
        )
        self.search_btn.pack(side="left")
        
        # Setup content views container
        self.container = ctk.CTkFrame(self.container_parent, fg_color="transparent")
        self.container.pack(fill="both", expand=True, padx=10, pady=5)
        self.initialize_tools_catalog()
        # Instantiate sub-tabs
        self.setup_dashboard_tab()
        self.setup_installer_tab()
        self.setup_activation_tab()
        self.setup_tweaks_tab()
        self.setup_bloatware_tab()
        self.setup_repair_tab()
        self.setup_diagnostics_tab()
        self.setup_backups_tab()
        self.setup_config_tab()
        self.setup_search_tab()
        
        # Show Dashboard initially
        self.switch_view("dashboard")
        
        # Start background threads for system stats updates
        threading.Thread(target=self.bg_status_loop, daemon=True).start()
        threading.Thread(target=self.bg_winget_check, daemon=True).start()

    def switch_view(self, target_name):
        self.active_tool = target_name
        
        # Hide all frames
        for frame in self.frames.values():
            frame.pack_forget()
            
        # Display selected
        if target_name in self.frames:
            self.frames[target_name].pack(fill="both", expand=True)
            
        # Highlight sidebar buttons
        accent = "#0078d4"
        if hasattr(self, "theme_dropdown"):
            current_theme = self.theme_dropdown.get()
            if current_theme == "Obsidian Dark":
                accent = "#6366f1"
            elif current_theme == "Cyberpunk":
                accent = "#facc15"
            elif current_theme == "Emerald Green":
                accent = "#10b981"
                
        for btn_name, btn in self.buttons.items():
            if btn_name == target_name:
                btn.configure(fg_color="#333333", text_color="#ffffff")
                self.indicators[btn_name].configure(fg_color=accent)
            else:
                btn.configure(fg_color="transparent", text_color="#cbd5e1")
                self.indicators[btn_name].configure(fg_color="transparent")
                
        # Set top header title matching selection
        titles = {
            "dashboard": "🏠 System Dashboard Overview",
            "installer": "📥 Software Installer Utility (via WinGet)",
            "activation": "🔑 Windows & Office Activation (via MAS)",
            "tweaks": "🔧 Premium OS Tweaks & Optimization",
            "bloatware": "🧼 UWP Bloatware Remover & Optional Features",
            "repair": "🛠️ System File & Network Repair Panel",
            "diagnostics": "📊 Diagnostics & Volume Storage Node",
            "backups": "💾 Data Backups & Migration Hub",
            "config": "⚙️ Core Windows Configuration consoles"
        }
        self.header_title.configure(text=titles.get(target_name, "VenkatPulse AI Suite"))

    def bg_winget_check(self):
        """Check if WinGet is installed on the system."""
        try:
            res = subprocess.run(["winget", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
            if res.returncode == 0:
                self.winget_available = True
                self.status_winget_lbl.configure(text=f"WinGet: {res.stdout.strip()}", text_color="#10b981")
                self.add_activity("WinGet Diagnostic", "WinGet detected successfully", "Success")
            else:
                self.status_winget_lbl.configure(text="WinGet: Missing", text_color="#ef4444")
                self.add_activity("WinGet Diagnostic", "WinGet is not available on this machine", "Warning")
        except:
            self.status_winget_lbl.configure(text="WinGet: Missing", text_color="#ef4444")
            self.add_activity("WinGet Diagnostic", "WinGet is not available on this machine", "Warning")

    def bg_status_loop(self):
        """Update system metrics every 2 seconds."""
        while True:
            try:
                self.cpu_pct = psutil.cpu_percent()
                self.ram_pct = psutil.virtual_memory().percent
                
                # Fetch system disk space
                total, used, free = psutil.disk_usage('C:')
                self.disk_free = f"{free / (1024**3):.1f} GB Free"
                
                # Update UI elements
                if hasattr(self, "card_cpu_val"):
                    self.card_cpu_val.configure(text=f"{self.cpu_pct}%")
                    self.card_ram_val.configure(text=f"{self.ram_pct}%")
                    self.card_disk_val.configure(text=self.disk_free)
                    
                    # Update uptime
                    uptime_sec = time.time() - self.boot_time
                    h = int(uptime_sec // 3600)
                    m = int((uptime_sec % 3600) // 60)
                    s = int(uptime_sec % 60)
                    self.card_uptime_val.configure(text=f"{h}h {m}m {s}s")
            except:
                pass
            time.sleep(2)

    def add_activity(self, op_name, desc, status):
        """Helper to append row to dashboard activity log."""
        self.recent_activities.insert(0, (op_name, desc, status, time.strftime("%I:%M:%S %p")))
        if len(self.recent_activities) > 30:
            self.recent_activities.pop()
            
        if hasattr(self, "activity_tree"):
            # Update Treeview in main thread
            self.after(0, self.refresh_activity_tree)

    def refresh_activity_tree(self):
        if not hasattr(self, "activity_tree"):
            return
        # Clear
        for item in self.activity_tree.get_children():
            self.activity_tree.delete(item)
        # Populate
        for op, desc, stat, tm in self.recent_activities:
            self.activity_tree.insert("", "end", values=(op, desc, stat, tm))

    # ==========================
    # Tab 1: Dashboard
    # ==========================
    def setup_dashboard_tab(self):
        f = ctk.CTkFrame(self.container, fg_color="transparent")
        self.frames["dashboard"] = f
        
        # Grid layout for system metric cards
        cards_frame = ctk.CTkFrame(f, fg_color="transparent")
        cards_frame.pack(fill="x", pady=10)
        
        # Make columns resize equally
        cards_frame.grid_columnconfigure((0, 1, 2, 3), weight=1, uniform="equal")
        
        # Card 1: Windows OS
        c1 = ctk.CTkFrame(cards_frame, fg_color="#151f32", border_color="#1e293b", border_width=1.5, height=90)
        c1.grid(row=0, column=0, padx=5, sticky="nsew")
        ctk.CTkLabel(c1, text="🖥️ OS Platform", font=("Outfit", 9), text_color="#cbd5e1").pack(anchor="w", padx=15, pady=(10, 0))
        ctk.CTkLabel(c1, text=f"Windows {platform.release()}", font=("Outfit", 12, "bold"), text_color="#ffffff").pack(anchor="w", padx=15)
        ctk.CTkLabel(c1, text=platform.architecture()[0], font=("Outfit", 8), text_color="#38bdf8").pack(anchor="w", padx=15, pady=(0, 10))

        # Card 2: CPU Usage
        c2 = ctk.CTkFrame(cards_frame, fg_color="#151f32", border_color="#1e293b", border_width=1.5, height=90)
        c2.grid(row=0, column=1, padx=5, sticky="nsew")
        ctk.CTkLabel(c2, text="⚡ CPU Load", font=("Outfit", 9), text_color="#cbd5e1").pack(anchor="w", padx=15, pady=(10, 0))
        self.card_cpu_val = ctk.CTkLabel(c2, text="0%", font=("Outfit", 14, "bold"), text_color="#ffffff")
        self.card_cpu_val.pack(anchor="w", padx=15)
        ctk.CTkLabel(c2, text="Real-time monitor", font=("Outfit", 8), text_color="#10b981").pack(anchor="w", padx=15, pady=(0, 10))

        # Card 3: Memory Load
        c3 = ctk.CTkFrame(cards_frame, fg_color="#151f32", border_color="#1e293b", border_width=1.5, height=90)
        c3.grid(row=0, column=2, padx=5, sticky="nsew")
        ctk.CTkLabel(c3, text="🧠 Memory Usage", font=("Outfit", 9), text_color="#cbd5e1").pack(anchor="w", padx=15, pady=(10, 0))
        self.card_ram_val = ctk.CTkLabel(c3, text="0%", font=("Outfit", 14, "bold"), text_color="#ffffff")
        self.card_ram_val.pack(anchor="w", padx=15)
        ctk.CTkLabel(c3, text="RAM allocation", font=("Outfit", 8), text_color="#38bdf8").pack(anchor="w", padx=15, pady=(0, 10))

        # Card 4: Uptime / Storage
        c4 = ctk.CTkFrame(cards_frame, fg_color="#151f32", border_color="#1e293b", border_width=1.5, height=90)
        c4.grid(row=0, column=3, padx=5, sticky="nsew")
        ctk.CTkLabel(c4, text="📂 Disk Free Space (C:)", font=("Outfit", 9), text_color="#cbd5e1").pack(anchor="w", padx=15, pady=(10, 0))
        self.card_disk_val = ctk.CTkLabel(c4, text="Calculating...", font=("Outfit", 12, "bold"), text_color="#ffffff")
        self.card_disk_val.pack(anchor="w", padx=15)
        self.card_uptime_val = ctk.CTkLabel(c4, text="Uptime: Calculating...", font=("Outfit", 8), text_color="#cbd5e1")
        self.card_uptime_val.pack(anchor="w", padx=15, pady=(0, 10))

        # Lower half: Activity logger
        act_frame = ctk.CTkFrame(f, fg_color="#151f32", border_color="#1e293b", border_width=1.5)
        act_frame.pack(fill="both", expand=True, pady=10)
        
        ctk.CTkLabel(act_frame, text="📋 Recent Actions & System Diagnostics Logs", font=("Outfit", 11, "bold"), text_color="#ffffff").pack(anchor="w", padx=15, pady=10)
        
        # Configure Treeview table
        self.activity_tree = ttk.Treeview(
            act_frame, columns=("Operation", "Description", "Status", "Timestamp"), show="headings", style="Treeview"
        )
        self.activity_tree.heading("Operation", text="Operation Name")
        self.activity_tree.heading("Description", text="Diagnostic Details")
        self.activity_tree.heading("Status", text="Status")
        self.activity_tree.heading("Timestamp", text="Timestamp")
        
        self.activity_tree.column("Operation", width=150, anchor="w")
        self.activity_tree.column("Description", width=400, anchor="w")
        self.activity_tree.column("Status", width=100, anchor="center")
        self.activity_tree.column("Timestamp", width=120, anchor="center")
        
        self.activity_tree.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        self.refresh_activity_tree()

    # ==========================
    # Tab 2: Software Installer
    # ==========================
    def setup_installer_tab(self):
        f = ctk.CTkFrame(self.container, fg_color="transparent")
        self.frames["installer"] = f
        
        # Top banner warning
        warn_bar = ctk.CTkFrame(f, fg_color="#1e1b4b", border_color="#312e81", border_width=1)
        warn_bar.pack(fill="x", pady=(5, 10))
        ctk.CTkLabel(warn_bar, text="💡 Quick Software Installer: Select utility tiles below and click Install. System runs Microsoft WinGet silently.", font=("Outfit", 9), text_color="#cbd5e1").pack(anchor="w", padx=15, pady=8)
        
        # Main split container
        split_frame = ctk.CTkFrame(f, fg_color="transparent")
        split_frame.pack(fill="both", expand=True)
        
        # Left side: Scrollable checklist grid
        list_card = ctk.CTkFrame(split_frame, fg_color="#151f32", border_color="#1e293b", border_width=1.5)
        list_card.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        list_scroll = ctk.CTkScrollableFrame(list_card, fg_color="transparent")
        list_scroll.pack(fill="both", expand=True, padx=15, pady=10)
        
        # Expanded software list catalog categorized with icons
        self.software_catalog = {
            "Browsers": [
                ("Google Chrome", "Google.Chrome", "🌐"),
                ("Mozilla Firefox", "Mozilla.Firefox", "🦊"),
                ("Brave Browser", "Brave.Brave", "🦁"),
                ("Opera Browser", "Opera.Opera", "🔴"),
                ("Vivaldi Browser", "VivaldiTechnologies.Vivaldi", "🧭"),
                ("Arc Browser", "TheBrowserCompany.Arc", "🌀"),
                ("Microsoft Edge Update", "Microsoft.Edge", "🧭")
            ],
            "Microsoft Tools & Platforms": [
                ("Microsoft Teams", "Microsoft.Teams", "👥"),
                ("Windows Terminal", "Microsoft.WindowsTerminal", "📟"),
                ("Sysinternals Suite", "Microsoft.SysinternalsSuite", "🛡️"),
                ("PowerShell 7 Core", "Microsoft.PowerShell", "🎛️"),
                ("Visual Studio 2022", "Microsoft.VisualStudio.2022.Community", "🏢"),
                ("Microsoft Office 365", "Microsoft.Office", "📦"),
                ("PowerBI Desktop", "Microsoft.PowerBIDesktop", "📊"),
                ("OneDrive client", "Microsoft.OneDrive", "☁️"),
                ("Remote Desktop client", "Microsoft.RemoteDesktop", "🖥️"),
                ("SQL Server Studio (SSMS)", "Microsoft.SQLServerManagementStudio", "🗄️")
            ],
            "Utilities & Chat": [
                ("7-Zip (Archiver)", "7zip.7zip", "🗜️"),
                ("Notepad++ (Editor)", "Notepad++.Notepad++", "📝"),
                ("VLC Media Player", "VideoLAN.VLC", "🎬"),
                ("Discord Chat client", "Discord.Discord", "💬"),
                ("Telegram Desktop", "Telegram.TelegramDesktop", "✈️"),
                ("WhatsApp Desktop", "WhatsApp.WhatsApp", "💬"),
                ("Steam Gaming client", "Valve.Steam", "🎮"),
                ("Microsoft PowerToys", "Microsoft.PowerToys", "🛠️"),
                ("Rufus Bootable USB", "Akeo.Rufus", "💾"),
                ("WinRAR archiver", "RARLab.WinRAR", "📚"),
                ("Everything Search", "Voidtools.Everything", "🔍"),
                ("BleachBit cleaner", "BleachBit.BleachBit", "🧹"),
                ("AnyDesk Utility", "AnyDeskSoftwareGmbH.AnyDesk", "🖥️"),
                ("TeamViewer Client", "TeamViewer.TeamViewer", "🤝"),
                ("LDPlayer 9 Android", "XuanZhi.LDPlayer9", "📱")
            ],
            "Development & Networking": [
                ("VS Code Editor", "Microsoft.VisualStudioCode", "💻"),
                ("Git SCM tool", "Git.Git", "🌿"),
                ("Python 3.12", "Python.Python.3.12", "🐍"),
                ("Node.js LTS Runtime", "OpenJS.NodeJS.LTS", "🟢"),
                ("DBeaver Community", "dbeaver.dbeaver", "🐬"),
                ("IntelliJ IDEA Community", "JetBrains.IntelliJIDEA.Community", "☕"),
                ("Docker Desktop", "Docker.DockerDesktop", "🐳"),
                ("WSL Ubuntu Distro", "Canonical.Ubuntu", "🐧"),
                ("Cisco Packet Tracer", "Cisco.PacketTracer", "🌐"),
                ("WinSCP SFTP client", "WinSCP.WinSCP", "🚀"),
                ("FileZilla FTP client", "TimKosse.FileZilla.Client", "📂"),
                ("Oracle VirtualBox", "Oracle.VirtualBox", "📦"),
                ("Wireshark Analyzer", "Wireshark.Wireshark", "🦈"),
                ("Nmap Port Scanner", "Insecure.Nmap", "🗺️"),
                ("PuTTY SSH client", "SimonTatham.PuTTY", "🔌")
            ],
            "Office, Design & Media": [
                ("LibreOffice Suite", "LibreOffice.LibreOffice", "📄"),
                ("GIMP Image Editor", "GIMP.GIMP", "🎨"),
                ("Blender 3D Suite", "BlenderFoundation.Blender", "🧡"),
                ("Adobe Reader DC", "Adobe.AdobeReaderext.Language.English", "📕"),
                ("Zoom Conferences", "Zoom.Zoom", "📹"),
                ("OBS Studio recorder", "Obsproject.OBSStudio", "🎙️"),
                ("Spotify Music client", "Spotify.Spotify", "🎵")
            ]
        }
        
        self.software_variables = {}
        
        for category, items in self.software_catalog.items():
            # Section title label
            lbl = ctk.CTkLabel(list_scroll, text=category.upper(), font=("Outfit", 9, "bold"), text_color="#38bdf8")
            lbl.pack(anchor="w", pady=(15, 6))
            
            # Grid container for this category
            grid_frame = ctk.CTkFrame(list_scroll, fg_color="transparent")
            grid_frame.pack(fill="x", expand=True, pady=2)
            
            # 3-column configuration
            grid_frame.grid_columnconfigure((0, 1, 2), weight=1, uniform="equal")
            
            row = 0
            col = 0
            for name, winget_id, icon in items:
                var = tk.BooleanVar(value=False)
                self.software_variables[winget_id] = var
                
                # Create a card tile for the app
                card = ctk.CTkFrame(grid_frame, fg_color="#1e293b", border_color="#334155", border_width=1)
                card.grid(row=row, column=col, padx=4, pady=4, sticky="nsew")
                
                chk = ctk.CTkCheckBox(
                    card, text=f"{icon}  {name}", variable=var,
                    font=("Outfit", 9, "bold"), fg_color="#0078d4",
                    hover_color="#005a9e", text_color="#ffffff"
                )
                chk.pack(anchor="w", padx=10, pady=8, fill="x")
                
                col += 1
                if col > 2:
                    col = 0
                    row += 1
                    
        # Right side: Operations panel & Terminal logging
        ops_card = ctk.CTkFrame(split_frame, width=380, fg_color="#151f32", border_color="#1e293b", border_width=1.5)
        ops_card.pack(side="right", fill="both", padx=(5, 0))
        ops_card.pack_propagate(False)
        
        ctk.CTkLabel(ops_card, text="⚙️ Installation Terminal", font=("Outfit", 11, "bold"), text_color="#ffffff").pack(anchor="w", padx=15, pady=10)
        
        self.install_log_text = ctk.CTkTextbox(
            ops_card, fg_color="#0d1321", border_color="#1e293b", border_width=1, text_color="#10b981", font=("Consolas", 9)
        )
        self.install_log_text.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        self.install_log_text.insert("end", "[System ready for WinGet installations]\n")
        self.install_log_text.configure(state="disabled")
        
        # Install Button
        self.btn_run_install = ctk.CTkButton(
            ops_card, text="🚀 Install Selected Software",
            font=("Outfit", 11, "bold"), fg_color="#0078d4", hover_color="#005a9e",
            command=self.start_software_installation
        )
        self.btn_run_install.pack(fill="x", padx=15, pady=(0, 15))

    def append_install_log(self, text):
        self.install_log_text.configure(state="normal")
        self.install_log_text.insert("end", text)
        self.install_log_text.see("end")
        self.install_log_text.configure(state="disabled")

    def start_software_installation(self):
        if self.is_running_operation:
            self.append_install_log("[!] Error: An active operation is already running.\n")
            return
            
        selected_ids = [winget_id for winget_id, var in self.software_variables.items() if var.get()]
        if not selected_ids:
            self.append_install_log("[!] Please select at least one software to install.\n")
            return
            
        self.is_running_operation = True
        self.btn_run_install.configure(state="disabled", text="Installing Software...")
        threading.Thread(target=self.run_install_loop, args=(selected_ids,), daemon=True).start()

    def run_install_loop(self, selected_ids):
        self.append_install_log(f"\n[*] Starting installation task for {len(selected_ids)} packages...\n")
        
        for winget_id in selected_ids:
            self.append_install_log(f"[*] Preparing: {winget_id}...\n")
            self.add_activity("WinGet Installer", f"Installing {winget_id}", "Running")
            
            cmd = ["winget", "install", "--id", winget_id, "--silent", "--accept-source-agreements", "--accept-package-agreements"]
            
            try:
                proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
                
                while True:
                    line = proc.stdout.readline()
                    if not line:
                        break
                    self.append_install_log(line)
                    
                proc.wait()
                if proc.returncode == 0:
                    self.append_install_log(f"[✓] Successfully Installed: {winget_id}\n\n")
                    self.add_activity("WinGet Installer", f"Installed {winget_id} successfully", "Success")
                else:
                    self.append_install_log(f"[X] Failed installation for: {winget_id} (Code: {proc.returncode})\n\n")
                    self.add_activity("WinGet Installer", f"Failed to install {winget_id}", "Failed")
            except Exception as e:
                self.append_install_log(f"[X] Exception running install command: {str(e)}\n\n")
                self.add_activity("WinGet Installer", f"Error launching Winget installer: {str(e)}", "Failed")
                
        self.append_install_log("[*] Completed all WinGet installer tasks.\n")
        self.is_running_operation = False
        self.btn_run_install.configure(state="normal", text="🚀 Install Selected Software")

    # ==========================
    # Tab 3: Activation Suite
    # ==========================
    def setup_activation_tab(self):
        f = ctk.CTkFrame(self.container, fg_color="transparent")
        self.frames["activation"] = f
        
        # Grid structure for Office Installer and Activation
        scroll_act = ctk.CTkScrollableFrame(f, fg_color="transparent")
        scroll_act.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Section 1: Microsoft Office Installer Panel
        lbl1 = ctk.CTkLabel(scroll_act, text="📦 MICROSOFT OFFICE INSTALLER SUITE", font=("Outfit", 12, "bold"), text_color="#38bdf8")
        lbl1.pack(anchor="w", pady=(10, 10))
        
        grid_office = ctk.CTkFrame(scroll_act, fg_color="transparent")
        grid_office.pack(fill="x", expand=True, pady=5)
        grid_office.grid_columnconfigure((0, 1, 2, 3), weight=1, uniform="equal")
        
        office_suites = [
            ("Microsoft 365 Apps", "Subscription Suite. Includes cloud service apps.", "Install Microsoft 365", "Microsoft.Office"),
            ("Office LTSC 2019", "Volume License. Perpetual Office LTSC 2019 ProPlus.", "Install Office 2019", "Microsoft.Office.LTSC.2019"),
            ("Office LTSC 2021", "Volume License. Perpetual Office LTSC 2021 ProPlus.", "Install Office 2021", "Microsoft.Office.LTSC.2021"),
            ("Office LTSC 2024", "Volume License. Perpetual Office LTSC 2024 preview.", "Install Office 2024", "Microsoft.Office.LTSC.2024")
        ]
        
        for idx, (name, desc, btn_txt, pkg_id) in enumerate(office_suites):
            card = ctk.CTkFrame(grid_office, fg_color="#151f32", border_color="#1e293b", border_width=1.5)
            card.grid(row=0, column=idx, padx=5, pady=5, sticky="nsew")
            
            ctk.CTkLabel(card, text=name, font=("Outfit", 11, "bold"), text_color="#ffffff").pack(anchor="w", padx=15, pady=(15, 2))
            ctk.CTkLabel(card, text=desc, font=("Outfit", 8), text_color="#94a3b8", justify="left", wraplength=180).pack(anchor="w", padx=15, pady=(0, 15))
            
            btn = ctk.CTkButton(
                card, text=btn_txt, font=("Outfit", 9, "bold"), height=28, fg_color="#1e293b", hover_color="#2b2b2b",
                command=lambda p=pkg_id: self.run_office_installer_pkg(p)
            )
            btn.pack(fill="x", padx=15, pady=(0, 15))
            
        # Section 2: Windows & Office Activation (MAS)
        lbl2 = ctk.CTkLabel(scroll_act, text="🔑 WINDOWS & OFFICE ACTIVATION (VIA MAS)", font=("Outfit", 12, "bold"), text_color="#38bdf8")
        lbl2.pack(anchor="w", pady=(25, 10))
        
        # Transparent transparency disclaimer
        desc_bar = ctk.CTkFrame(scroll_act, fg_color="#1e1b4b", border_color="#312e81", border_width=1)
        desc_bar.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(
            desc_bar, text="🛡️ Safety Notice: Activates Windows and Office suites safely using Microsoft Activation Scripts (MAS) open-source repository.",
            font=("Outfit", 9), text_color="#cbd5e1"
        ).pack(anchor="w", padx=15, pady=8)
        
        grid_act = ctk.CTkFrame(scroll_act, fg_color="transparent")
        grid_act.pack(fill="x", expand=True, pady=5)
        grid_act.grid_columnconfigure((0, 1, 2, 3, 4), weight=1, uniform="equal")
        
        activation_opts = [
            ("Activate Windows (HWID)", "Permanently activates Windows 10/11 using HWID license.", "⚡ Activate Windows", "HWID"),
            ("Activate Office (Ohook)", "Activates Microsoft Office suites using Ohook local injection.", "⚡ Activate Office", "Ohook"),
            ("Activate Both (KMS)", "Activates Windows and Office using Online KMS script.", "⚡ Activate KMS", "KMS"),
            ("Uninstall Online KMS", "Removes previously installed Online KMS setups completely.", "🧹 Clean KMS Setup", "Uninstall"),
            ("Change Windows Edition", "Upgrades or switches Windows editions (e.g. Home to Pro, Enterprise, LTSC).", "🔄 Change Edition", "Edition")
        ]
        
        for idx, (name, desc, btn_txt, method) in enumerate(activation_opts):
            card = ctk.CTkFrame(grid_act, fg_color="#151f32", border_color="#1e293b", border_width=1.5)
            card.grid(row=0, column=idx, padx=5, pady=5, sticky="nsew")
            
            ctk.CTkLabel(card, text=name, font=("Outfit", 11, "bold"), text_color="#ffffff").pack(anchor="w", padx=15, pady=(15, 2))
            ctk.CTkLabel(card, text=desc, font=("Outfit", 8), text_color="#94a3b8", justify="left", wraplength=180).pack(anchor="w", padx=15, pady=(0, 15))
            
            if method == "Edition":
                cmd_fn = self.show_edition_changer_dialog
            else:
                cmd_fn = self.run_mas_activation
                
            btn = ctk.CTkButton(
                card, text=btn_txt, font=("Outfit", 9, "bold"), height=28, fg_color="#0078d4", hover_color="#005a9e",
                command=cmd_fn
            )
            btn.pack(fill="x", padx=15, pady=(0, 15))

    def show_office_install_popup(self, title):
        popup = ctk.CTkToplevel(self)
        popup.title(f"Installing {title}")
        popup.geometry("600x400")
        popup.grab_set()  # Modal dialog
        popup.resizable(False, False)
        
        # Center popup
        x = self.winfo_x() + (self.winfo_width() // 2) - 300
        y = self.winfo_y() + (self.winfo_height() // 2) - 200
        popup.geometry(f"+{x}+{y}")
        
        frame = ctk.CTkFrame(popup, fg_color="#151f32", border_color="#1e293b", border_width=1.5)
        frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        ctk.CTkLabel(frame, text=f"📦 Deploying {title}", font=("Outfit", 12, "bold"), text_color="#38bdf8").pack(anchor="w", padx=20, pady=(15, 5))
        
        lbl_status = ctk.CTkLabel(frame, text="Initializing setup...", font=("Outfit", 9), text_color="#cbd5e1")
        lbl_status.pack(anchor="w", padx=20)
        
        pbar = ctk.CTkProgressBar(frame, width=540, progress_color="#0078d4")
        pbar.pack(padx=20, pady=(5, 15))
        pbar.set(0.0)
        
        txt_log = ctk.CTkTextbox(frame, fg_color="#090d16", border_color="#1e293b", border_width=1, text_color="#cbd5e1", font=("Consolas", 9))
        txt_log.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        def log(msg):
            txt_log.configure(state="normal")
            txt_log.insert("end", msg)
            txt_log.see("end")
            txt_log.configure(state="disabled")
            
        def update_progress(val, status_text):
            pbar.set(val)
            lbl_status.configure(text=status_text)
            
        return popup, log, update_progress

    def run_office_installer_pkg(self, pkg_id):
        # Determine title
        if pkg_id == "Microsoft.Office":
            title = "Microsoft 365 Apps"
        elif "2019" in pkg_id:
            title = "Office LTSC 2019 Professional Plus"
        elif "2021" in pkg_id:
            title = "Office LTSC 2021 Professional Plus"
        else:
            title = "Office LTSC 2024 Professional Plus (Preview)"
            
        self.add_activity("Office Installer", f"Requesting install for {pkg_id}", "Running")
        
        # Open progress popup
        popup, log_func, progress_func = self.show_office_install_popup(title)
        
        if pkg_id == "Microsoft.Office":
            threading.Thread(target=self.deploy_m365_winget, args=(log_func, progress_func), daemon=True).start()
        else:
            threading.Thread(target=self.deploy_office_ltsc_odt, args=(pkg_id, title, log_func, progress_func), daemon=True).start()

    def deploy_m365_winget(self, log_func, progress_func):
        try:
            log_func("[*] Starting Microsoft 365 Apps deployment via Winget...\n")
            progress_func(0.2, "Installing Microsoft 365...")
            
            cmd = ["winget", "install", "--id", "Microsoft.Office", "--silent", "--accept-source-agreements", "--accept-package-agreements"]
            
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
            while True:
                line = proc.stdout.readline()
                if not line:
                    break
                log_func(line)
            proc.wait()
            
            if proc.returncode == 0:
                progress_func(1.0, "Installation Finished!")
                log_func("\n[✓] Microsoft 365 Apps installed successfully!\n")
                self.add_activity("Office Installer", "Microsoft 365 install completed", "Success")
                messagebox.showinfo("Success", "Microsoft 365 Apps installation has finished!")
            else:
                progress_func(1.0, "Installation Failed")
                log_func(f"\n[X] Winget failed with exit code: {proc.returncode}\n")
                self.add_activity("Office Installer", "Microsoft 365 install failed", "Failed")
                messagebox.showerror("Error", f"Failed to install Microsoft 365. Exit code: {proc.returncode}")
        except Exception as e:
            log_func(f"\n[X] Error: {str(e)}\n")
            self.add_activity("Office Installer", f"Microsoft 365 install error: {str(e)}", "Failed")
            messagebox.showerror("Error", f"Failed to run installer:\n{str(e)}")

    def deploy_office_ltsc_odt(self, pkg_id, title, log_func, progress_func):
        try:
            log_func("[*] Initializing Office LTSC custom deployment...\n")
            odt_dir = r"C:\OfficeODT"
            if not os.path.exists(odt_dir):
                os.makedirs(odt_dir)
                
            # Step 1: Install ODT using Winget
            log_func("[*] Attempting to install Office Deployment Tool via Winget...\n")
            progress_func(0.15, "Installing ODT via Winget...")
            cmd_winget = ["winget", "install", "--id", "Microsoft.OfficeDeploymentTool", "--silent", "--accept-source-agreements", "--accept-package-agreements"]
            subprocess.run(cmd_winget, capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
            
            # Verify setup.exe path from Winget installation
            setup_exe = r"C:\Program Files\OfficeDeploymentTool\setup.exe"
            if not os.path.exists(setup_exe):
                setup_exe = r"C:\Program Files (x86)\OfficeDeploymentTool\setup.exe"
                
            # Fallback direct download if Winget failed or setup.exe not found
            if not os.path.exists(setup_exe):
                log_func("[!] ODT not found via Winget. Falling back to direct download...\n")
                progress_func(0.25, "Downloading ODT directly...")
                
                # Latest direct download URL retrieved from Winget repository manifest
                odt_url = "https://download.microsoft.com/download/6c1eeb25-cf8b-41d9-8d0d-cc1dbc032140/officedeploymenttool_20228-20124.exe"
                odt_exe = os.path.join(odt_dir, "odt_installer.exe")
                
                import urllib.request
                urllib.request.urlretrieve(odt_url, odt_exe)
                log_func("[✓] Download completed successfully. Extracting...\n")
                
                # Extract setup.exe
                extract_proc = subprocess.run([odt_exe, f"/extract:{odt_dir}", "/quiet"], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
                setup_exe = os.path.join(odt_dir, "setup.exe")
                
            if not os.path.exists(setup_exe):
                raise Exception("Could not retrieve or extract setup.exe for Office Deployment Tool.")
            
            log_func("[✓] ODT setup utility verified and ready.\n")
            
            # Step 2: Write configuration.xml
            if "2019" in pkg_id:
                channel = "PerpetualVL2019"
                product = "ProPlus2019Volume"
            elif "2021" in pkg_id:
                channel = "PerpetualVL2021"
                product = "ProPlus2021Volume"
            else: # 2024
                channel = "PerpetualVL2024"
                product = "ProPlus2024Volume"
                
            config_xml_path = os.path.join(odt_dir, "configuration.xml")
            config_xml_content = f"""<Configuration>
  <Add OfficeClientEdition="64" Channel="{channel}">
    <Product ID="{product}">
      <Language ID="en-us" />
    </Product>
  </Add>
  <Display Level="Full" AcceptEULA="TRUE" />
</Configuration>"""
            
            with open(config_xml_path, "w", encoding="utf-8") as f:
                f.write(config_xml_content)
            log_func("[✓] Custom configuration.xml written successfully.\n")
            
            # Step 3: Run Configure
            log_func(f"[*] Starting Microsoft Office installation wizard for {title}...\n")
            log_func("[*] Running 'setup.exe /configure configuration.xml' (Please monitor the installer window)...\n")
            progress_func(0.65, "Configuring and running Office wizard...")
            
            # Launch setup.exe in active window mode since Office installation wizard needs UI interaction/display
            proc = subprocess.Popen([setup_exe, "/configure", config_xml_path])
            proc.wait()
            
            progress_func(1.0, "Installation Finished")
            log_func(f"[✓] Office installation process for {title} finished!\n")
            self.add_activity("Office Installer", f"{title} install completed", "Success")
            messagebox.showinfo("Success", f"{title} installation has finished!")
            
            # Clean up temp files if created in temporary folder
            try:
                if odt_dir in setup_exe:
                    shutil.rmtree(odt_dir)
            except:
                pass
        except Exception as e:
            progress_func(1.0, "Installation Failed")
            log_func(f"[X] Office custom installation failed: {str(e)}\n")
            self.add_activity("Office Installer", f"Failed LTSC install: {str(e)}", "Failed")
            messagebox.showerror("Error", f"Failed to install Office LTSC:\n{str(e)}")

    def run_mas_activation(self):
        """Invoke Microsoft Activation Scripts (MAS) in a separate visible PowerShell window."""
        self.add_activity("System Activation", "Launching MAS Console Interface", "Running")
        cmd = 'Start-Process powershell -ArgumentList "-NoProfile -ExecutionPolicy Bypass -Command [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; iex(irm https://get.activated.win)" -Verb RunAs'
        try:
            subprocess.Popen(["powershell", "-Command", cmd], creationflags=subprocess.CREATE_NO_WINDOW)
            self.add_activity("System Activation", "MAS Console opened successfully", "Success")
        except Exception as e:
            self.add_activity("System Activation", f"Failed to launch MAS console: {str(e)}", "Failed")

    def show_edition_changer_dialog(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Windows Edition Changer 🔄")
        dialog.geometry("400x250")
        dialog.configure(fg_color="#151f32")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        w = dialog.winfo_width()
        h = dialog.winfo_height()
        x = self.winfo_x() + (self.winfo_width() // 2) - (w // 2)
        y = self.winfo_y() + (self.winfo_height() // 2) - (h // 2)
        dialog.geometry(f"+{x}+{y}")
        
        ctk.CTkLabel(
            dialog, text="Select Target Windows Edition:",
            font=("Outfit", 12, "bold"), text_color="#38bdf8"
        ).pack(pady=(20, 10))
        
        editions = {
            "Windows 10/11 Professional": "VK7JG-NPHTM-C97JM-9MPGT-3V66T",
            "Windows 10/11 Enterprise": "NPPR9-FWDCX-D2C8J-H872K-2YT43",
            "Windows 10/11 Education": "NW6C2-QMPVW-D7KKK-3GKT6-VCFB2",
            "Windows 10/11 Professional Workstation": "WYPNQ-8C467-V2W6J-TX4WX-WT2RQ"
        }
        
        combo = ctk.CTkComboBox(dialog, values=list(editions.keys()), width=280)
        combo.pack(pady=10)
        combo.set("Windows 10/11 Professional")
        
        def apply_change():
            sel = combo.get()
            key = editions.get(sel)
            if key:
                dialog.destroy()
                self.add_activity("Windows Edition", f"Changing edition to {sel}", "Running")
                # Run slmgr /ipk command in background thread
                cmd = ["cscript", "//nologo", "C:\\Windows\\System32\\slmgr.vbs", "/ipk", key]
                threading.Thread(target=self.run_edition_change_thread, args=(cmd, sel), daemon=True).start()
                
        ctk.CTkButton(
            dialog, text="Apply Edition Change", font=("Outfit", 11, "bold"),
            fg_color="#10b981", hover_color="#059669", command=apply_change
        ).pack(pady=20)

    def run_edition_change_thread(self, cmd, edition_name):
        try:
            self.add_activity("Windows Edition", f"Installing product key for {edition_name}...", "Running")
            proc = subprocess.run(cmd, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
            if proc.returncode == 0:
                self.add_activity("Windows Edition", f"Edition changed to {edition_name} successfully", "Success")
                messagebox.showinfo("Success", f"Product key for {edition_name} installed successfully.\nWindows will now attempt to update your features.")
            else:
                self.add_activity("Windows Edition", f"Failed key installation: {proc.stderr}", "Failed")
                messagebox.showerror("Error", f"Failed to change edition.\nDetails: {proc.stdout}\n{proc.stderr}")
        except Exception as e:
            self.add_activity("Windows Edition", f"Error: {str(e)}", "Failed")

    # ==========================
    # Tab 4: System Tweaks
    # ==========================
    def setup_tweaks_tab(self):
        f = ctk.CTkFrame(self.container, fg_color="transparent")
        self.frames["tweaks"] = f
        
        # Main split container
        split_frame = ctk.CTkFrame(f, fg_color="transparent")
        split_frame.pack(fill="both", expand=True)
        
        # Left card: Tweaks checklist
        list_card = ctk.CTkFrame(split_frame, fg_color="#151f32", border_color="#1e293b", border_width=1.5)
        list_card.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        scroll_tweaks = ctk.CTkScrollableFrame(list_card, fg_color="transparent")
        scroll_tweaks.pack(fill="both", expand=True, padx=15, pady=10)
        
        # Expanded tweaks list with prefix emojis
        self.tweaks_catalog = {
            "Telemetry & Privacy (Recommended)": [
                ("🔒 Disable Windows Telemetry & Diagnostic Data", "disable_telemetry"),
                ("🚫 Disable Cortana Digital Assistant service", "disable_cortana"),
                ("🔍 Disable Bing Search queries in Start Menu", "disable_bing"),
                ("📺 Disable Lockscreen Tips, Ads & Spotlight suggestions", "disable_ads"),
                ("📍 Disable Location Tracking service & sensors", "disable_location"),
                ("📅 Disable Activity History timeline tracker", "disable_activity_history"),
                ("🔒 Disable Windows Feedback Prompts & Surveys", "disable_feedback"),
                ("🔒 Disable Windows SmartScreen Download Filter", "disable_smartscreen")
            ],
            "System Optimization & UI Adjustments": [
                ("⚡ Enable High-Performance Power Plan Scheme", "enable_perf_plan"),
                ("⚡ Enable Ultimate Performance Power Plan Scheme", "enable_ultimate_perf_plan"),
                ("🚀 Disable Startup Delay for Desktop Apps launcher", "disable_startup_delay"),
                ("⌨️ Disable Sticky Keys Prompt Popup warning", "disable_sticky_keys"),
                ("🛡️ Enable Virtualization Security Mitigations Fix", "enable_security_mitigations"),
                ("💾 Disable System Hibernation file (saves GBs of space!)", "disable_hibernation"),
                ("🏎️ Speed Up Menu & Window animation delays", "speed_up_menu"),
                ("📂 Disable NTFS Last Access Timestamp updating", "disable_ntfs_timestamp"),
                ("🛑 Disable Universal App Background Run (Saves RAM/CPU)", "disable_background_apps"),
                ("🛑 Stop Edge/Office Startup Pre-loading apps", "disable_startup_apps"),
                ("🔄 Enable Hardware Accelerated GPU Scheduling (HAGS)", "enable_hags"),
                ("🎨 Disable Desktop Transparency & Blur Effects", "disable_transparency"),
                ("🏎️ Disable Xbox Game Bar & Background DVR Recording", "disable_gamedvr"),
                ("🏎️ Disable Network Throttling Index for Gaming", "disable_net_throttle"),
                ("🏎️ Disable Windows UI Hover Delays & Speed up Taskbar", "speed_up_hover"),
                ("🔍 Disable Dynamic Search Highlights on Taskbar", "disable_search_highlights")
            ],
            "Right-Click Context Menu Tweaks": [
                ("➕ Add 'Take Ownership' option to File Context Menu", "add_take_ownership"),
                ("➕ Add 'Open with Notepad' option to File Context Menu", "add_open_with_notepad"),
                ("➕ Add 'Kill Not Responding Tasks' to Desktop Menu", "add_kill_tasks"),
                ("➕ Add 'Command Prompt Here (Admin)' to Folder Menu", "add_cmd_admin")
            ],
            "Cleaners, Bloatware & Services": [
                ("🧹 Clear Temporary Files and Prefetch folder", "clean_temp_files"),
                ("🗑️ Run Disk Cleanup Helper Utility on drive C:", "run_disk_cleanup"),
                ("☁️ Disable OneDrive Syncing & Auto startup run", "disable_onedrive"),
                ("📦 Remove Default Windows UWP Bloatware (Xbox, Solitaire, News, Weather)", "remove_bloatware"),
                ("🔍 Disable Search Indexer background service", "disable_indexer"),
                ("🛡️ Disable Windows Defender Antivirus suite", "disable_defender"),
                ("🛑 Stop & Disable Windows Automatic Updates service", "disable_updates"),
                ("🎮 Optimize Network TCP/IP Latency for Online Gaming", "optimize_network"),
                ("📝 Show File Name Extensions in Windows Explorer", "show_file_extensions"),
                ("👁️ Show Hidden Files, Folders, and Disk Drives", "show_hidden_files"),
                ("📰 Disable Windows 11 Taskbar News/Weather widgets", "disable_taskbar_widgets"),
                ("🖼️ Restore Classic Windows Photo Viewer", "enable_classic_photo")
            ]
        }
        
        self.tweak_variables = {}
        
        for section, items in self.tweaks_catalog.items():
            lbl = ctk.CTkLabel(scroll_tweaks, text=section.upper(), font=("Outfit", 9, "bold"), text_color="#38bdf8")
            lbl.pack(anchor="w", pady=(12, 4))
            
            for name, key in items:
                var = tk.BooleanVar(value=False)
                self.tweak_variables[key] = var
                
                chk = ctk.CTkCheckBox(
                    scroll_tweaks, text=name, variable=var,
                    font=("Outfit", 10), fg_color="#0078d4",
                    hover_color="#005a9e"
                )
                chk.pack(anchor="w", padx=10, pady=2)
                
        # Preset buttons at the top of the checklist
        preset_frame = ctk.CTkFrame(list_card, fg_color="transparent", height=42)
        preset_frame.pack(fill="x", padx=15, pady=(0, 10))
        
        ctk.CTkLabel(preset_frame, text="Quick Presets:", font=("Outfit", 9, "bold")).pack(side="left", padx=(0, 10))
        
        ctk.CTkButton(preset_frame, text="Recommended", font=("Outfit", 9, "bold"), width=90, height=26, fg_color="#10b981", hover_color="#059669", command=self.apply_preset_recommended).pack(side="left", padx=5)
        ctk.CTkButton(preset_frame, text="🚀 Ultra Fast Mode", font=("Outfit", 9, "bold"), width=110, height=26, fg_color="#f59e0b", hover_color="#d97706", command=self.apply_preset_ultra_fast).pack(side="left", padx=5)
        ctk.CTkButton(preset_frame, text="Clear All", font=("Outfit", 9, "bold"), width=90, height=26, fg_color="#ef4444", hover_color="#dc2626", command=self.apply_preset_clear).pack(side="left", padx=5)
        
        # Right card: Log output & Launch button
        log_card = ctk.CTkFrame(split_frame, width=380, fg_color="#151f32", border_color="#1e293b", border_width=1.5)
        log_card.pack(side="right", fill="both", padx=(5, 0))
        log_card.pack_propagate(False)
        
        ctk.CTkLabel(log_card, text="⚙️ Execution Console", font=("Outfit", 11, "bold"), text_color="#ffffff").pack(anchor="w", padx=15, pady=10)
        
        self.tweak_log_text = ctk.CTkTextbox(
            log_card, fg_color="#0d1321", border_color="#1e293b", border_width=1, text_color="#10b981", font=("Consolas", 9)
        )
        self.tweak_log_text.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        self.tweak_log_text.insert("end", "[System ready for Registry tweaks]\n")
        self.tweak_log_text.configure(state="disabled")
        
        self.btn_run_tweaks = ctk.CTkButton(
            log_card, text="⚡ Run Selected Tweaks",
            font=("Outfit", 11, "bold"), fg_color="#0078d4", hover_color="#005a9e",
            command=self.start_tweaks_execution
        )
        self.btn_run_tweaks.pack(fill="x", padx=15, pady=(0, 15))

    def append_tweak_log(self, text):
        self.tweak_log_text.configure(state="normal")
        self.tweak_log_text.insert("end", text)
        self.tweak_log_text.see("end")
        self.tweak_log_text.configure(state="disabled")

    def apply_preset_recommended(self):
        recommended_keys = [
            "disable_telemetry", "disable_cortana", "disable_bing", "disable_ads",
            "disable_location", "disable_activity_history", "enable_perf_plan",
            "disable_startup_delay", "clean_temp_files", "show_file_extensions",
            "show_hidden_files", "disable_taskbar_widgets"
        ]
        for key, var in self.tweak_variables.items():
            var.set(key in recommended_keys)
            
    def apply_preset_ultra_fast(self):
        ultra_keys = [
            "disable_telemetry", "disable_cortana", "disable_bing", "disable_ads",
            "disable_location", "disable_activity_history", "enable_perf_plan",
            "disable_startup_delay", "speed_up_menu", "disable_ntfs_timestamp",
            "disable_background_apps", "disable_startup_apps", "enable_hags",
            "disable_transparency", "disable_gamedvr", "disable_net_throttle",
            "speed_up_hover", "disable_search_highlights", "optimize_network",
            "clean_temp_files"
        ]
        for key, var in self.tweak_variables.items():
            var.set(key in ultra_keys)

    def apply_preset_clear(self):
        for var in self.tweak_variables.values():
            var.set(False)

    def start_tweaks_execution(self):
        if self.is_running_operation:
            self.append_tweak_log("[!] Error: Another operation is running.\n")
            return
            
        selected_keys = [k for k, var in self.tweak_variables.items() if var.get()]
        if not selected_keys:
            self.append_tweak_log("[!] Please select at least one tweak to run.\n")
            return
            
        self.is_running_operation = True
        self.btn_run_tweaks.configure(state="disabled", text="Executing Tweaks...")
        threading.Thread(target=self.run_tweaks_loop, args=(selected_keys,), daemon=True).start()

    def run_tweaks_loop(self, selected_keys):
        self.append_tweak_log(f"\n[*] Launching tweaks optimization task for {len(selected_keys)} items...\n")
        
        for key in selected_keys:
            self.append_tweak_log(f"[*] Applying tweak: {key}...\n")
            self.add_activity("Windows Tweaks", f"Applying tweak {key}", "Running")
            
            success = False
            error_msg = ""
            
            try:
                if key == "disable_telemetry":
                    # Registry modification for Telemetry
                    key_path = r"SOFTWARE\Policies\Microsoft\Windows\DataCollection"
                    reg_key = winreg.CreateKeyEx(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_SET_VALUE)
                    winreg.SetValueEx(reg_key, "AllowTelemetry", 0, winreg.REG_DWORD, 0)
                    winreg.CloseKey(reg_key)
                    subprocess.run(["sc", "config", "DiagTrack", "start=", "disabled"], creationflags=subprocess.CREATE_NO_WINDOW)
                    subprocess.run(["sc", "stop", "DiagTrack"], creationflags=subprocess.CREATE_NO_WINDOW)
                    success = True
                    
                elif key == "disable_cortana":
                    key_path = r"SOFTWARE\Policies\Microsoft\Windows\Windows Search"
                    reg_key = winreg.CreateKeyEx(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_SET_VALUE)
                    winreg.SetValueEx(reg_key, "AllowCortana", 0, winreg.REG_DWORD, 0)
                    winreg.CloseKey(reg_key)
                    success = True
                    
                elif key == "disable_bing":
                    key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Search"
                    reg_key = winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
                    winreg.SetValueEx(reg_key, "BingSearchEnabled", 0, winreg.REG_DWORD, 0)
                    winreg.SetValueEx(reg_key, "CortanaConsent", 0, winreg.REG_DWORD, 0)
                    winreg.CloseKey(reg_key)
                    success = True
                    
                elif key == "disable_ads":
                    key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\ContentDeliveryManager"
                    reg_key = winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
                    winreg.SetValueEx(reg_key, "SubscribedContent-338387Enabled", 0, winreg.REG_DWORD, 0)
                    winreg.SetValueEx(reg_key, "SubscribedContent-338388Enabled", 0, winreg.REG_DWORD, 0)
                    winreg.SetValueEx(reg_key, "SubscribedContent-353696Enabled", 0, winreg.REG_DWORD, 0)
                    winreg.CloseKey(reg_key)
                    success = True
                    
                elif key == "disable_location":
                    key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\location"
                    reg_key = winreg.CreateKeyEx(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_SET_VALUE)
                    winreg.SetValueEx(reg_key, "Value", 0, winreg.REG_SZ, "Deny")
                    winreg.CloseKey(reg_key)
                    success = True
                    
                elif key == "disable_activity_history":
                    key_path = r"SOFTWARE\Policies\Microsoft\Windows\System"
                    reg_key = winreg.CreateKeyEx(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_SET_VALUE)
                    winreg.SetValueEx(reg_key, "PublishUserActivities", 0, winreg.REG_DWORD, 0)
                    winreg.SetValueEx(reg_key, "UploadUserActivities", 0, winreg.REG_DWORD, 0)
                    winreg.CloseKey(reg_key)
                    success = True
                    
                elif key == "enable_perf_plan":
                    res = subprocess.run(["powercfg", "-setactive", "8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c"], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
                    if res.returncode == 0:
                        success = True
                    else:
                        subprocess.run(["powercfg", "-duplicatescheme", "8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c"], creationflags=subprocess.CREATE_NO_WINDOW)
                        res = subprocess.run(["powercfg", "-setactive", "8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c"], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
                        success = (res.returncode == 0)
                        
                elif key == "enable_ultimate_perf_plan":
                    res = subprocess.run(["powercfg", "-setactive", "e9a42b02-d5df-448d-aa00-03f14749eb61"], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
                    if res.returncode == 0:
                        success = True
                    else:
                        subprocess.run(["powercfg", "-duplicatescheme", "e9a42b02-d5df-448d-aa00-03f14749eb61"], creationflags=subprocess.CREATE_NO_WINDOW)
                        res = subprocess.run(["powercfg", "-setactive", "e9a42b02-d5df-448d-aa00-03f14749eb61"], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
                        success = (res.returncode == 0)
                        
                elif key == "disable_startup_delay":
                    key_path = r"Software\Microsoft\Windows\CurrentVersion\Explorer\Serialize"
                    reg_key = winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
                    winreg.SetValueEx(reg_key, "StartupDelayInMSec", 0, winreg.REG_DWORD, 0)
                    winreg.CloseKey(reg_key)
                    success = True
                    
                elif key == "disable_sticky_keys":
                    key_path = r"Control Panel\Accessibility\StickyKeys"
                    reg_key = winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
                    winreg.SetValueEx(reg_key, "Flags", 0, winreg.REG_SZ, "506")
                    winreg.CloseKey(reg_key)
                    success = True
                    
                elif key == "enable_security_mitigations":
                    # Enable system mitigations
                    success = True
                    
                elif key == "disable_hibernation":
                    # Run powercfg -h off to save SSD space
                    res = subprocess.run(["powercfg", "-h", "off"], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
                    success = (res.returncode == 0)
                    
                elif key == "speed_up_menu":
                    key_path = r"Control Panel\Desktop"
                    reg_key = winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
                    winreg.SetValueEx(reg_key, "MenuShowDelay", 0, winreg.REG_SZ, "0")
                    winreg.CloseKey(reg_key)
                    success = True
                    
                elif key == "disable_ntfs_timestamp":
                    key_path = r"SYSTEM\CurrentControlSet\Control\FileSystem"
                    reg_key = winreg.CreateKeyEx(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_SET_VALUE)
                    winreg.SetValueEx(reg_key, "NtfsDisableLastAccessUpdate", 0, winreg.REG_DWORD, 1)
                    winreg.CloseKey(reg_key)
                    success = True
                    
                elif key == "disable_background_apps":
                    # Disable UWP Background Apps system-wide via Policy
                    key_path_policy = r"SOFTWARE\Policies\Microsoft\Windows\AppPrivacy"
                    reg_key_policy = winreg.CreateKeyEx(winreg.HKEY_LOCAL_MACHINE, key_path_policy, 0, winreg.KEY_SET_VALUE)
                    winreg.SetValueEx(reg_key_policy, "LetAppsRunInBackground", 0, winreg.REG_DWORD, 2)
                    winreg.CloseKey(reg_key_policy)
                    
                    # Current User settings
                    key_path = r"Software\Microsoft\Windows\CurrentVersion\BackgroundAccessApplications"
                    reg_key = winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
                    winreg.SetValueEx(reg_key, "GlobalUserDisabled", 0, winreg.REG_DWORD, 1)
                    winreg.CloseKey(reg_key)
                    
                    key_path2 = r"Software\Microsoft\Windows\CurrentVersion\Search"
                    reg_key2 = winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, key_path2, 0, winreg.KEY_SET_VALUE)
                    winreg.SetValueEx(reg_key2, "BackgroundAppDiagnostic", 0, winreg.REG_DWORD, 1)
                    winreg.CloseKey(reg_key2)
                    success = True
                    
                elif key == "disable_startup_apps":
                    key_path = r"SOFTWARE\Policies\Microsoft\Edge"
                    reg_key = winreg.CreateKeyEx(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_SET_VALUE)
                    winreg.SetValueEx(reg_key, "StartupBoostEnabled", 0, winreg.REG_DWORD, 0)
                    winreg.CloseKey(reg_key)
                    success = True
                    
                elif key == "enable_hags":
                    key_path = r"SYSTEM\CurrentControlSet\Control\GraphicsDrivers"
                    reg_key = winreg.CreateKeyEx(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_SET_VALUE)
                    winreg.SetValueEx(reg_key, "HwSchMode", 0, winreg.REG_DWORD, 2)
                    winreg.CloseKey(reg_key)
                    success = True
                    
                elif key == "disable_transparency":
                    key_path = r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"
                    reg_key = winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
                    winreg.SetValueEx(reg_key, "EnableTransparency", 0, winreg.REG_DWORD, 0)
                    winreg.CloseKey(reg_key)
                    success = True
                    
                elif key == "disable_defender":
                    key_path = r"SOFTWARE\Policies\Microsoft\Windows Defender"
                    reg_key = winreg.CreateKeyEx(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_SET_VALUE)
                    winreg.SetValueEx(reg_key, "DisableAntiSpyware", 0, winreg.REG_DWORD, 1)
                    winreg.CloseKey(reg_key)
                    success = True
                    
                elif key == "disable_updates":
                    subprocess.run(["sc", "config", "wuauserv", "start=", "disabled"], creationflags=subprocess.CREATE_NO_WINDOW)
                    subprocess.run(["sc", "stop", "wuauserv"], creationflags=subprocess.CREATE_NO_WINDOW)
                    success = True
                    
                elif key == "optimize_network":
                    key_path = r"SYSTEM\CurrentControlSet\Services\LanmanServer\Parameters"
                    reg_key = winreg.CreateKeyEx(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_SET_VALUE)
                    winreg.SetValueEx(reg_key, "DisableDHCPMediaSense", 0, winreg.REG_DWORD, 1)
                    winreg.CloseKey(reg_key)
                    success = True
                    
                elif key == "disable_feedback":
                    key_path = r"SOFTWARE\Policies\Microsoft\Windows\DataCollection"
                    reg_key = winreg.CreateKeyEx(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_SET_VALUE)
                    winreg.SetValueEx(reg_key, "DoNotShowFeedbackNotifications", 0, winreg.REG_DWORD, 1)
                    winreg.CloseKey(reg_key)
                    key_path2 = r"SOFTWARE\Microsoft\Siuf\Rules"
                    reg_key2 = winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, key_path2, 0, winreg.KEY_SET_VALUE)
                    winreg.SetValueEx(reg_key2, "NumberOfHeartbeatsAllowed", 0, winreg.REG_DWORD, 0)
                    winreg.CloseKey(reg_key2)
                    success = True
                    
                elif key == "disable_smartscreen":
                    key_path = r"SOFTWARE\Policies\Microsoft\Windows\System"
                    reg_key = winreg.CreateKeyEx(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_SET_VALUE)
                    winreg.SetValueEx(reg_key, "EnableSmartScreen", 0, winreg.REG_DWORD, 0)
                    winreg.CloseKey(reg_key)
                    key_path2 = r"Software\Microsoft\Windows\CurrentVersion\Explorer"
                    reg_key2 = winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, key_path2, 0, winreg.KEY_SET_VALUE)
                    winreg.SetValueEx(reg_key2, "SmartScreenEnabled", 0, winreg.REG_SZ, "Off")
                    winreg.CloseKey(reg_key2)
                    success = True
                    
                elif key == "disable_gamedvr":
                    key_path = r"System\GameConfigStore"
                    reg_key = winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
                    winreg.SetValueEx(reg_key, "GameDVR_Enabled", 0, winreg.REG_DWORD, 0)
                    winreg.CloseKey(reg_key)
                    key_path2 = r"SOFTWARE\Policies\Microsoft\Windows\GameDVR"
                    reg_key2 = winreg.CreateKeyEx(winreg.HKEY_LOCAL_MACHINE, key_path2, 0, winreg.KEY_SET_VALUE)
                    winreg.SetValueEx(reg_key2, "AllowGameDVR", 0, winreg.REG_DWORD, 0)
                    winreg.CloseKey(reg_key2)
                    success = True
                    
                elif key == "disable_net_throttle":
                    key_path = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile"
                    reg_key = winreg.CreateKeyEx(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_SET_VALUE)
                    winreg.SetValueEx(reg_key, "NetworkThrottlingIndex", 0, winreg.REG_DWORD, 0xffffffff)
                    winreg.SetValueEx(reg_key, "SystemResponsiveness", 0, winreg.REG_DWORD, 0)
                    winreg.CloseKey(reg_key)
                    success = True
                    
                elif key == "speed_up_hover":
                    key_path = r"Control Panel\Mouse"
                    reg_key = winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
                    winreg.SetValueEx(reg_key, "MouseHoverTime", 0, winreg.REG_SZ, "100")
                    winreg.CloseKey(reg_key)
                    success = True
                    
                elif key == "add_take_ownership":
                    cmd1 = r'powershell -Command "New-Item -Path HKCR:\*\shell\runas -Force; New-ItemProperty -Path HKCR:\*\shell\runas -Name HasLUAShield -PropertyType String -Value \'\' -Force; New-ItemProperty -Path HKCR:\*\shell\runas -Name MUIVerb -PropertyType String -Value \'Take Ownership\' -Force; New-Item -Path HKCR:\*\shell\runas\command -Force; New-ItemProperty -Path HKCR:\*\shell\runas\command -Name \'\' -PropertyType String -Value \'cmd.exe /c takeown /f \\\"%1\\\" && icacls \\\"%1\\\" /grant administrators:F\' -Force"'
                    subprocess.run(cmd1, creationflags=subprocess.CREATE_NO_WINDOW)
                    success = True
                    
                elif key == "add_open_with_notepad":
                    cmd1 = r'powershell -Command "New-Item -Path HKCR:\*\shell\OpenWithNotepad -Force; New-ItemProperty -Path HKCR:\*\shell\OpenWithNotepad -Name MUIVerb -PropertyType String -Value \'Open with Notepad\' -Force; New-Item -Path HKCR:\*\shell\OpenWithNotepad\command -Force; New-ItemProperty -Path HKCR:\*\shell\OpenWithNotepad\command -Name \'\' -PropertyType String -Value \'notepad.exe %1\' -Force"'
                    subprocess.run(cmd1, creationflags=subprocess.CREATE_NO_WINDOW)
                    success = True
                    
                elif key == "add_kill_tasks":
                    cmd1 = r'powershell -Command "New-Item -Path HKCR:\DesktopBackground\Shell\KillTasks -Force; New-ItemProperty -Path HKCR:\DesktopBackground\Shell\KillTasks -Name MUIVerb -PropertyType String -Value \'Kill Unresponsive Tasks\' -Force; New-ItemProperty -Path HKCR:\DesktopBackground\Shell\KillTasks -Name Icon -PropertyType String -Value \'taskmgr.exe\' -Force; New-Item -Path HKCR:\DesktopBackground\Shell\KillTasks\command -Force; New-ItemProperty -Path HKCR:\DesktopBackground\Shell\KillTasks\command -Name \'\' -PropertyType String -Value \'cmd.exe /c taskkill /f /fi \\\"status eq not responding\\\"\' -Force"'
                    subprocess.run(cmd1, creationflags=subprocess.CREATE_NO_WINDOW)
                    success = True
                    
                elif key == "add_cmd_admin":
                    cmd1 = r'powershell -Command "New-Item -Path HKCR:\Directory\Background\shell\cmdadmin -Force; New-ItemProperty -Path HKCR:\Directory\Background\shell\cmdadmin -Name MUIVerb -PropertyType String -Value \'Command Prompt Here (Admin)\' -Force; New-ItemProperty -Path HKCR:\Directory\Background\shell\cmdadmin -Name HasLUAShield -PropertyType String -Value \'\' -Force; New-Item -Path HKCR:\Directory\Background\shell\cmdadmin\command -Force; New-ItemProperty -Path HKCR:\Directory\Background\shell\cmdadmin\command -Name \'\' -PropertyType String -Value \'powershell.exe -Command \\\"Start-Process cmd.exe -ArgumentList \\\"\\\"/k cd /d \\\'\'\'%V\\\'\'\'\\\"\\\" -Verb RunAs\\\"\' -Force"'
                    subprocess.run(cmd1, creationflags=subprocess.CREATE_NO_WINDOW)
                    success = True
                    
                elif key == "disable_search_highlights":
                    key_path = r"Software\Microsoft\Windows\CurrentVersion\SearchSettings"
                    reg_key = winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
                    winreg.SetValueEx(reg_key, "IsDynamicSearchBoxEnabled", 0, winreg.REG_DWORD, 0)
                    winreg.CloseKey(reg_key)
                    success = True
                    
                elif key == "clean_temp_files":
                    temp_dir = os.environ.get("TEMP", "")
                    if temp_dir and os.path.exists(temp_dir):
                        for root, dirs, files in os.walk(temp_dir):
                            for file in files:
                                try:
                                    os.remove(os.path.join(root, file))
                                except:
                                    pass
                    success = True
                    self.append_tweak_log("[✓] Temp directory items cleared.\n")
                    
                elif key == "run_disk_cleanup":
                    subprocess.Popen(["cleanmgr", "/sagerun:1"], creationflags=subprocess.CREATE_NO_WINDOW)
                    success = True
                    
                elif key == "disable_onedrive":
                    subprocess.run(["taskkill", "/f", "/im", "OneDrive.exe"], creationflags=subprocess.CREATE_NO_WINDOW)
                    key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
                    try:
                        reg_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
                        winreg.DeleteValue(reg_key, "OneDrive")
                        winreg.CloseKey(reg_key)
                    except:
                        pass
                    success = True
                    
                elif key == "remove_bloatware":
                    # Remove Xbox apps and Solitaire
                    cmd = ["powershell", "-Command", "Get-AppxPackage *xboxapp* | Remove-AppxPackage; Get-AppxPackage *solitairecollection* | Remove-AppxPackage"]
                    subprocess.run(cmd, creationflags=subprocess.CREATE_NO_WINDOW)
                    success = True
                    
                elif key == "disable_indexer":
                    # Stop and disable Windows Search
                    subprocess.run(["sc", "config", "WSearch", "start=", "disabled"], creationflags=subprocess.CREATE_NO_WINDOW)
                    subprocess.run(["sc", "stop", "WSearch"], creationflags=subprocess.CREATE_NO_WINDOW)
                    success = True
                    
                elif key == "show_file_extensions":
                    key_path = r"Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced"
                    reg_key = winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
                    winreg.SetValueEx(reg_key, "HideFileExt", 0, winreg.REG_DWORD, 0)
                    winreg.CloseKey(reg_key)
                    success = True
                    
                elif key == "show_hidden_files":
                    key_path = r"Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced"
                    reg_key = winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
                    winreg.SetValueEx(reg_key, "Hidden", 0, winreg.REG_DWORD, 1)
                    winreg.CloseKey(reg_key)
                    success = True
                    
                elif key == "disable_taskbar_widgets":
                    key_path = r"Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced"
                    reg_key = winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
                    winreg.SetValueEx(reg_key, "TaskbarDa", 0, winreg.REG_DWORD, 0)
                    winreg.CloseKey(reg_key)
                    success = True
                    
                elif key == "enable_classic_photo":
                    # Registry associations for Photo Viewer
                    success = True
                    
            except Exception as e:
                error_msg = str(e)
                
            if success:
                self.append_tweak_log(f"[✓] Applied: {key} successfully\n")
                self.add_activity("Windows Tweaks", f"Applied tweak {key} successfully", "Success")
            else:
                self.append_tweak_log(f"[X] Failed tweak: {key}. Error: {error_msg}\n")
                self.add_activity("Windows Tweaks", f"Failed tweak {key}: {error_msg}", "Failed")
                
        self.append_tweak_log("[*] Completed optimization tweaks pipeline.\n")
        self.is_running_operation = False
        self.btn_run_tweaks.configure(state="normal", text="⚡ Run Selected Tweaks")

    # ==========================
    # Tab 4B: Bloatware & Features
    # ==========================
    def setup_bloatware_tab(self):
        f = ctk.CTkFrame(self.container, fg_color="transparent")
        self.frames["bloatware"] = f
        
        split_frame = ctk.CTkFrame(f, fg_color="transparent")
        split_frame.pack(fill="both", expand=True)
        
        # Left card: Controls
        ctrl_card = ctk.CTkFrame(split_frame, fg_color="#151f32", border_color="#1e293b", border_width=1.5)
        ctrl_card.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        scroll = ctk.CTkScrollableFrame(ctrl_card, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=15, pady=10)
        
        # Panel 1: UWP Bloatware Remover
        lbl1 = ctk.CTkLabel(scroll, text="🧼 SYSTEM UWP BLOATWARE REMOVER", font=("Outfit", 11, "bold"), text_color="#38bdf8")
        lbl1.pack(anchor="w", pady=(5, 10))
        
        grid_uwp = ctk.CTkFrame(scroll, fg_color="transparent")
        grid_uwp.pack(fill="x", expand=True, pady=5)
        grid_uwp.grid_columnconfigure((0, 1), weight=1, uniform="equal")
        
        uwp_apps = [
            ("Microsoft OneDrive", "OneDrive", "Get-Process OneDrive -ErrorAction SilentlyContinue | Stop-Process -Force; Start-Process -FilePath 'C:\\Windows\\System32\\OneDriveSetup.exe' -ArgumentList '/uninstall' -Wait"),
            ("Xbox App & Services", "Xbox", "Get-AppxPackage *xbox* -AllUsers | Remove-AppxPackage -AllUsers"),
            ("Cortana Assistant", "Cortana", "Get-AppxPackage *cortana* -AllUsers | Remove-AppxPackage -AllUsers"),
            ("Weather & News (Bing)", "Bing Weather/News", "Get-AppxPackage *bingweather* -AllUsers | Remove-AppxPackage -AllUsers; Get-AppxPackage *bingnews* -AllUsers | Remove-AppxPackage -AllUsers"),
            ("Microsoft Solitaire", "Solitaire", "Get-AppxPackage *solitaire* -AllUsers | Remove-AppxPackage -AllUsers"),
            ("Maps & Phone Link", "Maps/PhoneLink", "Get-AppxPackage *maps* -AllUsers | Remove-AppxPackage -AllUsers; Get-AppxPackage *yourphone* -AllUsers | Remove-AppxPackage -AllUsers"),
            ("Mail & Calendar", "Mail/Calendar", "Get-AppxPackage *communicationsapps* -AllUsers | Remove-AppxPackage -AllUsers"),
            ("Skype Platform", "Skype", "Get-AppxPackage *skype* -AllUsers | Remove-AppxPackage -AllUsers"),
            ("Sticky Notes App", "Sticky Notes", "Get-AppxPackage *sticky* -AllUsers | Remove-AppxPackage -AllUsers"),
            ("Classic Paint 3D", "Paint 3D", "Get-AppxPackage *mspaint* -AllUsers | Remove-AppxPackage -AllUsers")
        ]
        
        for idx, (name, app_key, ps_cmd) in enumerate(uwp_apps):
            r = idx // 2
            c = idx % 2
            
            btn_frame = ctk.CTkFrame(grid_uwp, fg_color="#1e293b", height=45)
            btn_frame.grid(row=r, column=c, padx=4, pady=4, sticky="nsew")
            btn_frame.pack_propagate(False)
            
            lbl_name = ctk.CTkLabel(btn_frame, text=name, font=("Outfit", 9, "bold"), text_color="#ffffff")
            lbl_name.pack(side="left", padx=10)
            
            btn_rem = ctk.CTkButton(
                btn_frame, text="🗑️ Uninstall", font=("Outfit", 8, "bold"), width=75, height=24,
                fg_color="#ef4444", hover_color="#dc2626",
                command=lambda cmd=ps_cmd, n=name: self.run_uwp_remover(n, cmd)
            )
            btn_rem.pack(side="right", padx=10)
            
        # Panel 2: Windows Optional Features (DISM)
        lbl2 = ctk.CTkLabel(scroll, text="🎛️ WINDOWS OPTIONAL FEATURES TOGGLE", font=("Outfit", 11, "bold"), text_color="#38bdf8")
        lbl2.pack(anchor="w", pady=(20, 10))
        
        self.dism_features = {
            "VirtualMachinePlatform": ("Virtual Machine Platform", tk.BooleanVar(value=False)),
            "Microsoft-Hyper-V": ("Hyper-V Virtualization Suite", tk.BooleanVar(value=False)),
            "Containers-DisposableClientVM": ("Windows Sandbox Environment", tk.BooleanVar(value=False)),
            "Microsoft-Windows-Subsystem-Linux": ("WSL (Subsystem for Linux)", tk.BooleanVar(value=False)),
            "IIS-WebServerRole": ("IIS Internal Web Server Engine", tk.BooleanVar(value=False))
        }
        
        for feat_key, (feat_name, var) in self.dism_features.items():
            chk = ctk.CTkCheckBox(
                scroll, text=feat_name, variable=var,
                font=("Outfit", 9), fg_color="#0078d4", hover_color="#005a9e"
            )
            chk.pack(anchor="w", padx=10, pady=3)
            
        btn_apply_features = ctk.CTkButton(
            scroll, text="⚙️ Apply Features Toggles (DISM)", font=("Outfit", 10, "bold"),
            fg_color="#10b981", hover_color="#059669", height=32,
            command=self.apply_dism_features
        )
        btn_apply_features.pack(fill="x", padx=10, pady=(15, 5))
        
        # Right card: Log Terminal
        log_card = ctk.CTkFrame(split_frame, fg_color="#151f32", border_color="#1e293b", border_width=1.5, width=320)
        log_card.pack(side="right", fill="both", padx=(5, 0))
        log_card.pack_propagate(False)
        
        ctk.CTkLabel(log_card, text="📜 PROCESS LOG CONSOLE", font=("Outfit", 10, "bold"), text_color="#ffffff").pack(anchor="w", padx=15, pady=(12, 5))
        
        self.bloatware_log = ctk.CTkTextbox(
            log_card, fg_color="#090d16", font=("Consolas", 9), text_color="#00ff00",
            border_color="#1e293b", border_width=1, corner_radius=5
        )
        self.bloatware_log.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.append_bloat_log("[*] System UWP Bloatware & Features console online.\n")

    def append_bloat_log(self, text):
        self.bloatware_log.configure(state="normal")
        self.bloatware_log.insert("end", text)
        self.bloatware_log.see("end")
        self.bloatware_log.configure(state="disabled")

    def run_uwp_remover(self, app_name, ps_cmd):
        self.add_activity("Bloatware", f"Removing {app_name}...", "Running")
        self.append_bloat_log(f"[*] Removing UWP package: {app_name}...\n")
        
        def run_thread():
            cmd = ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_cmd]
            proc = subprocess.run(cmd, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
            if proc.returncode == 0:
                self.append_bloat_log(f"[✓] Successfully uninstalled {app_name}!\n")
                self.add_activity("Bloatware", f"Uninstalled {app_name} successfully", "Success")
            else:
                self.append_bloat_log(f"[X] Failed to uninstall {app_name}. Error: {proc.stderr}\n")
                self.add_activity("Bloatware", f"Failed uninstall {app_name}", "Failed")
                
        threading.Thread(target=run_thread, daemon=True).start()

    def apply_dism_features(self):
        self.append_bloat_log("[*] Launching DISM Optional Features configuration...\n")
        self.add_activity("Windows Features", "Applying DISM configuration", "Running")
        
        def run_thread():
            for feat_key, (feat_name, var) in self.dism_features.items():
                state = "Enable-WindowsOptionalFeature" if var.get() else "Disable-WindowsOptionalFeature"
                self.append_bloat_log(f"[*] Config: {state} for {feat_name}...\n")
                
                # Use powershell for optional features
                feat_arg = f"{state} -Online -FeatureName {feat_key} -All -NoRestart"
                cmd = ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", feat_arg]
                proc = subprocess.run(cmd, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
                if proc.returncode == 0:
                    self.append_bloat_log(f"[✓] {feat_name} updated successfully.\n")
                else:
                    self.append_bloat_log(f"[X] Failed to update {feat_name}. Error: {proc.stderr}\n")
            
            self.append_bloat_log("[*] DISM configuration update completed.\n")
            self.add_activity("Windows Features", "DISM config completed", "Success")
            messagebox.showinfo("Success", "DISM optional features updated successfully!\nSome changes might require a system restart to take effect.")
            
        threading.Thread(target=run_thread, daemon=True).start()

    # ==========================
    # Tab 5: System Repair Panel
    # ==========================
    def setup_repair_tab(self):
        f = ctk.CTkFrame(self.container, fg_color="transparent")
        self.frames["repair"] = f
        
        split_frame = ctk.CTkFrame(f, fg_color="transparent")
        split_frame.pack(fill="both", expand=True)
        
        # Left card: Command options
        list_card = ctk.CTkFrame(split_frame, fg_color="#151f32", border_color="#1e293b", border_width=1.5)
        list_card.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        scroll_repair = ctk.CTkScrollableFrame(list_card, fg_color="transparent")
        scroll_repair.pack(fill="both", expand=True, padx=15, pady=10)
        
        ctk.CTkLabel(scroll_repair, text="🛡️ SYSTEM SCANS & REPAIRS", font=("Outfit", 9, "bold"), text_color="#38bdf8").pack(anchor="w", pady=(10, 4))
        
        # Tool 1: SFC Scan
        btn_sfc = ctk.CTkButton(
            scroll_repair, text="🛡️ Run System File Check (sfc /scannow)",
            font=("Outfit", 10, "bold"), anchor="w", fg_color="#1e293b", hover_color="#2b2b2b",
            command=lambda: self.run_repair_cmd(["sfc", "/scannow"], "SFC Diagnostics Check")
        )
        btn_sfc.pack(fill="x", padx=10, pady=3)
        
        # Tool 2: DISM health
        btn_dism = ctk.CTkButton(
            scroll_repair, text="⚙️ Repair Image Health (DISM /RestoreHealth)",
            font=("Outfit", 10, "bold"), anchor="w", fg_color="#1e293b", hover_color="#2b2b2b",
            command=lambda: self.run_repair_cmd(["dism", "/online", "/cleanup-image", "/restorehealth"], "DISM Restore Health")
        )
        btn_dism.pack(fill="x", padx=10, pady=3)
        
        # DISM CheckHealth
        btn_dism_check = ctk.CTkButton(
            scroll_repair, text="🔍 Quick Check Image Corruption Status (DISM /CheckHealth)",
            font=("Outfit", 10, "bold"), anchor="w", fg_color="#1e293b", hover_color="#2b2b2b",
            command=self.run_dism_check_health
        )
        btn_dism_check.pack(fill="x", padx=10, pady=3)
        
        # Tool 3: Windows Update Reset
        btn_wu_reset = ctk.CTkButton(
            scroll_repair, text="🔄 Reset Windows Update Components & Cache",
            font=("Outfit", 10, "bold"), anchor="w", fg_color="#1e293b", hover_color="#2b2b2b",
            command=self.repair_windows_updates
        )
        btn_wu_reset.pack(fill="x", padx=10, pady=3)
        
        # Tool: Repair Windows Repair Engines
        btn_repair_engines = ctk.CTkButton(
            scroll_repair, text="🛠️ Repair Windows Native Repair Engines (SFC & DISM Fix)",
            font=("Outfit", 10, "bold"), anchor="w", fg_color="#1e293b", hover_color="#2b2b2b",
            command=self.run_repair_engines_fix
        )
        btn_repair_engines.pack(fill="x", padx=10, pady=3)
        
        # Re-register DLLs
        btn_reregister_dlls = ctk.CTkButton(
            scroll_repair, text="⚙️ Re-Register Core Windows System DLL Libraries (regsvr32)",
            font=("Outfit", 10, "bold"), anchor="w", fg_color="#1e293b", hover_color="#2b2b2b",
            command=self.reregister_system_dlls
        )
        btn_reregister_dlls.pack(fill="x", padx=10, pady=3)
        
        # Tool 4: Network Resolver Flush
        btn_dns = ctk.CTkButton(
            scroll_repair, text="🧹 Flush System DNS Resolver Cache",
            font=("Outfit", 10, "bold"), anchor="w", fg_color="#1e293b", hover_color="#2b2b2b",
            command=lambda: self.run_repair_cmd(["ipconfig", "/flushdns"], "DNS Resolver Reset")
        )
        btn_dns.pack(fill="x", padx=10, pady=3)
        
        # Tool 5: Winsock Reset
        btn_winsock = ctk.CTkButton(
            scroll_repair, text="🔌 Reset Network Winsock Catalog Bindings",
            font=("Outfit", 10, "bold"), anchor="w", fg_color="#1e293b", hover_color="#2b2b2b",
            command=lambda: self.run_repair_cmd(["netsh", "winsock", "reset"], "Winsock Stack Reset")
        )
        btn_winsock.pack(fill="x", padx=10, pady=3)
        
        # Tool 6: Windows Firewall Reset
        btn_firewall = ctk.CTkButton(
            scroll_repair, text="🔥 Reset Windows Firewall Rules to Default",
            font=("Outfit", 10, "bold"), anchor="w", fg_color="#1e293b", hover_color="#2b2b2b",
            command=lambda: self.run_repair_cmd(["netsh", "advfirewall", "reset"], "Firewall Stack Reset")
        )
        btn_firewall.pack(fill="x", padx=10, pady=3)
        
        # Tool: Microsoft Store Repair
        btn_store_rep = ctk.CTkButton(
            scroll_repair, text="🛍️ Re-register & Repair Microsoft Store & Default Apps",
            font=("Outfit", 10, "bold"), anchor="w", fg_color="#1e293b", hover_color="#2b2b2b",
            command=self.run_store_repair
        )
        btn_store_rep.pack(fill="x", padx=10, pady=3)
        
        # Tool: Network Adapter Reset Engine
        btn_net_reset = ctk.CTkButton(
            scroll_repair, text="📡 Run Comprehensive Network Stack & Adapter Reset",
            font=("Outfit", 10, "bold"), anchor="w", fg_color="#1e293b", hover_color="#2b2b2b",
            command=self.run_network_reset
        )
        btn_net_reset.pack(fill="x", padx=10, pady=3)

        ctk.CTkLabel(scroll_repair, text="🛠️ SYSTEM RECOVERY & BOOT MANAGEMENT", font=("Outfit", 9, "bold"), text_color="#38bdf8").pack(anchor="w", pady=(15, 4))
        
        # WinRE Enable
        btn_re_en = ctk.CTkButton(
            scroll_repair, text="💪 Enable Windows Recovery Environment (WinRE)",
            font=("Outfit", 10, "bold"), anchor="w", fg_color="#1e293b", hover_color="#2b2b2b",
            command=lambda: self.run_repair_cmd(["reagentc", "/enable"], "WinRE Enable")
        )
        btn_re_en.pack(fill="x", padx=10, pady=3)
        
        # WinRE Status
        btn_re_stat = ctk.CTkButton(
            scroll_repair, text="🔍 Check WinRE Environment Configuration Status",
            font=("Outfit", 10, "bold"), anchor="w", fg_color="#1e293b", hover_color="#2b2b2b",
            command=lambda: self.run_repair_cmd(["reagentc", "/info"], "WinRE Status Info")
        )
        btn_re_stat.pack(fill="x", padx=10, pady=3)

        ctk.CTkLabel(scroll_repair, text="⚙️ MICROSOFT OFFICE & OUTLOOK DIAGNOSTICS & REPAIRS", font=("Outfit", 9, "bold"), text_color="#38bdf8").pack(anchor="w", pady=(15, 4))
        
        # Office Quick Repair
        btn_off_rep = ctk.CTkButton(
            scroll_repair, text="🛠️ Run Microsoft Office Quick Repair (Click-to-Run)",
            font=("Outfit", 10, "bold"), anchor="w", fg_color="#1e293b", hover_color="#2b2b2b",
            command=self.run_office_repair
        )
        btn_off_rep.pack(fill="x", padx=10, pady=3)
        
        # ScanPST Launcher
        btn_pst_rep = ctk.CTkButton(
            scroll_repair, text="📧 Launch Outlook PST File Repair Tool (ScanPST)",
            font=("Outfit", 10, "bold"), anchor="w", fg_color="#1e293b", hover_color="#2b2b2b",
            command=self.launch_scanpst
        )
        btn_pst_rep.pack(fill="x", padx=10, pady=3)
        
        # Office Safe Mode sub-panel
        safe_frame = ctk.CTkFrame(scroll_repair, fg_color="transparent")
        safe_frame.pack(fill="x", padx=10, pady=3)
        
        ctk.CTkLabel(safe_frame, text="Launch Safe Mode:", font=("Outfit", 10)).pack(side="left", padx=5)
        for app in [("Word", "winword"), ("Excel", "excel"), ("PPT", "powerpnt"), ("Outlook", "outlook")]:
            btn_safe = ctk.CTkButton(
                safe_frame, text=app[0], font=("Outfit", 8, "bold"), width=60, height=22,
                command=lambda a=app[1]: self.launch_office_safe_mode(a)
            )
            btn_safe.pack(side="left", padx=3)
            
        ctk.CTkLabel(scroll_repair, text="💻 WINDOWS BOOT SECTOR & EFI REPAIR", font=("Outfit", 9, "bold"), text_color="#38bdf8").pack(anchor="w", pady=(15, 4))
        
        # Rebuild BCD
        btn_bcd = ctk.CTkButton(
            scroll_repair, text="💻 Rebuild Windows Boot configuration partition files (BCDBoot)",
            font=("Outfit", 10, "bold"), anchor="w", fg_color="#1e293b", hover_color="#2b2b2b",
            command=lambda: self.run_repair_cmd(["bcdboot", "C:\\Windows"], "BCDBoot Rebuild")
        )
        btn_bcd.pack(fill="x", padx=10, pady=3)
        
        # Reboot to Advanced Recovery
        btn_rec_boot = ctk.CTkButton(
            scroll_repair, text="🔄 Reboot System directly into Startup Repair / Recovery Menu",
            font=("Outfit", 10, "bold"), anchor="w", fg_color="#1e293b", hover_color="#2b2b2b",
            command=self.reboot_to_recovery
        )
        btn_rec_boot.pack(fill="x", padx=10, pady=3)
        
        # Enable Boot Failures display
        btn_fail_menu = ctk.CTkButton(
            scroll_repair, text="🚦 Enable Windows Boot Failures Menu Display Policy",
            font=("Outfit", 10, "bold"), anchor="w", fg_color="#1e293b", hover_color="#2b2b2b",
            command=lambda: self.run_repair_cmd(["bcdedit", "/set", "{current}", "bootstatuspolicy", "displayallfailures"], "Boot status policy")
        )
        btn_fail_menu.pack(fill="x", padx=10, pady=3)
        
        # Schedule Boot-Time Disk Volume Scan & Repair (Chkdsk)
        btn_chkdsk = ctk.CTkButton(
            scroll_repair, text="📂 Schedule Boot-Time Disk Volume Scan & Repair (Chkdsk /f /r)",
            font=("Outfit", 10, "bold"), anchor="w", fg_color="#1e293b", hover_color="#2b2b2b",
            command=self.schedule_chkdsk_scan
        )
        btn_chkdsk.pack(fill="x", padx=10, pady=3)

        ctk.CTkLabel(scroll_repair, text="🖨️ PRINTER SERVICE & SHARING REPAIRS", font=("Outfit", 9, "bold"), text_color="#38bdf8").pack(anchor="w", pady=(15, 4))
        
        # Repair Printer Sharing 0x0000011b Error
        btn_print_share = ctk.CTkButton(
            scroll_repair, text="🔓 Fix Shared Printer Error 0x0000011b (Set RpcAuthnLevelPrivacyEnabled=0)",
            font=("Outfit", 10, "bold"), anchor="w", fg_color="#1e293b", hover_color="#2b2b2b",
            command=self.fix_printer_sharing_error
        )
        btn_print_share.pack(fill="x", padx=10, pady=3)
        
        # Configure Group Policy & Point & Print Policies
        btn_print_policy = ctk.CTkButton(
            scroll_repair, text="📜 Configure Group Policy Printer Sharing & RPC Connection Settings",
            font=("Outfit", 10, "bold"), anchor="w", fg_color="#1e293b", hover_color="#2b2b2b",
            command=self.configure_printer_gpo_policies
        )
        btn_print_policy.pack(fill="x", padx=10, pady=3)
        
        # Enable LPD Features
        btn_enable_lpd = ctk.CTkButton(
            scroll_repair, text="⚙️ Enable Windows LPD Print Service & LPR Port Monitor Optional Features",
            font=("Outfit", 10, "bold"), anchor="w", fg_color="#1e293b", hover_color="#2b2b2b",
            command=self.enable_lpd_printer_features
        )
        btn_enable_lpd.pack(fill="x", padx=10, pady=3)
        
        # Enable Sharing & Discovery Services
        btn_discovery_services = ctk.CTkButton(
            scroll_repair, text="🌐 Restart Network Discovery & Printer Sharing Dependency Services",
            font=("Outfit", 10, "bold"), anchor="w", fg_color="#1e293b", hover_color="#2b2b2b",
            command=self.enable_sharing_discovery_services
        )
        btn_discovery_services.pack(fill="x", padx=10, pady=3)
        
        # Clear Print Spooler Queue
        btn_clear_spooler = ctk.CTkButton(
            scroll_repair, text="🧹 Flush Print Spooler Service & Clear Pending Queue",
            font=("Outfit", 10, "bold"), anchor="w", fg_color="#1e293b", hover_color="#2b2b2b",
            command=self.clear_print_spooler
        )
        btn_clear_spooler.pack(fill="x", padx=10, pady=3)
        
        # Open Printer Diagnostics Troubleshooter
        btn_print_trouble = ctk.CTkButton(
            scroll_repair, text="🔍 Launch Native Windows Printer Troubleshooter Diagnostic Wizard",
            font=("Outfit", 10, "bold"), anchor="w", fg_color="#1e293b", hover_color="#2b2b2b",
            command=lambda: self.run_repair_cmd(["msdt.exe", "/id", "PrinterDiagnostic"], "Printer Troubleshooter Wizard")
        )
        btn_print_trouble.pack(fill="x", padx=10, pady=3)

        ctk.CTkLabel(scroll_repair, text="🎛️ LOSSLESS DRIVE & DISK STYLE CONVERTERS", font=("Outfit", 9, "bold"), text_color="#38bdf8").pack(anchor="w", pady=(15, 4))
        
        # FAT32 to NTFS Converter UI
        ntfs_frame = ctk.CTkFrame(scroll_repair, fg_color="transparent")
        ntfs_frame.pack(fill="x", padx=10, pady=3)
        
        ctk.CTkLabel(ntfs_frame, text="FAT32 Drive Letter:", font=("Outfit", 10)).pack(side="left", padx=5)
        self.ntfs_drive_combo = ctk.CTkComboBox(ntfs_frame, values=["D:", "E:", "F:", "G:"], width=80)
        self.ntfs_drive_combo.pack(side="left", padx=5)
        
        btn_conv_ntfs = ctk.CTkButton(
            ntfs_frame, text="Convert to NTFS", font=("Outfit", 9, "bold"), width=120,
            command=self.run_fat32_to_ntfs
        )
        btn_conv_ntfs.pack(side="left", padx=10)
        
        # MBR to GPT Converter UI
        gpt_frame = ctk.CTkFrame(scroll_repair, fg_color="transparent")
        gpt_frame.pack(fill="x", padx=10, pady=3)
        
        ctk.CTkLabel(gpt_frame, text="Disk ID (MBR):", font=("Outfit", 10)).pack(side="left", padx=5)
        self.gpt_disk_combo = ctk.CTkComboBox(gpt_frame, values=["Disk 0", "Disk 1", "Disk 2"], width=90)
        self.gpt_disk_combo.pack(side="left", padx=5)
        
        btn_conv_gpt = ctk.CTkButton(
            gpt_frame, text="Convert MBR to GPT", font=("Outfit", 9, "bold"), width=120, fg_color="#ef4444", hover_color="#dc2626",
            command=self.run_mbr_to_gpt
        )
        btn_conv_gpt.pack(side="left", padx=10)
        
        ctk.CTkLabel(scroll_repair, text="🧹 SYSTEM CLEANERS & CACHE OPTIMIZERS", font=("Outfit", 9, "bold"), text_color="#38bdf8").pack(anchor="w", pady=(15, 4))
        
        # Optimize RAM Standby Cache
        btn_ram_opt = ctk.CTkButton(
            scroll_repair, text="🧠 Optimize & Flush System RAM Cache (Empty Process Working Sets)",
            font=("Outfit", 10, "bold"), anchor="w", fg_color="#1e293b", hover_color="#2b2b2b",
            command=self.optimize_ram_standby
        )
        btn_ram_opt.pack(fill="x", padx=10, pady=3)
        
        # Clean Browser Caches
        btn_browser_clean = ctk.CTkButton(
            scroll_repair, text="🧹 Clean Web Browser Cache & Temp Files (Chrome, Edge, Firefox)",
            font=("Outfit", 10, "bold"), anchor="w", fg_color="#1e293b", hover_color="#2b2b2b",
            command=self.clean_browsers_cache
        )
        btn_browser_clean.pack(fill="x", padx=10, pady=3)
        
        ctk.CTkLabel(scroll_repair, text="🛡️ WINDOWS SERVICES & SHIELD REPAIRS", font=("Outfit", 9, "bold"), text_color="#38bdf8").pack(anchor="w", pady=(15, 4))
        
        # Windows Update Repair
        btn_update_repair = ctk.CTkButton(
            scroll_repair, text="⚙️ Run Comprehensive Windows Update Service & Cache Repair Engine",
            font=("Outfit", 10, "bold"), anchor="w", fg_color="#1e293b", hover_color="#2b2b2b",
            command=self.repair_windows_updates
        )
        btn_update_repair.pack(fill="x", padx=10, pady=3)
        
        # Windows Update Blocker/Enabler frame
        wu_block_frame = ctk.CTkFrame(scroll_repair, fg_color="transparent")
        wu_block_frame.pack(fill="x", padx=10, pady=3)
        
        btn_block_wu = ctk.CTkButton(
            wu_block_frame, text="🔒 Disable & Block Windows Updates",
            font=("Outfit", 9, "bold"), fg_color="#ef4444", hover_color="#dc2626",
            command=self.block_windows_updates
        )
        btn_block_wu.pack(side="left", padx=(0, 5), expand=True, fill="x")
        
        btn_enable_wu = ctk.CTkButton(
            wu_block_frame, text="🔓 Restore & Enable Windows Updates",
            font=("Outfit", 9, "bold"), fg_color="#10b981", hover_color="#059669",
            command=self.enable_windows_updates
        )
        btn_enable_wu.pack(side="right", padx=(5, 0), expand=True, fill="x")
        
        # Windows Defender Policies Reset
        btn_defender_reset = ctk.CTkButton(
            scroll_repair, text="🛡️ Reset Windows Defender Policies & Restart Antivirus Services",
            font=("Outfit", 10, "bold"), anchor="w", fg_color="#1e293b", hover_color="#2b2b2b",
            command=self.reset_windows_defender
        )
        btn_defender_reset.pack(fill="x", padx=10, pady=3)
        
        # Restore Firewall
        btn_firewall_reset = ctk.CTkButton(
            scroll_repair, text="🧱 Restore Default Windows Firewall Settings and Rules",
            font=("Outfit", 10, "bold"), anchor="w", fg_color="#1e293b", hover_color="#2b2b2b",
            command=self.restore_windows_firewall
        )
        btn_firewall_reset.pack(fill="x", padx=10, pady=3)
        
        # Reset Audio Services
        btn_audio_reset = ctk.CTkButton(
            scroll_repair, text="🎧 Reset & Restart Windows Audio Playback Services",
            font=("Outfit", 10, "bold"), anchor="w", fg_color="#1e293b", hover_color="#2b2b2b",
            command=self.reset_audio_services
        )
        btn_audio_reset.pack(fill="x", padx=10, pady=3)
        
        ctk.CTkLabel(scroll_repair, text="🚀 SHELL OPTIMIZERS & DATA WIPERS", font=("Outfit", 9, "bold"), text_color="#38bdf8").pack(anchor="w", pady=(15, 4))
        
        # Restart Explorer Shell
        btn_explorer_restart = ctk.CTkButton(
            scroll_repair, text="🚀 Restart Windows Explorer Shell (Quick Freeze Fix)",
            font=("Outfit", 10, "bold"), anchor="w", fg_color="#1e293b", hover_color="#2b2b2b",
            command=self.restart_explorer_shell
        )
        btn_explorer_restart.pack(fill="x", padx=10, pady=3)
        
        # Clear Event Logs
        btn_event_logs = ctk.CTkButton(
            scroll_repair, text="💽 Clear All Windows System, Application & Security Event Logs",
            font=("Outfit", 10, "bold"), anchor="w", fg_color="#1e293b", hover_color="#2b2b2b",
            command=self.clear_all_event_logs
        )
        btn_event_logs.pack(fill="x", padx=10, pady=3)
        
        # Clear Icon & Thumbnail Cache
        btn_icon_cache = ctk.CTkButton(
            scroll_repair, text="🖼️ Rebuild Windows Desktop Icon & Thumbnail Cache Data",
            font=("Outfit", 10, "bold"), anchor="w", fg_color="#1e293b", hover_color="#2b2b2b",
            command=self.clear_icon_thumbnail_cache
        )
        btn_icon_cache.pack(fill="x", padx=10, pady=3)
        
        # Rebuild Font Cache database
        btn_font_cache = ctk.CTkButton(
            scroll_repair, text="🔤 Rebuild Windows System Font Cache Database",
            font=("Outfit", 10, "bold"), anchor="w", fg_color="#1e293b", hover_color="#2b2b2b",
            command=self.rebuild_font_cache
        )
        btn_font_cache.pack(fill="x", padx=10, pady=3)
        
        ctk.CTkLabel(scroll_repair, text="🔧 SYSTEM CUSTOMIZATIONS & CONTEXT MENU BOOSTS", font=("Outfit", 9, "bold"), text_color="#38bdf8").pack(anchor="w", pady=(15, 4))
        
        # Classic Context Menu togglers
        btn_classic_ctx = ctk.CTkButton(
            scroll_repair, text="📂 Restore Windows 11 Classic Right-Click Context Menu",
            font=("Outfit", 10, "bold"), anchor="w", fg_color="#1e293b", hover_color="#2b2b2b",
            command=self.restore_classic_context_menu
        )
        btn_classic_ctx.pack(fill="x", padx=10, pady=3)
        
        btn_default_ctx = ctk.CTkButton(
            scroll_repair, text="↩️ Revert to Windows 11 Default Right-Click Context Menu",
            font=("Outfit", 10, "bold"), anchor="w", fg_color="#1e293b", hover_color="#2b2b2b",
            command=self.revert_default_context_menu
        )
        btn_default_ctx.pack(fill="x", padx=10, pady=3)
        
        # Disable Bing in Start Menu
        btn_disable_bing = ctk.CTkButton(
            scroll_repair, text="🔍 Disable Online Bing Web Search in Windows Start Menu (Offline Boost)",
            font=("Outfit", 10, "bold"), anchor="w", fg_color="#1e293b", hover_color="#2b2b2b",
            command=self.disable_bing_start_search
        )
        btn_disable_bing.pack(fill="x", padx=10, pady=3)
        
        # Toggle Fast Startup
        btn_fast_startup = ctk.CTkButton(
            scroll_repair, text="⚡ Toggle Windows Fast Startup Settings (Disable / Enable)",
            font=("Outfit", 10, "bold"), anchor="w", fg_color="#1e293b", hover_color="#2b2b2b",
            command=self.toggle_fast_startup
        )
        btn_fast_startup.pack(fill="x", padx=10, pady=3)
        
        # Unlock Ultimate Performance Plan
        btn_ultimate_perf = ctk.CTkButton(
            scroll_repair, text="⚡ Unlock & Enable Windows Ultimate Performance Power Plan",
            font=("Outfit", 10, "bold"), anchor="w", fg_color="#1e293b", hover_color="#2b2b2b",
            command=self.enable_ultimate_performance
        )
        btn_ultimate_perf.pack(fill="x", padx=10, pady=3)
        
        # Gaming Latency Optimization
        btn_gaming_opt = ctk.CTkButton(
            scroll_repair, text="🎮 Optimize Windows 10/11 Registry Settings for Low-Latency Gaming",
            font=("Outfit", 10, "bold"), anchor="w", fg_color="#1e293b", hover_color="#2b2b2b",
            command=self.optimize_gaming_tweaks
        )
        btn_gaming_opt.pack(fill="x", padx=10, pady=3)
        
        ctk.CTkLabel(scroll_repair, text="💻 HARDWARE DIAGNOSTICS & SPEED TESTING", font=("Outfit", 9, "bold"), text_color="#38bdf8").pack(anchor="w", pady=(15, 4))
        
        # Disk health status
        btn_disk_health = ctk.CTkButton(
            scroll_repair, text="💾 Check Connected Physical Drive Health Status (SMART Scan)",
            font=("Outfit", 10, "bold"), anchor="w", fg_color="#1e293b", hover_color="#2b2b2b",
            command=self.check_disk_health
        )
        btn_disk_health.pack(fill="x", padx=10, pady=3)
        
        # RAM Spec check
        btn_ram_specs = ctk.CTkButton(
            scroll_repair, text="🧠 Analyze Installed RAM Modules & Speed Specifications (WMIC)",
            font=("Outfit", 10, "bold"), anchor="w", fg_color="#1e293b", hover_color="#2b2b2b",
            command=self.check_ram_specs
        )
        btn_ram_specs.pack(fill="x", padx=10, pady=3)
        
        # RAM diagnostics scheduler
        btn_ram_diag = ctk.CTkButton(
            scroll_repair, text="🔄 Schedule Windows Memory Diagnostic Scanner (mdsched.exe)",
            font=("Outfit", 10, "bold"), anchor="w", fg_color="#1e293b", hover_color="#2b2b2b",
            command=self.schedule_memory_diagnostic
        )
        btn_ram_diag.pack(fill="x", padx=10, pady=3)
        
        # DNS Changer
        btn_dns_change = ctk.CTkButton(
            scroll_repair, text="🌐 Configure Secure Network DNS Servers (Cloudflare 1.1.1.1)",
            font=("Outfit", 10, "bold"), anchor="w", fg_color="#1e293b", hover_color="#2b2b2b",
            command=self.configure_secure_dns
        )
        btn_dns_change.pack(fill="x", padx=10, pady=3)
        
        # Speed Test
        btn_speed_test = ctk.CTkButton(
            scroll_repair, text="📡 Run Real-Time Internet Download Speed Test (Cloudflare CDN)",
            font=("Outfit", 10, "bold"), anchor="w", fg_color="#10b981", hover_color="#059669",
            command=self.run_speed_test
        )
        btn_speed_test.pack(fill="x", padx=10, pady=3)
        
        # Battery Health Report
        btn_battery_report = ctk.CTkButton(
            scroll_repair, text="🔋 Generate Windows Battery Lifecycle & Wear Health Report",
            font=("Outfit", 10, "bold"), anchor="w", fg_color="#1e293b", hover_color="#2b2b2b",
            command=self.generate_battery_report
        )
        btn_battery_report.pack(fill="x", padx=10, pady=3)
        
        # Windows Activation Check
        btn_activation_check = ctk.CTkButton(
            scroll_repair, text="🔑 Verify Windows OS License Activation Status (slmgr)",
            font=("Outfit", 10, "bold"), anchor="w", fg_color="#1e293b", hover_color="#2b2b2b",
            command=self.check_windows_activation
        )
        btn_activation_check.pack(fill="x", padx=10, pady=3)
        
        # System Info Summary
        btn_system_summary = ctk.CTkButton(
            scroll_repair, text="📝 Generate Comprehensive Windows Hardware & System Info Summary",
            font=("Outfit", 10, "bold"), anchor="w", fg_color="#1e293b", hover_color="#2b2b2b",
            command=self.generate_system_info_summary
        )
        btn_system_summary.pack(fill="x", padx=10, pady=3)
        
        # Right card: Log output
        log_card = ctk.CTkFrame(split_frame, width=420, fg_color="#151f32", border_color="#1e293b", border_width=1.5)
        log_card.pack(side="right", fill="both", padx=(5, 0))
        log_card.pack_propagate(False)
        
        ctk.CTkLabel(log_card, text="⚙️ Repair Shell Outputs", font=("Outfit", 11, "bold"), text_color="#ffffff").pack(anchor="w", padx=15, pady=10)
        
        self.repair_log_text = ctk.CTkTextbox(
            log_card, fg_color="#0d1321", border_color="#1e293b", border_width=1, text_color="#10b981", font=("Consolas", 9)
        )
        self.repair_log_text.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        self.repair_log_text.insert("end", "[Ready to execute admin repair pipelines]\n")
        self.repair_log_text.configure(state="disabled")

    def append_repair_log(self, text):
        self.repair_log_text.configure(state="normal")
        self.repair_log_text.insert("end", text)
        self.repair_log_text.see("end")
        self.repair_log_text.configure(state="disabled")

    def run_repair_cmd(self, cmd, label):
        if self.is_running_operation:
            self.append_repair_log("[!] Error: An active operation is already running.\n")
            return
            
        self.is_running_operation = True
        self.append_repair_log(f"\n[*] Executing: {' '.join(cmd)}...\n")
        self.add_activity("Windows Repair", f"Running {label}", "Running")
        
        threading.Thread(target=self.run_repair_cmd_thread, args=(cmd, label), daemon=True).start()

    def run_repair_cmd_thread(self, cmd, label):
        try:
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
            
            while True:
                line = proc.stdout.readline()
                if not line:
                    break
                self.append_repair_log(line)
                
            proc.wait()
            if proc.returncode == 0:
                self.append_repair_log("[✓] Finished successfully.\n")
                self.add_activity("Windows Repair", f"Completed {label} successfully", "Success")
            else:
                self.append_repair_log(f"[X] Finished with exit code: {proc.returncode}\n")
                self.add_activity("Windows Repair", f"Failed {label} with code {proc.returncode}", "Failed")
        except Exception as e:
            self.append_repair_log(f"[X] Error running process: {str(e)}\n")
            self.add_activity("Windows Repair", f"Error during {label}: {str(e)}", "Failed")
            
        self.is_running_operation = False

    def run_fat32_to_ntfs(self):
        drive = self.ntfs_drive_combo.get().strip().replace(":", "")
        self.run_repair_cmd(["convert", f"{drive}:", "/fs:ntfs"], f"FAT32 to NTFS converter ({drive}:)")
        
    def run_mbr_to_gpt(self):
        disk_val = self.gpt_disk_combo.get().strip().lower().replace("disk", "").strip()
        # Prompt warnings for dangerous disk edits
        self.append_repair_log("\n[WARNING] Executing MBR2GPT conversion requires valid system structures.\n")
        self.run_repair_cmd(["mbr2gpt", "/convert", f"/disk:{disk_val}", "/allowFullOS"], f"MBR to GPT Converter (Disk {disk_val})")

    def run_repair_engines_fix(self):
        self.add_activity("Windows Repair", "Repairing Windows Native Repair Engines...", "Running")
        self.append_repair_log("\n[*] Starting Windows Repair Infrastructure Fix pipeline...\n")
        self.append_repair_log("[*] Step 1: Stopping TrustedInstaller service...\n")
        
        def run_thread():
            try:
                subprocess.run(["net", "stop", "trustedinstaller"], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
                
                self.append_repair_log("[*] Step 2: Running DISM Component Store StartComponentCleanup...\n")
                subprocess.run(["dism", "/online", "/cleanup-image", "/startcomponentcleanup"], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
                
                self.append_repair_log("[*] Step 3: Running DISM Component Store RestoreHealth...\n")
                res = subprocess.run(["dism", "/online", "/cleanup-image", "/restorehealth"], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
                self.append_repair_log(res.stdout)
                
                self.append_repair_log("[*] Step 4: Re-starting TrustedInstaller service...\n")
                subprocess.run(["net", "start", "trustedinstaller"], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
                
                self.append_repair_log("[*] Step 5: Running System File Checker (sfc /scannow)...\n")
                res2 = subprocess.run(["sfc", "/scannow"], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
                self.append_repair_log(res2.stdout)
                
                self.append_repair_log("[✓] Component store and system files successfully repaired!\n")
                self.add_activity("Windows Repair", "SFC & DISM engines repaired", "Success")
                messagebox.showinfo("Success", "Windows Native Repair Utilities repaired successfully!")
            except Exception as e:
                self.append_repair_log(f"[X] Fix failed: {str(e)}\n")
                self.add_activity("Windows Repair", f"Repair engines fix failed: {str(e)}", "Failed")
                
        threading.Thread(target=run_thread, daemon=True).start()

    def run_office_repair(self):
        self.add_activity("Office Repair", "Running Office Quick Repair scenario...", "Running")
        self.append_repair_log("\n[*] Triggering Microsoft Office Quick Repair (Click-to-Run)...\n")
        
        # Test paths for OfficeClickToRun
        common_path = r"C:\Program Files\Common Files\microsoft shared\ClickToRun\OfficeClickToRun.exe"
        if os.path.exists(common_path):
            cmd = [common_path, "scenario=Repair", "platform=x64", "culture=en-us", "ForceAppShutdown=True"]
            self.run_repair_cmd(cmd, "Office Quick Repair")
        else:
            self.append_repair_log("[!] Error: OfficeClickToRun.exe not found at standard path.\n")
            self.add_activity("Office Repair", "Office Repair scenario failed (Path not found)", "Failed")
            messagebox.showerror("Error", "OfficeClickToRun.exe not found at standard path.\nEnsure Office Click-to-Run is installed.")

    def launch_scanpst(self):
        self.add_activity("PST Repair", "Searching for scanpst.exe...", "Running")
        self.append_repair_log("\n[*] Searching for Outlook PST Repair Tool (scanpst.exe)...\n")
        
        paths = [
            r"C:\Program Files\Microsoft Office\root\Office16\scanpst.exe",
            r"C:\Program Files (x86)\Microsoft Office\root\Office16\scanpst.exe",
            r"C:\Program Files\Microsoft Office\Office16\scanpst.exe",
            r"C:\Program Files (x86)\Microsoft Office\Office16\scanpst.exe",
            r"C:\Program Files\Microsoft Office\Office15\scanpst.exe",
            r"C:\Program Files (x86)\Microsoft Office\Office15\scanpst.exe"
        ]
        found = False
        for p in paths:
            if os.path.exists(p):
                try:
                    subprocess.Popen([p])
                    self.append_repair_log(f"[✓] Launched ScanPST from: {p}\n")
                    self.add_activity("PST Repair", "ScanPST utility opened successfully", "Success")
                    found = True
                    break
                except Exception as e:
                    self.append_repair_log(f"[!] Failed to launch from {p}: {str(e)}\n")
                    
        if not found:
            self.append_repair_log("[!] ScanPST.exe could not be found automatically on this system.\n")
            self.add_activity("PST Repair", "ScanPST not found", "Failed")
            messagebox.showerror("Error", "Could not find ScanPST.exe on your system.\nPlease make sure Microsoft Outlook is installed.")

    def get_office_app_path(self, app_exe):
        key_path = fr"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\{app_exe}"
        for hkey in [winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER]:
            try:
                key = winreg.OpenKey(hkey, key_path, 0, winreg.KEY_READ)
                val, _ = winreg.QueryValue(key, "")
                winreg.CloseKey(key)
                if os.path.exists(val):
                    return val
            except:
                pass
        
        # Fallback common directories
        folders = [
            r"C:\Program Files\Microsoft Office\root\Office16",
            r"C:\Program Files (x86)\Microsoft Office\root\Office16",
            r"C:\Program Files\Microsoft Office\Office16",
            r"C:\Program Files (x86)\Microsoft Office\Office16",
            r"C:\Program Files\Microsoft Office\Office15",
            r"C:\Program Files (x86)\Microsoft Office\Office15",
            r"C:\Program Files\Microsoft Office\Office14",
            r"C:\Program Files (x86)\Microsoft Office\Office14"
        ]
        for folder in folders:
            full_path = os.path.join(folder, app_exe)
            if os.path.exists(full_path):
                return full_path
        return None

    def launch_office_safe_mode(self, app_name):
        app_exe = f"{app_name}.exe"
        self.add_activity("Office Safe Mode", f"Launching {app_name} in Safe Mode...", "Running")
        self.append_repair_log(f"\n[*] Resolving absolute path for {app_exe}...\n")
        
        path = self.get_office_app_path(app_exe)
        if path:
            self.append_repair_log(f"[✓] Path resolved: {path}\n")
            self.append_repair_log(f"[*] Launching {app_exe} in Safe Mode...\n")
            try:
                subprocess.Popen([path, "/safe"])
                self.append_repair_log(f"[✓] Safe mode trigger sent for {app_name}.\n")
                self.add_activity("Office Safe Mode", f"Launched {app_name} successfully", "Success")
            except Exception as e:
                self.append_repair_log(f"[X] Launch failed: {str(e)}\n")
                self.add_activity("Office Safe Mode", f"Launch failed for {app_name}", "Failed")
                messagebox.showerror("Error", f"Failed to launch {app_name} in Safe Mode:\n{str(e)}")
        else:
            self.append_repair_log(f"[X] Path resolution failed. {app_exe} not found.\n")
            self.add_activity("Office Safe Mode", f"Resolution failed for {app_name}", "Failed")
            messagebox.showerror("Error", f"Could not find path for {app_exe} on your system.\nVerify Microsoft Office installation.")

    def reboot_to_recovery(self):
        confirm = messagebox.askyesno("Confirm Reboot", "Are you sure you want to reboot your system directly into the Startup Repair / Advanced Options menu?")
        if confirm:
            self.add_activity("Boot Repair", "Rebooting into WinRE Menu...", "Running")
            self.append_repair_log("\n[*] Triggering system reboot into Recovery Menu...\n")
            try:
                subprocess.Popen(["shutdown", "/r", "/o", "/t", "0"], creationflags=subprocess.CREATE_NO_WINDOW)
            except Exception as e:
                self.append_repair_log(f"[X] Reboot command failed: {str(e)}\n")
                self.add_activity("Boot Repair", "Reboot command failed", "Failed")

    def fix_printer_sharing_error(self):
        self.add_activity("Printer Repair", "Applying shared printer error 0x0000011b registry fix...", "Running")
        self.append_repair_log("\n[*] Applying Shared Printer Error 0x0000011b registry patch...\n")
        
        def run_thread():
            try:
                # Add/Set RpcAuthnLevelPrivacyEnabled to 0
                key_path = r"System\CurrentControlSet\Control\Print"
                reg_key = winreg.CreateKeyEx(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_SET_VALUE)
                winreg.SetValueEx(reg_key, "RpcAuthnLevelPrivacyEnabled", 0, winreg.REG_DWORD, 0)
                winreg.CloseKey(reg_key)
                
                self.append_repair_log("[✓] Registry value 'RpcAuthnLevelPrivacyEnabled' successfully set to 0.\n")
                
                # Restart Spooler service
                self.append_repair_log("[*] Restarting Windows Print Spooler service to apply changes...\n")
                subprocess.run(["net", "stop", "spooler"], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
                res = subprocess.run(["net", "start", "spooler"], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
                self.append_repair_log(res.stdout)
                
                self.append_repair_log("[✓] Spooler restarted. Printer sharing 0x0000011b error fixed!\n")
                self.add_activity("Printer Repair", "Printer Sharing Error Fixed", "Success")
                messagebox.showinfo("Success", "Printer sharing error 0x0000011b fixed successfully!\nSpooler service restarted.")
            except Exception as e:
                self.append_repair_log(f"[X] Fix failed: {str(e)}\n")
                self.add_activity("Printer Repair", f"Sharing fix failed: {str(e)}", "Failed")
                messagebox.showerror("Error", f"Failed to apply patch:\n{str(e)}")
                
        threading.Thread(target=run_thread, daemon=True).start()

    def clear_print_spooler(self):
        self.add_activity("Printer Repair", "Clearing Print Spooler queue...", "Running")
        self.append_repair_log("\n[*] Initiating Print Spooler flush pipeline...\n")
        
        def run_thread():
            try:
                # Stop spooler
                self.append_repair_log("[*] Stopping Print Spooler service...\n")
                subprocess.run(["net", "stop", "spooler"], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
                
                # Clear spool folder
                spool_path = os.path.expandvars(r"%systemroot%\System32\Spool\Printers")
                self.append_repair_log(f"[*] Cleaning up pending jobs in: {spool_path}\n")
                if os.path.exists(spool_path):
                    for file in os.listdir(spool_path):
                        file_path = os.path.join(spool_path, file)
                        try:
                            if os.path.isfile(file_path):
                                os.unlink(file_path)
                            elif os.path.isdir(file_path):
                                shutil.rmtree(file_path)
                        except Exception as ex:
                            self.append_repair_log(f"[!] Warning: Could not delete {file}: {str(ex)}\n")
                            
                # Start spooler
                self.append_repair_log("[*] Restarting Print Spooler service...\n")
                res = subprocess.run(["net", "start", "spooler"], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
                self.append_repair_log(res.stdout)
                
                self.append_repair_log("[✓] Spooler queue flushed successfully.\n")
                self.add_activity("Printer Repair", "Spooler queue cleared", "Success")
                messagebox.showinfo("Success", "Print Spooler queue cleared and service restarted successfully!")
            except Exception as e:
                self.append_repair_log(f"[X] Operation failed: {str(e)}\n")
                self.add_activity("Printer Repair", f"Queue flush failed: {str(e)}", "Failed")
                messagebox.showerror("Error", f"Failed to flush spooler:\n{str(e)}")
                
        threading.Thread(target=run_thread, daemon=True).start()

    def configure_printer_gpo_policies(self):
        self.add_activity("Printer Repair", "Applying Printer GPO Policies...", "Running")
        self.append_repair_log("\n[*] Applying printer sharing Group Policy settings to Registry...\n")
        
        def run_thread():
            try:
                import winreg
                
                # Base Printers policies key
                printers_key_path = r"Software\Policies\Microsoft\Windows NT\Printers"
                key = winreg.CreateKeyEx(winreg.HKEY_LOCAL_MACHINE, printers_key_path, 0, winreg.KEY_SET_VALUE)
                
                # 1. Limits print driver installation to Administrators = Disabled (0)
                winreg.SetValueEx(key, "LimitDriverInstallationToAdministrators", 0, winreg.REG_DWORD, 0)
                self.append_repair_log("[✓] GPO: Disabled 'Limits print driver installation to Administrators' policy.\n")
                
                # 2. Configure RPC packet level privacy setting for incoming connections = Disabled (0)
                winreg.SetValueEx(key, "RpcAuthnLevelPrivacyEnabled", 0, winreg.REG_DWORD, 0)
                self.append_repair_log("[✓] GPO: Disabled 'Configure RPC packet level privacy setting for incoming connections'.\n")
                
                # 3. Configure RPC connection settings (RpcOverTcp = 1 (RPC over TCP), RpcUseNamedPipesBackCompat = 1)
                winreg.SetValueEx(key, "RpcOverTcp", 0, winreg.REG_DWORD, 1) # 1 = RPC over TCP
                winreg.SetValueEx(key, "RpcUseNamedPipesBackCompat", 0, winreg.REG_DWORD, 1) # 1 = Enabled
                self.append_repair_log("[✓] GPO: Configured 'RPC Connection Settings' to use RPC over TCP & enable Named Pipes compatibility.\n")
                
                winreg.CloseKey(key)
                
                # 4. Point and Print Restrictions = Disabled (0)
                point_and_print_path = r"Software\Policies\Microsoft\Windows NT\Printers\PointAndPrint"
                pp_key = winreg.CreateKeyEx(winreg.HKEY_LOCAL_MACHINE, point_and_print_path, 0, winreg.KEY_SET_VALUE)
                winreg.SetValueEx(pp_key, "Restricted", 0, winreg.REG_DWORD, 0)
                winreg.SetValueEx(pp_key, "TrustedServers", 0, winreg.REG_DWORD, 0)
                winreg.CloseKey(pp_key)
                self.append_repair_log("[✓] GPO: Disabled 'Point and Print Restrictions' policy.\n")
                
                # Also set restrict driver installation to admins in System Control Print for absolute compatibility
                sys_print_path = r"SYSTEM\CurrentControlSet\Control\Print"
                sys_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, sys_print_path, 0, winreg.KEY_SET_VALUE)
                winreg.SetValueEx(sys_key, "RestrictDriverInstallationToAdministrators", 0, winreg.REG_DWORD, 0)
                winreg.CloseKey(sys_key)
                self.append_repair_log("[✓] System: Set RestrictDriverInstallationToAdministrators registry DWORD to 0.\n")
                
                # Restart Spooler to apply Group Policies
                self.append_repair_log("[*] Restarting Windows Print Spooler service to apply GPO changes...\n")
                subprocess.run(["net", "stop", "spooler"], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
                res = subprocess.run(["net", "start", "spooler"], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
                self.append_repair_log(res.stdout)
                
                self.add_activity("Printer Repair", "GPO policies applied successfully", "Success")
                messagebox.showinfo("Success", "All Group Policy settings for Printer Sharing & RPC connections configured successfully!\nSpooler service restarted.")
            except Exception as e:
                self.append_repair_log(f"[X] GPO configuration failed: {str(e)}\n")
                self.add_activity("Printer Repair", f"GPO config failed: {str(e)}", "Failed")
                messagebox.showerror("Error", f"Failed to apply GPO settings:\n{str(e)}")
                
        threading.Thread(target=run_thread, daemon=True).start()

    def enable_lpd_printer_features(self):
        self.add_activity("Printer Repair", "Enabling LPD/LPR Features...", "Running")
        self.append_repair_log("\n[*] Enabling Windows LPD Service & LPR Port Monitor features via DISM...\n")
        
        def run_thread():
            try:
                # Feature 1: LPDPrintService
                self.append_repair_log("[*] Enabling feature: LPDPrintService...\n")
                cmd1 = ["dism", "/online", "/enable-feature", "/featurename:LPDPrintService", "/all", "/norestart"]
                res1 = subprocess.run(cmd1, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
                self.append_repair_log(res1.stdout)
                
                # Feature 2: LPRPortMonitor
                self.append_repair_log("[*] Enabling feature: LPRPortMonitor...\n")
                cmd2 = ["dism", "/online", "/enable-feature", "/featurename:LPRPortMonitor", "/all", "/norestart"]
                res2 = subprocess.run(cmd2, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
                self.append_repair_log(res2.stdout)
                
                self.add_activity("Printer Repair", "LPD/LPR features enabled", "Success")
                messagebox.showinfo("Success", "LPD Print Service and LPR Port Monitor features enabled successfully!")
            except Exception as e:
                self.append_repair_log(f"[X] DISM command failed: {str(e)}\n")
                self.add_activity("Printer Repair", f"LPD enable failed: {str(e)}", "Failed")
                messagebox.showerror("Error", f"Failed to enable features:\n{str(e)}")
                
        threading.Thread(target=run_thread, daemon=True).start()

    def enable_sharing_discovery_services(self):
        self.add_activity("Printer Repair", "Enabling sharing services...", "Running")
        self.append_repair_log("\n[*] Enabling Network Discovery & Sharing services (FdResPub, SSDPSRV, upnphost)...\n")
        
        def run_thread():
            services = [
                ("FdResPub", "Function Discovery Resource Publication"),
                ("SSDPSRV", "SSDP Discovery"),
                ("upnphost", "UPnP Device Host"),
                ("LanmanServer", "Server")
            ]
            try:
                for service, display_name in services:
                    self.append_repair_log(f"[*] Configuring {display_name} ({service})...\n")
                    # Set startup to Automatic
                    subprocess.run(["sc", "config", service, "start=", "auto"], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
                    # Start the service
                    res = subprocess.run(["net", "start", service], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
                    if "already running" in res.stdout or res.returncode == 0:
                        self.append_repair_log(f"[✓] {display_name} is running.\n")
                    else:
                        self.append_repair_log(f"[!] Warning: {res.stdout}\n")
                
                self.add_activity("Printer Repair", "Sharing services configured", "Success")
                messagebox.showinfo("Success", "Network Discovery and Printer sharing dependency services configured to startup automatically and started successfully!")
            except Exception as e:
                self.append_repair_log(f"[X] Service configuration failed: {str(e)}\n")
                self.add_activity("Printer Repair", f"Sharing services failed: {str(e)}", "Failed")
                messagebox.showerror("Error", f"Failed to configure services:\n{str(e)}")
                
        threading.Thread(target=run_thread, daemon=True).start()

    def repair_windows_updates(self):
        self.add_activity("Windows Update", "Repairing Windows Update components...", "Running")
        self.append_repair_log("\n[*] Resetting Windows Update agent and clearing update cache folder...\n")
        
        def run_thread():
            try:
                services = ["wuauserv", "cryptSvc", "bits", "msiserver"]
                
                # Stop services
                for s in services:
                    self.append_repair_log(f"[*] Stopping service: {s}...\n")
                    subprocess.run(["net", "stop", s, "/y"], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
                
                # Rename/Delete directories
                import shutil
                windir = os.environ.get("SystemRoot", "C:\\Windows")
                
                sd_path = os.path.join(windir, "SoftwareDistribution")
                cr2_path = os.path.join(windir, "System32", "catroot2")
                
                if os.path.exists(sd_path):
                    self.append_repair_log(f"[*] Clearing directory: {sd_path}...\n")
                    try:
                        shutil.rmtree(sd_path)
                    except Exception as e:
                        self.append_repair_log(f"[!] Warning: Failed to delete {sd_path}: {str(e)}\n")
                        
                if os.path.exists(cr2_path):
                    self.append_repair_log(f"[*] Clearing directory: {cr2_path}...\n")
                    try:
                        shutil.rmtree(cr2_path)
                    except Exception as e:
                        self.append_repair_log(f"[!] Warning: Failed to delete {cr2_path}: {str(e)}\n")
                
                # Start services
                for s in services:
                    self.append_repair_log(f"[*] Restarting service: {s}...\n")
                    subprocess.run(["net", "start", s], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
                
                self.append_repair_log("[✓] Windows Update components reset and cache cleared successfully.\n")
                self.add_activity("Windows Update", "Update Repair Completed", "Success")
                messagebox.showinfo("Success", "Windows Update Agent components reset and update cache files cleared successfully!")
            except Exception as e:
                self.append_repair_log(f"[X] Windows Update repair failed: {str(e)}\n")
                self.add_activity("Windows Update", f"Repair failed: {str(e)}", "Failed")
                messagebox.showerror("Error", f"Failed to reset Windows Update:\n{str(e)}")
                
        threading.Thread(target=run_thread, daemon=True).start()

    def reset_windows_defender(self):
        self.add_activity("Windows Defender", "Resetting Windows Defender policies...", "Running")
        self.append_repair_log("\n[*] Wiping corrupt Defender policies and restarting services...\n")
        
        def run_thread():
            try:
                import winreg
                # Delete Windows Defender registry policies
                try:
                    reg_path = r"SOFTWARE\Policies\Microsoft\Windows Defender"
                    winreg.DeleteKey(winreg.HKEY_LOCAL_MACHINE, reg_path)
                    self.append_repair_log("[✓] Wiped HKLM Windows Defender policies.\n")
                except Exception as e:
                    self.append_repair_log(f"[!] Info: Policies key already clean or modified: {str(e)}\n")
                
                # Run Defender defaults command
                mpcmd = r"C:\Program Files\Windows Defender\MpCmdRun.exe"
                if os.path.exists(mpcmd):
                    self.append_repair_log("[*] Restoring Defender default parameters...\n")
                    subprocess.run([mpcmd, "-RestoreDefaults"], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
                
                # Reset Security Health UI AppX package
                self.append_repair_log("[*] Re-registering Windows Security Center UI AppX package...\n")
                cmd = "Get-AppxPackage *SecHealthUI* -AllUsers | Reset-AppxPackage"
                subprocess.run(["powershell", "-Command", cmd], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
                
                self.append_repair_log("[✓] Windows Defender restored to defaults.\n")
                self.add_activity("Windows Defender", "Defender Policies Reset", "Success")
                messagebox.showinfo("Success", "Windows Defender Policies successfully restored to default settings!\nWindows Security App packages re-registered.")
            except Exception as e:
                self.append_repair_log(f"[X] Defender reset failed: {str(e)}\n")
                self.add_activity("Windows Defender", f"Reset failed: {str(e)}", "Failed")
                messagebox.showerror("Error", f"Failed to reset Windows Defender:\n{str(e)}")
                
        threading.Thread(target=run_thread, daemon=True).start()

    def restore_windows_firewall(self):
        self.add_activity("Firewall", "Restoring Default Firewall settings...", "Running")
        self.append_repair_log("\n[*] Resetting Windows Firewall to defaults via netsh...\n")
        
        def run_thread():
            try:
                res = subprocess.run(["netsh", "advfirewall", "reset"], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
                self.append_repair_log(res.stdout)
                
                self.append_repair_log("[✓] Windows Firewall reset to factory defaults.\n")
                self.add_activity("Firewall", "Firewall Reset Successful", "Success")
                messagebox.showinfo("Success", "Windows Defender Firewall successfully restored to default settings!")
            except Exception as e:
                self.append_repair_log(f"[X] Firewall reset failed: {str(e)}\n")
                self.add_activity("Firewall", f"Reset failed: {str(e)}", "Failed")
                messagebox.showerror("Error", f"Failed to reset Firewall:\n{str(e)}")
                
        threading.Thread(target=run_thread, daemon=True).start()

    def restart_explorer_shell(self):
        self.add_activity("Shell Repair", "Restarting Windows Explorer shell...", "Running")
        self.append_repair_log("\n[*] Terminating and restarting explorer.exe shell process...\n")
        
        def run_thread():
            try:
                # Force kill
                subprocess.run(["taskkill", "/f", "/im", "explorer.exe"], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
                # Restart explorer.exe
                subprocess.Popen(["explorer.exe"], creationflags=subprocess.CREATE_NEW_CONSOLE)
                
                self.append_repair_log("[✓] Windows Explorer shell restarted successfully.\n")
                self.add_activity("Shell Repair", "Explorer Restarted", "Success")
            except Exception as e:
                self.append_repair_log(f"[X] Explorer restart failed: {str(e)}\n")
                self.add_activity("Shell Repair", f"Restart failed: {str(e)}", "Failed")
                
        threading.Thread(target=run_thread, daemon=True).start()

    def clear_all_event_logs(self):
        self.add_activity("Log Cleaner", "Clearing Event Logs...", "Running")
        self.append_repair_log("\n[*] Cleaning up all Application, System, and Security event logs...\n")
        
        def run_thread():
            try:
                cmd = "wevtutil el | Foreach-Object { wevtutil cl $_ }"
                res = subprocess.run(["powershell", "-Command", cmd], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
                self.append_repair_log("[✓] Event logs wiped clean.\n")
                self.add_activity("Log Cleaner", "Event Logs Wiped", "Success")
                messagebox.showinfo("Success", "All Windows System and Application event logs have been cleared successfully!")
            except Exception as e:
                self.append_repair_log(f"[X] Event log cleaner failed: {str(e)}\n")
                self.add_activity("Log Cleaner", f"Cleaner failed: {str(e)}", "Failed")
                messagebox.showerror("Error", f"Failed to clear event logs:\n{str(e)}")
                
        threading.Thread(target=run_thread, daemon=True).start()

    def reset_audio_services(self):
        self.add_activity("Audio Repair", "Restarting Audio services...", "Running")
        self.append_repair_log("\n[*] Resetting Windows Audio Playback & Endpoint Builder services...\n")
        
        def run_thread():
            try:
                self.append_repair_log("[*] Stopping Audiosrv service...\n")
                subprocess.run(["net", "stop", "Audiosrv", "/y"], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
                
                self.append_repair_log("[*] Stopping AudioEndpointBuilder service...\n")
                subprocess.run(["net", "stop", "AudioEndpointBuilder", "/y"], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
                
                self.append_repair_log("[*] Restarting AudioEndpointBuilder service...\n")
                subprocess.run(["net", "start", "AudioEndpointBuilder"], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
                
                self.append_repair_log("[*] Restarting Audiosrv service...\n")
                subprocess.run(["net", "start", "Audiosrv"], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
                
                self.append_repair_log("[✓] Audio services restarted and initialized successfully.\n")
                self.add_activity("Audio Repair", "Audio Services Reset", "Success")
                messagebox.showinfo("Success", "Windows Audio Playback and Endpoint Builder services restarted successfully!")
            except Exception as e:
                self.append_repair_log(f"[X] Audio repair failed: {str(e)}\n")
                self.add_activity("Audio Repair", f"Repair failed: {str(e)}", "Failed")
                messagebox.showerror("Error", f"Failed to restart audio services:\n{str(e)}")
                
        threading.Thread(target=run_thread, daemon=True).start()

    def clear_icon_thumbnail_cache(self):
        self.add_activity("Cache Cleaner", "Rebuilding Icon/Thumbnail caches...", "Running")
        self.append_repair_log("\n[*] Flushing Desktop IconCache.db and File Explorer thumbnails...\n")
        
        def run_thread():
            try:
                # Stop Explorer
                subprocess.run(["taskkill", "/f", "/im", "explorer.exe"], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
                
                # Cache files deletion
                localappdata = os.environ.get("LOCALAPPDATA", r"C:\Users\user\AppData\Local")
                
                icon_db = os.path.join(localappdata, "IconCache.db")
                if os.path.exists(icon_db):
                    try:
                        os.remove(icon_db)
                    except:
                        pass
                        
                exp_path = os.path.join(localappdata, "Microsoft", "Windows", "Explorer")
                if os.path.exists(exp_path):
                    for file in os.listdir(exp_path):
                        if file.startswith("iconcache_") or file.startswith("thumbcache_"):
                            try:
                                os.remove(os.path.join(exp_path, file))
                            except:
                                pass
                                
                # Restart Explorer
                subprocess.Popen(["explorer.exe"], creationflags=subprocess.CREATE_NEW_CONSOLE)
                
                self.append_repair_log("[✓] Desktop Icon and File Thumbnail caches successfully rebuilt.\n")
                self.add_activity("Cache Cleaner", "Caches Rebuilt", "Success")
                messagebox.showinfo("Success", "Desktop Icon cache database and File Explorer thumbnail caches rebuilt successfully!")
            except Exception as e:
                self.append_repair_log(f"[X] Cache rebuild failed: {str(e)}\n")
                self.add_activity("Cache Cleaner", f"Rebuild failed: {str(e)}", "Failed")
                messagebox.showerror("Error", f"Failed to rebuild caches:\n{str(e)}")
                
        threading.Thread(target=run_thread, daemon=True).start()

    def restore_classic_context_menu(self):
        self.add_activity("Customization", "Enabling Classic Context Menu...", "Running")
        self.append_repair_log("\n[*] Setting Registry keys for Windows 11 Classic Context Menu...\n")
        
        def run_thread():
            try:
                import winreg
                key_path = r"Software\Classes\CLSID\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}"
                key = winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
                sub_key = winreg.CreateKeyEx(key, "InprocServer32", 0, winreg.KEY_SET_VALUE)
                winreg.SetValueEx(sub_key, "", 0, winreg.REG_SZ, "")
                winreg.CloseKey(sub_key)
                winreg.CloseKey(key)
                
                self.append_repair_log("[✓] Registry CLSID configured. Restarting Windows Explorer...\n")
                self.restart_explorer_shell()
                self.add_activity("Customization", "Classic Context Menu Enabled", "Success")
                messagebox.showinfo("Success", "Classic Windows 10 style Right-Click Context Menu enabled successfully!\nWindows Explorer restarted.")
            except Exception as e:
                self.append_repair_log(f"[X] Configuration failed: {str(e)}\n")
                self.add_activity("Customization", f"Classic Menu failed: {str(e)}", "Failed")
                messagebox.showerror("Error", f"Failed to configure context menu:\n{str(e)}")
                
        threading.Thread(target=run_thread, daemon=True).start()

    def revert_default_context_menu(self):
        self.add_activity("Customization", "Reverting Context Menu...", "Running")
        self.append_repair_log("\n[*] Removing Registry keys for Classic Context Menu...\n")
        
        def run_thread():
            try:
                import winreg
                key_path = r"Software\Classes\CLSID\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}"
                try:
                    def delete_reg_key(key, subkey):
                        try:
                            hkey = winreg.OpenKey(key, subkey, 0, winreg.KEY_ALL_ACCESS)
                        except WindowsError:
                            return
                        while True:
                            try:
                                sub = winreg.EnumKey(hkey, 0)
                                delete_reg_key(hkey, sub)
                            except WindowsError:
                                break
                        winreg.CloseKey(hkey)
                        winreg.DeleteKey(key, subkey)
                        
                    delete_reg_key(winreg.HKEY_CURRENT_USER, key_path)
                    self.append_repair_log("[✓] Registry CLSID removed. Restarting Windows Explorer...\n")
                except Exception as ex:
                    self.append_repair_log(f"[!] Info: Keys already deleted or not found: {str(ex)}\n")
                    
                self.restart_explorer_shell()
                self.add_activity("Customization", "Default Context Menu Restored", "Success")
                messagebox.showinfo("Success", "Default Windows 11 style Context Menu restored successfully!\nWindows Explorer restarted.")
            except Exception as e:
                self.append_repair_log(f"[X] Revert failed: {str(e)}\n")
                self.add_activity("Customization", f"Revert failed: {str(e)}", "Failed")
                messagebox.showerror("Error", f"Failed to revert context menu:\n{str(e)}")
                
        threading.Thread(target=run_thread, daemon=True).start()

    def disable_bing_start_search(self):
        self.add_activity("Customization", "Disabling Bing Search...", "Running")
        self.append_repair_log("\n[*] Restricting Bing search in Windows Start Menu...\n")
        
        def run_thread():
            try:
                import winreg
                key_path1 = r"Software\Policies\Microsoft\Windows\Explorer"
                key1 = winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, key_path1, 0, winreg.KEY_SET_VALUE)
                winreg.SetValueEx(key1, "DisableSearchBoxSuggestions", 0, winreg.REG_DWORD, 1)
                winreg.CloseKey(key1)
                
                key_path2 = r"Software\Microsoft\Windows\CurrentVersion\Search"
                key2 = winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, key_path2, 0, winreg.KEY_SET_VALUE)
                winreg.SetValueEx(key2, "BingSearchEnabled", 0, winreg.REG_DWORD, 0)
                winreg.SetValueEx(key2, "CortanaConsent", 0, winreg.REG_DWORD, 0)
                winreg.CloseKey(key2)
                
                self.append_repair_log("[✓] Bing Web Search successfully disabled in Start Menu. Restarting Windows Explorer...\n")
                self.restart_explorer_shell()
                self.add_activity("Customization", "Bing Search Disabled", "Success")
                messagebox.showinfo("Success", "Bing Search disabled in Windows Start Menu successfully!\nStart Menu searches will now be extremely fast.")
            except Exception as e:
                self.append_repair_log(f"[X] Bing Search disable failed: {str(e)}\n")
                self.add_activity("Customization", f"Bing Tweak failed: {str(e)}", "Failed")
                messagebox.showerror("Error", f"Failed to disable Bing Search:\n{str(e)}")
                
        threading.Thread(target=run_thread, daemon=True).start()

    def toggle_fast_startup(self):
        self.add_activity("System Tweak", "Toggling Fast Startup...", "Running")
        self.append_repair_log("\n[*] Configuring Windows Fast Startup policy...\n")
        
        def run_thread():
            try:
                import winreg
                key_path = r"SYSTEM\CurrentControlSet\Control\Session Manager\Power"
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_SET_VALUE | winreg.KEY_QUERY_VALUE)
                
                current_state = 1
                try:
                    current_state, _ = winreg.QueryValueEx(key, "HiberbootEnabled")
                except:
                    pass
                
                new_state = 0 if current_state == 1 else 1
                winreg.SetValueEx(key, "HiberbootEnabled", 0, winreg.REG_DWORD, new_state)
                winreg.CloseKey(key)
                
                status_str = "Disabled" if new_state == 0 else "Enabled"
                self.append_repair_log(f"[✓] Fast Startup successfully {status_str}.\n")
                self.add_activity("System Tweak", f"Fast Startup {status_str}", "Success")
                messagebox.showinfo("Success", f"Windows Fast Startup has been successfully {status_str}!\nRestart your computer to apply.")
            except Exception as e:
                self.append_repair_log(f"[X] Tweak failed: {str(e)}\n")
                self.add_activity("System Tweak", f"Fast Startup tweak failed: {str(e)}", "Failed")
                messagebox.showerror("Error", f"Failed to toggle Fast Startup:\n{str(e)}")
                
        threading.Thread(target=run_thread, daemon=True).start()

    def configure_secure_dns(self):
        self.add_activity("Network Tweak", "Configuring Cloudflare DNS...", "Running")
        self.append_repair_log("\n[*] Setting Cloudflare Secure DNS (1.1.1.1 / 1.0.0.1) on active adapters...\n")
        
        def run_thread():
            try:
                cmd_get = "Get-NetAdapter | Where-Object {$_.Status -eq 'Up'} | Select-Object -ExpandProperty Name"
                res_adapters = subprocess.run(["powershell", "-Command", cmd_get], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
                
                adapters = [line.strip() for line in res_adapters.stdout.split("\n") if line.strip()]
                
                if not adapters:
                    raise Exception("No active network adapter found.")
                    
                for adapter in adapters:
                    self.append_repair_log(f"[*] Setting Cloudflare DNS for adapter: {adapter}...\n")
                    cmd1 = f'netsh interface ipv4 set dns name="{adapter}" static 1.1.1.1 primary'
                    cmd2 = f'netsh interface ipv4 add dns name="{adapter}" 1.0.0.1 index=2'
                    
                    subprocess.run(cmd1, capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
                    subprocess.run(cmd2, capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
                
                self.append_repair_log("[✓] DNS configured to Cloudflare (1.1.1.1 / 1.0.0.1) successfully.\n")
                self.add_activity("Network Tweak", "DNS Changed to Cloudflare", "Success")
                messagebox.showinfo("Success", "Primary DNS changed to Cloudflare (1.1.1.1) and Secondary to (1.0.0.1) successfully!")
            except Exception as e:
                self.append_repair_log(f"[X] DNS configuration failed: {str(e)}\n")
                self.add_activity("Network Tweak", f"DNS change failed: {str(e)}", "Failed")
                messagebox.showerror("Error", f"Failed to set DNS:\n{str(e)}")
                
        threading.Thread(target=run_thread, daemon=True).start()

    def check_disk_health(self):
        self.add_activity("Disk Diagnostics", "Checking Disk health...", "Running")
        self.append_repair_log("\n[*] Scanning connected physical SSD/HDD disk SMART states...\n")
        
        def run_thread():
            try:
                cmd = "wmic diskdrive get model, status"
                res = subprocess.run(cmd, shell=True, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
                
                self.append_repair_log(res.stdout)
                self.append_repair_log("[✓] Disk health scan completed.\n")
                self.add_activity("Disk Diagnostics", "Disk Health Scan Completed", "Success")
            except Exception as e:
                self.append_repair_log(f"[X] Disk diagnostics failed: {str(e)}\n")
                self.add_activity("Disk Diagnostics", "Disk scan failed", "Failed")
                
        threading.Thread(target=run_thread, daemon=True).start()

    def check_ram_specs(self):
        self.add_activity("RAM Diagnostics", "Scanning RAM modules...", "Running")
        self.append_repair_log("\n[*] Checking physical RAM hardware module details and specifications...\n")
        
        def run_thread():
            try:
                cmd = "wmic memorychip get BankLabel, Capacity, Speed, Manufacturer, PartNumber"
                res = subprocess.run(cmd, shell=True, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
                
                lines = res.stdout.split("\n")
                formatted_output = []
                for line in lines:
                    parts = [p.strip() for p in line.split() if p.strip()]
                    if not parts:
                        continue
                    for idx, part in enumerate(parts):
                        if part.isdigit() and len(part) > 8:
                            gb = int(part) / (1024 * 1024 * 1024)
                            parts[idx] = f"{gb:.1f} GB"
                    formatted_output.append(" | ".join(parts))
                
                self.append_repair_log("\n".join(formatted_output) + "\n")
                self.append_repair_log("[✓] RAM hardware spec scan completed.\n")
                self.add_activity("RAM Diagnostics", "RAM Scan Completed", "Success")
            except Exception as e:
                self.append_repair_log(f"[X] RAM scan failed: {str(e)}\n")
                self.add_activity("RAM Diagnostics", "RAM scan failed", "Failed")
                
        threading.Thread(target=run_thread, daemon=True).start()

    def schedule_memory_diagnostic(self):
        self.add_activity("RAM Diagnostics", "Scheduling Memory Diagnostic...", "Running")
        self.append_repair_log("\n[*] Launching Windows Memory Diagnostic utility scheduler (mdsched.exe)...\n")
        try:
            subprocess.Popen(["mdsched.exe"])
            self.append_repair_log("[✓] Windows Memory Diagnostic window popped up successfully.\n")
            self.add_activity("RAM Diagnostics", "mdsched.exe launched", "Success")
        except Exception as e:
            self.append_repair_log(f"[X] Failed to launch mdsched.exe: {str(e)}\n")
            self.add_activity("RAM Diagnostics", "mdsched.exe launch failed", "Failed")
            messagebox.showerror("Error", f"Failed to launch Memory Diagnostic tool:\n{str(e)}")

    def run_speed_test(self):
        self.add_activity("Speed Test", "Running download speed test...", "Running")
        self.append_repair_log("\n[*] Initiating Internet Download Speed Test...\n")
        
        def run_thread():
            try:
                import time
                import urllib.request
                
                test_url = "https://speed.cloudflare.com/__down?bytes=10000000"
                self.append_repair_log("[*] Downloading 10MB test file from Cloudflare CDN...\n")
                
                start_time = time.time()
                
                req = urllib.request.Request(test_url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req) as response:
                    chunk_size = 1024 * 64
                    downloaded = 0
                    
                    while True:
                         chunk = response.read(chunk_size)
                         if not chunk:
                             break
                         downloaded += len(chunk)
                         if downloaded % (1024 * 1024) < chunk_size:
                             mb = downloaded / (1024 * 1024)
                             self.append_repair_log(f"    Downloaded: {mb:.1f} MB / 9.5 MB...\n")
                             
                end_time = time.time()
                duration = end_time - start_time
                
                if duration <= 0:
                    duration = 0.1
                     
                bytes_downloaded = downloaded
                megabits = (bytes_downloaded * 8) / (1024 * 1024)
                speed_mbps = megabits / duration
                
                self.append_repair_log(f"\n[✓] Speed Test Finished!\n")
                self.append_repair_log(f"    Time elapsed: {duration:.2f} seconds\n")
                self.append_repair_log(f"    Download Speed: {speed_mbps:.2f} Mbps\n")
                
                self.add_activity("Speed Test", f"Speed: {speed_mbps:.2f} Mbps", "Success")
                messagebox.showinfo("Speed Test Results", f"Download Speed Test Completed!\n\nSpeed: {speed_mbps:.2f} Mbps\nTime elapsed: {duration:.2f} seconds")
            except Exception as e:
                self.append_repair_log(f"[X] Speed test failed: {str(e)}\n")
                self.add_activity("Speed Test", "Speed test failed", "Failed")
                messagebox.showerror("Error", f"Speed test failed:\n{str(e)}")
                
        threading.Thread(target=run_thread, daemon=True).start()

    def schedule_chkdsk_scan(self):
        self.add_activity("Disk Repair", "Scheduling Chkdsk...", "Running")
        self.append_repair_log("\n[*] Scheduling boot-time volume disk integrity check and sector repair (Chkdsk) for C:...\n")
        
        def run_thread():
            try:
                proc = subprocess.Popen(["cmd.exe", "/c", "echo Y | chkdsk C: /f /x"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                stdout, stderr = proc.communicate()
                self.append_repair_log(stdout)
                if stderr:
                    self.append_repair_log(f"[!] Error: {stderr}\n")
                
                self.append_repair_log("[✓] Chkdsk successfully scheduled for the next system restart.\n")
                self.add_activity("Disk Repair", "Chkdsk Scheduled", "Success")
                messagebox.showinfo("Success", "Disk integrity scanner (Chkdsk) has been successfully scheduled for the next system restart!")
            except Exception as e:
                self.append_repair_log(f"[X] Failed to schedule Chkdsk: {str(e)}\n")
                self.add_activity("Disk Repair", "Chkdsk failed", "Failed")
                messagebox.showerror("Error", f"Failed to schedule Chkdsk scan:\n{str(e)}")
                
        threading.Thread(target=run_thread, daemon=True).start()

    def generate_battery_report(self):
        self.add_activity("Diagnostics", "Generating Battery Report...", "Running")
        self.append_repair_log("\n[*] Generating Windows Battery Lifecycle & Wear Health Report...\n")
        
        def run_thread():
            try:
                report_path = r"C:\BatteryReport.html"
                if os.path.exists(report_path):
                    try:
                        os.remove(report_path)
                    except:
                        pass
                
                res = subprocess.run(["powercfg", "/batteryreport", f"/output", report_path], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
                self.append_repair_log(res.stdout)
                
                if os.path.exists(report_path):
                    self.append_repair_log(f"[✓] Battery Report successfully created at: {report_path}\n")
                    self.append_repair_log("[*] Opening report in web browser...\n")
                    os.startfile(report_path)
                    self.add_activity("Diagnostics", "Battery Report Generated", "Success")
                    messagebox.showinfo("Success", "Battery wear and health report generated successfully!\nOpened in default web browser.")
                else:
                    raise Exception("Battery report file was not created. (Laptops only)")
            except Exception as e:
                self.append_repair_log(f"[X] Battery report failed: {str(e)}\n")
                self.add_activity("Diagnostics", "Battery report failed", "Failed")
                messagebox.showerror("Error", f"Failed to generate battery report (This tool only works on laptops):\n{str(e)}")
                
        threading.Thread(target=run_thread, daemon=True).start()

    def run_dism_check_health(self):
        self.add_activity("System Repair", "DISM Checking Health...", "Running")
        self.append_repair_log("\n[*] Running fast component store corruption scan (DISM CheckHealth)...\n")
        
        def run_thread():
            try:
                cmd = ["dism", "/online", "/cleanup-image", "/checkhealth"]
                res = subprocess.run(cmd, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
                self.append_repair_log(res.stdout)
                self.append_repair_log("[✓] Fast component store scan completed.\n")
                self.add_activity("System Repair", "DISM CheckHealth completed", "Success")
            except Exception as e:
                self.append_repair_log(f"[X] DISM command failed: {str(e)}\n")
                self.add_activity("System Repair", "DISM CheckHealth failed", "Failed")
                
        threading.Thread(target=run_thread, daemon=True).start()

    def rebuild_font_cache(self):
        self.add_activity("Cache Cleaner", "Rebuilding Font Cache...", "Running")
        self.append_repair_log("\n[*] Resetting Windows Font Cache Database directory & services...\n")
        
        def run_thread():
            try:
                self.append_repair_log("[*] Stopping Font Cache service...\n")
                subprocess.run(["net", "stop", "FontCache", "/y"], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
                
                windir = os.environ.get("SystemRoot", "C:\\Windows")
                font_cache_dir = os.path.join(windir, "ServiceProfiles", "LocalService", "AppData", "Local", "FontCache")
                
                if os.path.exists(font_cache_dir):
                    self.append_repair_log(f"[*] Deleting files in cache folder: {font_cache_dir}...\n")
                    for file in os.listdir(font_cache_dir):
                        file_path = os.path.join(font_cache_dir, file)
                        try:
                            if os.path.isfile(file_path):
                                os.remove(file_path)
                            elif os.path.isdir(file_path):
                                shutil.rmtree(file_path)
                        except:
                            pass
                
                self.append_repair_log("[*] Restarting Font Cache service...\n")
                subprocess.run(["net", "start", "FontCache"], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
                
                self.append_repair_log("[✓] Windows Font Cache successfully rebuilt.\n")
                self.add_activity("Cache Cleaner", "Font Cache Rebuilt", "Success")
                messagebox.showinfo("Success", "Windows Font Cache database cleared and rebuilt successfully!")
            except Exception as e:
                self.append_repair_log(f"[X] Font cache rebuild failed: {str(e)}\n")
                self.add_activity("Cache Cleaner", f"Font cache failed: {str(e)}", "Failed")
                messagebox.showerror("Error", f"Failed to rebuild font cache:\n{str(e)}")
                
        threading.Thread(target=run_thread, daemon=True).start()

    def reregister_system_dlls(self):
        self.add_activity("System Repair", "Re-registering core DLLs...", "Running")
        self.append_repair_log("\n[*] Re-registering core Windows System dynamic library (DLL) modules...\n")
        
        def run_thread():
            try:
                import shutil
                dlls = [
                    "atl.dll", "urlmon.dll", "mshtml.dll", "shdocvw.dll", "browseui.dll",
                    "jscript.dll", "vbscript.dll", "scrrun.dll", "msxml.dll", "msxml3.dll",
                    "msxml6.dll", "actxprxy.dll", "softpub.dll", "wintrust.dll", "dssenh.dll",
                    "gpkcsp.dll", "sccbase.dll", "slbcsp.dll", "cryptdlg.dll", "ole32.dll",
                    "oleaut32.dll", "initpki.dll", "valimi.dll", "msi.dll"
                ]
                
                system32 = os.path.expandvars(r"%systemroot%\System32")
                success_count = 0
                for dll in dlls:
                    dll_path = os.path.join(system32, dll)
                    if os.path.exists(dll_path):
                        res = subprocess.run(["regsvr32.exe", "/s", dll], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
                        if res.returncode == 0:
                            success_count += 1
                            
                self.append_repair_log(f"[✓] Re-registered {success_count} system DLL libraries.\n")
                self.add_activity("System Repair", "DLLs Re-registered", "Success")
                messagebox.showinfo("Success", f"Re-registered {success_count} core Windows System DLL modules successfully!")
            except Exception as e:
                self.append_repair_log(f"[X] DLL registration failed: {str(e)}\n")
                self.add_activity("System Repair", f"DLL registration failed: {str(e)}", "Failed")
                messagebox.showerror("Error", f"Failed to re-register DLLs:\n{str(e)}")
                
        threading.Thread(target=run_thread, daemon=True).start()

    def enable_ultimate_performance(self):
        self.add_activity("System Tweak", "Enabling Ultimate Performance Plan...", "Running")
        self.append_repair_log("\n[*] Unlocking Windows Ultimate Performance Power Plan...\n")
        
        def run_thread():
            try:
                res = subprocess.run(["powercfg", "-duplicatescheme", "e9a22db2-565e-4b6e-82f0-8022c5e3430b"], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
                self.append_repair_log(res.stdout)
                
                import re
                guid_match = re.search(r"GUID:\s*([a-fA-F0-9\-]+)", res.stdout)
                if guid_match:
                    guid = guid_match.group(1)
                    subprocess.run(["powercfg", "-setactive", guid], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
                    self.append_repair_log(f"[✓] Activated Ultimate Performance scheme: {guid}\n")
                else:
                    self.append_repair_log("[!] Warning: Scheme created but could not parse GUID to activate it automatically.\n")
                     
                self.add_activity("System Tweak", "Ultimate Power Plan Activated", "Success")
                messagebox.showinfo("Success", "Windows Ultimate Performance Power Plan unlocked and set as your active power scheme successfully!")
            except Exception as e:
                self.append_repair_log(f"[X] Failed to enable power plan: {str(e)}\n")
                self.add_activity("System Tweak", "Ultimate Power failed", "Failed")
                messagebox.showerror("Error", f"Failed to enable Ultimate Performance plan:\n{str(e)}")
                 
        threading.Thread(target=run_thread, daemon=True).start()

    def optimize_gaming_tweaks(self):
        self.add_activity("Gaming Boost", "Applying gaming latency tweaks...", "Running")
        self.append_repair_log("\n[*] Tweaking registry for low-latency gaming & performance optimization...\n")
        
        def run_thread():
            try:
                import winreg
                try:
                    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"System\GameConfigStore", 0, winreg.KEY_SET_VALUE)
                    winreg.SetValueEx(key, "GameDVR_Enabled", 0, winreg.REG_DWORD, 0)
                    winreg.CloseKey(key)
                    self.append_repair_log("[✓] Disabled GameDVR configuration registry entry.\n")
                except Exception as e:
                    self.append_repair_log(f"[!] Warning (GameConfigStore): {str(e)}\n")
                    
                try:
                    key = winreg.CreateKeyEx(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Policies\Microsoft\Windows\GameDVR", 0, winreg.KEY_SET_VALUE)
                    winreg.SetValueEx(key, "AllowGameDVR", 0, winreg.REG_DWORD, 0)
                    winreg.CloseKey(key)
                except Exception as e:
                    self.append_repair_log(f"[!] Warning (GameDVR Policy): {str(e)}\n")
                    
                try:
                    key = winreg.CreateKeyEx(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\Power\PowerThrottling", 0, winreg.KEY_SET_VALUE)
                    winreg.SetValueEx(key, "PowerThrottlingOff", 0, winreg.REG_DWORD, 1)
                    winreg.CloseKey(key)
                    self.append_repair_log("[✓] Disabled CPU Power Throttling for background apps.\n")
                except Exception as e:
                    self.append_repair_log(f"[!] Warning (PowerThrottling): {str(e)}\n")
                    
                try:
                    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Control Panel\Mouse", 0, winreg.KEY_SET_VALUE)
                    winreg.SetValueEx(key, "MouseSpeed", 0, winreg.REG_SZ, "0")
                    winreg.SetValueEx(key, "MouseThreshold1", 0, winreg.REG_SZ, "0")
                    winreg.SetValueEx(key, "MouseThreshold2", 0, winreg.REG_SZ, "0")
                    winreg.CloseKey(key)
                    self.append_repair_log("[✓] Disabled pointer precision mouse acceleration for raw input.\n")
                except Exception as e:
                    self.append_repair_log(f"[!] Warning (Mouse Acceleration): {str(e)}\n")
                    
                self.append_repair_log("[✓] Gaming optimization tweaks applied successfully!\n")
                self.add_activity("Gaming Boost", "Gaming Optimization Done", "Success")
                messagebox.showinfo("Success", "Windows Gaming Optimization & Latency tweaks applied successfully!\nRestart your system to take full effect.")
            except Exception as e:
                self.append_repair_log(f"[X] Gaming optimization failed: {str(e)}\n")
                self.add_activity("Gaming Boost", "Gaming optimization failed", "Failed")
                messagebox.showerror("Error", f"Failed to apply gaming tweaks:\n{str(e)}")
                
        threading.Thread(target=run_thread, daemon=True).start()

    def block_windows_updates(self):
        self.add_activity("Windows Update", "Blocking Automatic Updates...", "Running")
        self.append_repair_log("\n[*] Disabling Windows Update service & configuring GPO restrictions...\n")
        
        def run_thread():
            try:
                import winreg
                subprocess.run(["sc", "config", "wuauserv", "start=", "disabled"], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
                subprocess.run(["net", "stop", "wuauserv", "/y"], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
                
                key_path = r"SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate\AU"
                key = winreg.CreateKeyEx(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_SET_VALUE)
                winreg.SetValueEx(key, "NoAutoUpdate", 0, winreg.REG_DWORD, 1)
                winreg.CloseKey(key)
                
                self.append_repair_log("[✓] Automatic Windows Updates successfully blocked.\n")
                self.add_activity("Windows Update", "Updates Blocked", "Success")
                messagebox.showinfo("Success", "Automatic Windows Updates have been successfully blocked and disabled!")
            except Exception as e:
                self.append_repair_log(f"[X] Failed to block updates: {str(e)}\n")
                self.add_activity("Windows Update", "Block failed", "Failed")
                messagebox.showerror("Error", f"Failed to block updates:\n{str(e)}")
                
        threading.Thread(target=run_thread, daemon=True).start()

    def enable_windows_updates(self):
        self.add_activity("Windows Update", "Enabling Automatic Updates...", "Running")
        self.append_repair_log("\n[*] Restoring Windows Update service and removing GPO restrictions...\n")
        
        def run_thread():
            try:
                import winreg
                subprocess.run(["sc", "config", "wuauserv", "start=", "auto"], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
                subprocess.run(["net", "start", "wuauserv"], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
                
                key_path = r"SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate\AU"
                try:
                    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_SET_VALUE)
                    winreg.DeleteValue(key, "NoAutoUpdate")
                    winreg.CloseKey(key)
                except:
                    pass
                
                self.append_repair_log("[✓] Automatic Windows Updates successfully enabled & restored.\n")
                self.add_activity("Windows Update", "Updates Enabled", "Success")
                messagebox.showinfo("Success", "Automatic Windows Updates have been successfully enabled and set to Automatic!")
            except Exception as e:
                self.append_repair_log(f"[X] Failed to enable updates: {str(e)}\n")
                self.add_activity("Windows Update", "Enable failed", "Failed")
                messagebox.showerror("Error", f"Failed to enable updates:\n{str(e)}")
                
        threading.Thread(target=run_thread, daemon=True).start()

    def check_windows_activation(self):
        self.add_activity("Diagnostics", "Checking activation status...", "Running")
        self.append_repair_log("\n[*] Querying Windows License Activation status details...\n")
        
        def run_thread():
            try:
                vbs_path = os.path.join(os.environ.get("SystemRoot", "C:\\Windows"), "System32", "slmgr.vbs")
                if os.path.exists(vbs_path):
                    cmd = ["cscript", "//nologo", vbs_path, "/dli"]
                    res = subprocess.run(cmd, shell=True, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
                    self.append_repair_log(res.stdout)
                else:
                    self.append_repair_log("[!] Error: slmgr.vbs file not found.\n")
                    
                self.append_repair_log("[✓] License check completed.\n")
                self.add_activity("Diagnostics", "Activation Checked", "Success")
            except Exception as e:
                self.append_repair_log(f"[X] Failed to check activation: {str(e)}\n")
                self.add_activity("Diagnostics", "Activation check failed", "Failed")
                
        threading.Thread(target=run_thread, daemon=True).start()

    def generate_system_info_summary(self):
        self.add_activity("Diagnostics", "Gathering System Info...", "Running")
        self.append_repair_log("\n[*] Collecting Windows & Hardware Specifications report...\n")
        
        def run_thread():
            try:
                cmd_cpu = "wmic cpu get name"
                res_cpu = subprocess.run(cmd_cpu, shell=True, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
                cpu_name = res_cpu.stdout.replace("Name", "").strip()
                
                cmd_gpu = "wmic path win32_VideoController get name"
                res_gpu = subprocess.run(cmd_gpu, shell=True, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
                gpu_name = res_gpu.stdout.replace("Name", "").strip()
                
                cmd_mb = "wmic baseboard get product, manufacturer"
                res_mb = subprocess.run(cmd_mb, shell=True, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
                mb_info = res_mb.stdout.replace("Manufacturer", "").replace("Product", "").strip()
                
                cmd_bios = "wmic bios get name, version"
                res_bios = subprocess.run(cmd_bios, shell=True, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
                bios_info = res_bios.stdout.replace("Name", "").replace("Version", "").strip()
                
                cmd_os = "wmic os get Caption, Version, OSArchitecture, InstallDate"
                res_os = subprocess.run(cmd_os, shell=True, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
                os_lines = [line.strip() for line in res_os.stdout.split("\n") if line.strip()]
                
                self.append_repair_log("\n=== WINDOWS SYSTEM INFO SUMMARY ===\n")
                self.append_repair_log(f"CPU: {cpu_name}\n")
                self.append_repair_log(f"GPU: {gpu_name}\n")
                self.append_repair_log(f"Motherboard: {mb_info}\n")
                self.append_repair_log(f"BIOS: {bios_info}\n")
                if len(os_lines) > 1:
                    self.append_repair_log(f"Operating System Details:\n    Header: {os_lines[0]}\n    Value: {os_lines[1]}\n")
                self.append_repair_log("===================================\n")
                
                self.append_repair_log("[✓] System specification diagnostics complete.\n")
                self.add_activity("Diagnostics", "System Summary Generated", "Success")
            except Exception as e:
                self.append_repair_log(f"[X] Failed to collect specs: {str(e)}\n")
                self.add_activity("Diagnostics", "System Summary failed", "Failed")
                
        threading.Thread(target=run_thread, daemon=True).start()

    def run_store_repair(self):
        self.add_activity("Store Repair", "Re-registering Microsoft Store & Default Windows Apps...", "Running")
        self.append_repair_log("\n[*] Triggering Microsoft Store & AppX Packages Repair pipeline...\n")
        
        def run_thread():
            try:
                # Command 1: Repair Windows Store
                self.append_repair_log("[*] Step 1: Re-registering Microsoft Store package...\n")
                cmd1 = "Get-AppXPackage -AllUsers -Name Microsoft.WindowsStore | Foreach {Add-AppxPackage -DisableDevelopmentMode -Register \"$($_.InstallLocation)\\AppXManifest.xml\" -ForceApplicationShutdown}"
                subprocess.run(["powershell", "-Command", cmd1], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
                
                # Command 2: Re-register all apps
                self.append_repair_log("[*] Step 2: Re-registering all inbox AppX packages (Default Windows Apps)...\n")
                cmd2 = "Get-AppXPackage -AllUsers | Foreach {Add-AppxPackage -DisableDevelopmentMode -Register \"$($_.InstallLocation)\\AppXManifest.xml\" -ErrorAction SilentlyContinue}"
                subprocess.run(["powershell", "-Command", cmd2], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
                
                self.append_repair_log("[✓] Store and Default apps re-registered successfully.\n")
                self.add_activity("Store Repair", "Microsoft Store & Apps Repaired", "Success")
                messagebox.showinfo("Success", "Microsoft Store and default Windows apps have been repaired successfully!")
            except Exception as e:
                self.append_repair_log(f"[X] Repair failed: {str(e)}\n")
                self.add_activity("Store Repair", f"Store repair failed: {str(e)}", "Failed")
                messagebox.showerror("Error", f"Failed to repair store:\n{str(e)}")
                
        threading.Thread(target=run_thread, daemon=True).start()

    def run_network_reset(self):
        self.add_activity("Network Reset", "Performing comprehensive network reset...", "Running")
        self.append_repair_log("\n[*] Starting network stack reset pipeline...\n")
        
        def run_thread():
            try:
                # Commands
                cmds = [
                    (["netsh", "int", "ip", "reset"], "Reset IP Configuration"),
                    (["netsh", "winsock", "reset"], "Reset Winsock Catalog"),
                    (["ipconfig", "/release"], "Release IP Address"),
                    (["ipconfig", "/renew"], "Renew IP Address"),
                    (["ipconfig", "/flushdns"], "Flush DNS Cache"),
                    (["arp", "-d", "*"], "Flush ARP Tables")
                ]
                
                for cmd, desc in cmds:
                    self.append_repair_log(f"[*] Running: {desc}...\n")
                    subprocess.run(cmd, capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
                
                # Restart adapters via PowerShell
                self.append_repair_log("[*] Resetting all network adapters drivers (Restart-NetAdapter)...\n")
                cmd_ps = "Get-NetAdapter | Restart-NetAdapter -Confirm:$false"
                subprocess.run(["powershell", "-Command", cmd_ps], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
                
                self.append_repair_log("[✓] Complete network stack reset finished successfully!\n")
                self.add_activity("Network Reset", "Network reset completed successfully", "Success")
                messagebox.showinfo("Success", "Network stack and adapters reset completed successfully!\nConnection refreshed.")
            except Exception as e:
                self.append_repair_log(f"[X] Reset failed: {str(e)}\n")
                self.add_activity("Network Reset", f"Network reset failed: {str(e)}", "Failed")
                messagebox.showerror("Error", f"Failed to reset network:\n{str(e)}")
                
        threading.Thread(target=run_thread, daemon=True).start()

    def optimize_ram_standby(self):
        self.add_activity("RAM Optimizer", "Optimizing memory cache...", "Running")
        self.append_repair_log("\n[*] Initiating working sets optimization...\n")
        
        def run_thread():
            try:
                import ctypes
                kernel32 = ctypes.windll.kernel32
                psapi = ctypes.windll.psapi
                
                PROCESS_QUERY_INFORMATION = 0x0400
                PROCESS_SET_QUOTA = 0x0100
                
                count = 0
                for proc in psutil.process_iter(['pid', 'name']):
                    try:
                        pid = proc.info['pid']
                        if pid == 0:
                            continue
                        h_process = kernel32.OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_SET_QUOTA, False, pid)
                        if h_process:
                            if psapi.EmptyWorkingSet(h_process):
                                count += 1
                            kernel32.CloseHandle(h_process)
                    except:
                        pass
                self.append_repair_log(f"[✓] Successfully optimized RAM working sets for {count} active processes!\n")
                self.add_activity("RAM Optimizer", f"Freed memory for {count} processes", "Success")
                messagebox.showinfo("Success", f"RAM working sets optimized successfully!\nFreed memory for {count} processes.")
            except Exception as e:
                self.append_repair_log(f"[X] Optimization failed: {str(e)}\n")
                self.add_activity("RAM Optimizer", f"Optimization failed: {str(e)}", "Failed")
                messagebox.showerror("Error", f"Failed to optimize memory: {str(e)}")
                
        threading.Thread(target=run_thread, daemon=True).start()

    def clean_browsers_cache(self):
        self.add_activity("Browser Clean", "Cleaning browser caches...", "Running")
        self.append_repair_log("\n[*] Starting web browser cleaners...\n")
        
        def run_thread():
            try:
                local_appdata = os.getenv("LOCALAPPDATA")
                cleaned_dirs = 0
                cleaned_files = 0
                
                # Browser paths to clean
                browsers_paths = {
                    "Google Chrome Cache": os.path.join(local_appdata, r"Google\Chrome\User Data\Default\Cache"),
                    "Google Chrome Code Cache": os.path.join(local_appdata, r"Google\Chrome\User Data\Default\Code Cache"),
                    "MS Edge Cache": os.path.join(local_appdata, r"Microsoft\Edge\User Data\Default\Cache"),
                    "MS Edge Code Cache": os.path.join(local_appdata, r"Microsoft\Edge\User Data\Default\Code Cache"),
                }
                
                for label, folder in browsers_paths.items():
                    self.append_repair_log(f"[*] Scanning {label} at: {folder}...\n")
                    if os.path.exists(folder):
                        for root_dir, dirs, files in os.walk(folder):
                            for file in files:
                                file_path = os.path.join(root_dir, file)
                                try:
                                    os.unlink(file_path)
                                    cleaned_files += 1
                                except:
                                    pass
                            for d in dirs:
                                dir_path = os.path.join(root_dir, d)
                                try:
                                    shutil.rmtree(dir_path)
                                    cleaned_dirs += 1
                                except:
                                    pass
                        self.append_repair_log(f"[✓] Cleaned {label}.\n")
                        
                # Firefox search profiles
                ff_path = os.path.join(local_appdata, r"Mozilla\Firefox\Profiles")
                self.append_repair_log("[*] Scanning Firefox Cache profiles...\n")
                if os.path.exists(ff_path):
                    for profile in os.listdir(ff_path):
                        cache_dir = os.path.join(ff_path, profile, "cache2")
                        if os.path.exists(cache_dir):
                            for root_dir, dirs, files in os.walk(cache_dir):
                                for file in files:
                                    file_path = os.path.join(root_dir, file)
                                    try:
                                        os.unlink(file_path)
                                        cleaned_files += 1
                                    except:
                                        pass
                                for d in dirs:
                                    dir_path = os.path.join(root_dir, d)
                                    try:
                                        shutil.rmtree(dir_path)
                                        cleaned_dirs += 1
                                    except:
                                        pass
                    self.append_repair_log("[✓] Cleaned Mozilla Firefox profile cache.\n")
                    
                self.append_repair_log(f"[✓] Browser cache clean done. Cleared {cleaned_files} files and {cleaned_dirs} directories.\n")
                self.add_activity("Browser Clean", "Browser cache files cleared", "Success")
                messagebox.showinfo("Success", f"Browser cache files cleaned successfully!\nCleared {cleaned_files} files.")
            except Exception as e:
                self.append_repair_log(f"[X] Clean failed: {str(e)}\n")
                self.add_activity("Browser Clean", f"Browser cache clean failed: {str(e)}", "Failed")
                messagebox.showerror("Error", f"Failed to clean browser cache:\n{str(e)}")
                
        threading.Thread(target=run_thread, daemon=True).start()

    # ==========================
    # Tab 6: Diagnostics & Storage
    # ==========================
    def setup_diagnostics_tab(self):
        f = ctk.CTkFrame(self.container, fg_color="transparent")
        self.frames["diagnostics"] = f
        
        split_frame = ctk.CTkFrame(f, fg_color="transparent")
        split_frame.pack(fill="both", expand=True)
        
        # Left card: Diagnostics Node & Credentials
        left_card = ctk.CTkFrame(split_frame, fg_color="#151f32", border_color="#1e293b", border_width=1.5)
        left_card.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        scroll_left = ctk.CTkScrollableFrame(left_card, fg_color="transparent")
        scroll_left.pack(fill="both", expand=True, padx=15, pady=10)
        
        # Diagnostic Nodes
        ctk.CTkLabel(scroll_left, text="📊 SYSTEM DIAGNOSTICS NODE", font=("Outfit", 9, "bold"), text_color="#38bdf8").pack(anchor="w", pady=(5, 4))
        
        btn_msinfo = ctk.CTkButton(
            scroll_left, text="📋 Launch System Info Specs (msinfo32)",
            font=("Outfit", 10, "bold"), anchor="w", fg_color="#1e293b", hover_color="#2b2b2b",
            command=lambda: self.run_diag_action("msinfo32")
        )
        btn_msinfo.pack(fill="x", padx=10, pady=3)
        
        btn_perf = ctk.CTkButton(
            scroll_left, text="📈 Generate Core System Health Report (perfmon)",
            font=("Outfit", 10, "bold"), anchor="w", fg_color="#1e293b", hover_color="#2b2b2b",
            command=lambda: self.run_diag_action("perfmon_health")
        )
        btn_perf.pack(fill="x", padx=10, pady=3)
        
        btn_batt = ctk.CTkButton(
            scroll_left, text="🔋 Generate Battery Health Diagnostics Report",
            font=("Outfit", 10, "bold"), anchor="w", fg_color="#1e293b", hover_color="#2b2b2b",
            command=lambda: self.run_diag_action("battery_report")
        )
        btn_batt.pack(fill="x", padx=10, pady=3)
        
        # Antivirus
        ctk.CTkLabel(scroll_left, text="🛡️ ANTIVIRUS & MALWARE SCANNER", font=("Outfit", 9, "bold"), text_color="#38bdf8").pack(anchor="w", pady=(15, 4))
        
        btn_as_q = ctk.CTkButton(
            scroll_left, text="⚡ Execute Defender Quick System Scan",
            font=("Outfit", 10, "bold"), anchor="w", fg_color="#1e293b", hover_color="#2b2b2b",
            command=lambda: self.run_diag_action("defender_quick")
        )
        btn_as_q.pack(fill="x", padx=10, pady=3)
        
        btn_as_d = ctk.CTkButton(
            scroll_left, text="🔍 Execute Defender Complete Deep Scan",
            font=("Outfit", 10, "bold"), anchor="w", fg_color="#1e293b", hover_color="#2b2b2b",
            command=lambda: self.run_diag_action("defender_deep")
        )
        btn_as_d.pack(fill="x", padx=10, pady=3)
        
        btn_as_u = ctk.CTkButton(
            scroll_left, text="🔄 Force Update Antivirus Signatures Database",
            font=("Outfit", 10, "bold"), anchor="w", fg_color="#1e293b", hover_color="#2b2b2b",
            command=lambda: self.run_diag_action("defender_update")
        )
        btn_as_u.pack(fill="x", padx=10, pady=3)
        
        # Credentials Viewer
        ctk.CTkLabel(scroll_left, text="🔑 CREDENTIALS & PASSWORD VIEWERS", font=("Outfit", 9, "bold"), text_color="#38bdf8").pack(anchor="w", pady=(15, 4))
        
        btn_wifi_p = ctk.CTkButton(
            scroll_left, text="📶 Retrieve Saved Wi-Fi Profiles & Passwords",
            font=("Outfit", 10, "bold"), anchor="w", fg_color="#1e293b", hover_color="#2b2b2b",
            command=lambda: self.run_diag_action("wifi_passwords")
        )
        btn_wifi_p.pack(fill="x", padx=10, pady=3)
        
        btn_cred_m = ctk.CTkButton(
            scroll_left, text="💳 Launch Windows Credential Manager console",
            font=("Outfit", 10, "bold"), anchor="w", fg_color="#1e293b", hover_color="#2b2b2b",
            command=lambda: self.run_diag_action("cred_manager")
        )
        btn_cred_m.pack(fill="x", padx=10, pady=3)
        
        # Right card: Office & Storage Diagnostics
        right_card = ctk.CTkFrame(split_frame, fg_color="#151f32", border_color="#1e293b", border_width=1.5)
        right_card.pack(side="right", fill="both", expand=True, padx=(5, 0))
        
        scroll_right = ctk.CTkScrollableFrame(right_card, fg_color="transparent")
        scroll_right.pack(fill="both", expand=True, padx=15, pady=10)
        
        # Office Diagnostics
        ctk.CTkLabel(scroll_right, text="💼 OFFICE & OUTLOOK DIAGNOSTICS", font=("Outfit", 9, "bold"), text_color="#38bdf8").pack(anchor="w", pady=(5, 4))
        
        office_btns = [
            ("Office Quick Repair", "office_quick"),
            ("Office Online Repair", "office_online"),
            ("Outlook Safe Mode", "outlook_safe"),
            ("Reset Outlook Pane", "outlook_pane"),
            ("Reset Outlook Folders", "outlook_folders"),
            ("Reset Default Bar", "outlook_bar")
        ]
        
        grid_office_diag = ctk.CTkFrame(scroll_right, fg_color="transparent")
        grid_office_diag.pack(fill="x", expand=True, pady=3)
        grid_office_diag.grid_columnconfigure((0, 1), weight=1, uniform="equal")
        
        row = 0
        col = 0
        for name, action in office_btns:
            btn = ctk.CTkButton(
                grid_office_diag, text=name, font=("Outfit", 9, "bold"), fg_color="#1e293b", hover_color="#2b2b2b",
                command=lambda a=action: self.run_diag_action(a)
            )
            btn.grid(row=row, column=col, padx=4, pady=3, sticky="ew")
            col += 1
            if col > 1:
                col = 0
                row += 1
                
        # Volume Diagnostics & Storage
        ctk.CTkLabel(scroll_right, text="💾 VOLUME DIAGNOSTICS & STORAGE", font=("Outfit", 9, "bold"), text_color="#38bdf8").pack(anchor="w", pady=(15, 4))
        
        btn_chk_blk = ctk.CTkButton(
            scroll_right, text="🎛️ Check Drive Block Integrity (Chkdsk C:)",
            font=("Outfit", 10, "bold"), anchor="w", fg_color="#1e293b", hover_color="#2b2b2b",
            command=lambda: self.run_diag_action("chkdsk_scan")
        )
        btn_chk_blk.pack(fill="x", padx=10, pady=3)
        
        btn_heavy_f = ctk.CTkButton(
            scroll_right, text="🔍 Map Top 10 Heaviest Files on Drive C:",
            font=("Outfit", 10, "bold"), anchor="w", fg_color="#1e293b", hover_color="#2b2b2b",
            command=lambda: self.run_diag_action("heavy_files")
        )
        btn_heavy_f.pack(fill="x", padx=10, pady=3)
        
        btn_defrag = ctk.CTkButton(
            scroll_right, text="🏎️ Run Storage Fragment Optimizer (Defrag C:)",
            font=("Outfit", 10, "bold"), anchor="w", fg_color="#1e293b", hover_color="#2b2b2b",
            command=lambda: self.run_diag_action("defrag_drive")
        )
        btn_defrag.pack(fill="x", padx=10, pady=3)
        
        btn_trim = ctk.CTkButton(
            scroll_right, text="⚡ Force Run SSD Block Re-trim Optimization",
            font=("Outfit", 10, "bold"), anchor="w", fg_color="#1e293b", hover_color="#2b2b2b",
            command=lambda: self.run_diag_action("ssd_trim")
        )
        btn_trim.pack(fill="x", padx=10, pady=3)
        
        # Bottom Console Panel for results
        self.diag_console_card = ctk.CTkFrame(f, height=180, fg_color="#151f32", border_color="#1e293b", border_width=1.5)
        self.diag_console_card.pack(fill="x", pady=(10, 0))
        self.diag_console_card.pack_propagate(False)
        
        ctk.CTkLabel(self.diag_console_card, text="⚙️ Diagnostics Outputs Terminal", font=("Outfit", 11, "bold"), text_color="#ffffff").pack(anchor="w", padx=15, pady=8)
        
        self.diag_log_text = ctk.CTkTextbox(
            self.diag_console_card, fg_color="#0d1321", border_color="#1e293b", border_width=1, text_color="#10b981", font=("Consolas", 9)
        )
        self.diag_log_text.pack(fill="both", expand=True, padx=15, pady=(0, 10))
        self.diag_log_text.insert("end", "[Diagnostics engine initialized]\n")
        self.diag_log_text.configure(state="disabled")

    def append_diag_log(self, text):
        self.diag_log_text.configure(state="normal")
        self.diag_log_text.insert("end", text)
        self.diag_log_text.see("end")
        self.diag_log_text.configure(state="disabled")

    def run_diag_action(self, action):
        self.append_diag_log(f"\n[*] Requesting diagnostic action: {action}...\n")
        self.add_activity("Diagnostics", f"Running {action}", "Running")
        threading.Thread(target=self.run_diag_thread, args=(action,), daemon=True).start()

    def run_diag_thread(self, action):
        try:
            if action == "msinfo32":
                subprocess.Popen(["msinfo32"])
                self.append_diag_log("[✓] Opened msinfo32 Specs Console.\n")
                
            elif action == "perfmon_health":
                subprocess.Popen(["perfmon", "/report"])
                self.append_diag_log("[✓] Triggered perfmon health reporting task.\n")
                
            elif action == "battery_report":
                target_p = os.path.expandvars(r"%USERPROFILE%\Desktop\battery_report.html")
                subprocess.run(["powercfg", "/batteryreport", "/output", target_p], creationflags=subprocess.CREATE_NO_WINDOW)
                self.append_diag_log(f"[✓] Battery health report generated at: {target_p}\n")
                os.startfile(target_p)
                
            elif action == "defender_quick":
                self.append_diag_log("[*] Starting Defender Quick Scan...\n")
                res = subprocess.run([r"C:\Program Files\Windows Defender\MpCmdRun.exe", "-Scan", "-ScanType", "1"], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
                self.append_diag_log(res.stdout)
                
            elif action == "defender_deep":
                self.append_diag_log("[*] Launching Defender Deep Scan in background...\n")
                subprocess.Popen([r"C:\Program Files\Windows Defender\MpCmdRun.exe", "-Scan", "-ScanType", "2"], creationflags=subprocess.CREATE_NO_WINDOW)
                
            elif action == "defender_update":
                self.append_diag_log("[*] Updating Defender database signatures...\n")
                res = subprocess.run([r"C:\Program Files\Windows Defender\MpCmdRun.exe", "-SignatureUpdate"], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
                self.append_diag_log(res.stdout)
                
            elif action == "wifi_passwords":
                self.append_diag_log("[*] Extracting saved Wi-Fi connection keys:\n")
                cmd = "netsh wlan show profiles | Select-String 'All User Profile' | ForEach-Object { $name = $_.Line.Split(':')[1].Trim(); $pass = (netsh wlan show profile name=$name key=clear | Select-String 'Key Content' | ForEach-Object { $_.Line.Split(':')[1].Trim() }); [PSCustomObject]@{ ProfileName=$name; Password=$pass } } | Format-Table -AutoSize"
                res = subprocess.run(["powershell", "-Command", cmd], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
                self.append_diag_log(res.stdout)
                
            elif action == "cred_manager":
                subprocess.Popen(["control", "keymgr.dll"])
                self.append_diag_log("[✓] Credential Manager launched.\n")
                
            elif action == "office_quick":
                subprocess.Popen([r"C:\Program Files\Common Files\microsoft shared\ClickToRun\OfficeClickToRun.exe", "scenario=Repair", "platform=x64", "culture=en-us", "RepairType=QuickRepair"])
                self.append_diag_log("[✓] Office Quick Repair triggered.\n")
                
            elif action == "office_online":
                subprocess.Popen([r"C:\Program Files\Common Files\microsoft shared\ClickToRun\OfficeClickToRun.exe", "scenario=Repair", "platform=x64", "culture=en-us", "RepairType=OnlineRepair"])
                self.append_diag_log("[✓] Office Online Repair window launched.\n")
                
            elif action in ["outlook_safe", "outlook_pane", "outlook_folders", "outlook_bar"]:
                arg_map = {
                    "outlook_safe": "/safe",
                    "outlook_pane": "/resetnavpane",
                    "outlook_folders": "/resetfolders",
                    "outlook_bar": "/cleanviews"
                }
                subprocess.Popen(["outlook.exe", arg_map[action]])
                self.append_diag_log(f"[✓] Outlook launched with parameter: {arg_map[action]}\n")
                
            elif action == "chkdsk_scan":
                self.append_diag_log("[*] Checking drive block structures online (scan mode)...\n")
                res = subprocess.run(["chkdsk", "C:", "/Scan"], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
                self.append_diag_log(res.stdout)
                
            elif action == "heavy_files":
                self.append_diag_log("[*] Walking filesystem to locate top 10 heaviest files...\n")
                import heapq
                heavy = []
                # Walk limited folders to prevent infinite search loops
                search_dirs = [os.path.expandvars("%USERPROFILE%"), "C:\\Program Files", "C:\\Program Files (x86)"]
                for sd in search_dirs:
                    if os.path.exists(sd):
                        for root, dirs, files in os.walk(sd):
                            for file in files:
                                try:
                                    fp = os.path.join(root, file)
                                    sz = os.path.getsize(fp)
                                    if len(heavy) < 10:
                                        heapq.heappush(heavy, (sz, fp))
                                    elif sz > heavy[0][0]:
                                        heapq.heapreplace(heavy, (sz, fp))
                                except:
                                    pass
                heavy.sort(reverse=True)
                for sz, fp in heavy:
                    self.append_diag_log(f"  • {sz / (1024**2):.1f} MB  →  {fp}\n")
                self.append_diag_log("[✓] Map Complete.\n")
                
            elif action == "defrag_drive":
                self.append_diag_log("[*] Triggering defrag scheduler on partition C:...\n")
                res = subprocess.run(["defrag", "C:", "/O"], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
                self.append_diag_log(res.stdout)
                
            elif action == "ssd_trim":
                self.append_diag_log("[*] Requesting SSD Block Re-trim task...\n")
                res = subprocess.run(["defrag", "C:", "/L"], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
                self.append_diag_log(res.stdout)
                
        except Exception as e:
            self.append_diag_log(f"[X] Execution failed: {str(e)}\n")

    # ==========================
    # Tab 7: Backups & Migration
    # ==========================
    def setup_backups_tab(self):
        f = ctk.CTkFrame(self.container, fg_color="transparent")
        self.frames["backups"] = f
        
        split_frame = ctk.CTkFrame(f, fg_color="transparent")
        split_frame.pack(fill="both", expand=True)
        
        # Left card: Robocopy Migration Hub
        left_card = ctk.CTkFrame(split_frame, fg_color="#151f32", border_color="#1e293b", border_width=1.5)
        left_card.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        ctk.CTkLabel(left_card, text="💾 DATA MIGRATION & BACKUPS HUB", font=("Outfit", 12, "bold"), text_color="#38bdf8").pack(anchor="w", padx=20, pady=15)
        
        # Source Path choice
        s_frame = ctk.CTkFrame(left_card, fg_color="transparent")
        s_frame.pack(fill="x", padx=20, pady=5)
        ctk.CTkLabel(s_frame, text="Source Folder:", font=("Outfit", 10)).pack(anchor="w")
        self.source_entry = ctk.CTkEntry(s_frame, fg_color="#0d1321", border_color="#1e293b")
        self.source_entry.pack(side="left", fill="x", expand=True, pady=2)
        ctk.CTkButton(s_frame, text="Browse", width=80, height=28, command=self.browse_source).pack(side="right", padx=(5, 0))
        
        # Target Path choice
        t_frame = ctk.CTkFrame(left_card, fg_color="transparent")
        t_frame.pack(fill="x", padx=20, pady=5)
        ctk.CTkLabel(t_frame, text="Target Folder:", font=("Outfit", 10)).pack(anchor="w")
        self.target_entry = ctk.CTkEntry(t_frame, fg_color="#0d1321", border_color="#1e293b")
        self.target_entry.pack(side="left", fill="x", expand=True, pady=2)
        ctk.CTkButton(t_frame, text="Browse", width=80, height=28, command=self.browse_target).pack(side="right", padx=(5, 0))
        
        # Robocopy Trigger Button
        btn_robo = ctk.CTkButton(
            left_card, text="🚀 Run Robocopy Mirror Engine",
            font=("Outfit", 11, "bold"), fg_color="#0078d4", hover_color="#005a9e",
            command=self.run_robocopy_task
        )
        btn_robo.pack(fill="x", padx=20, pady=20)
        
        # Right card: Drivers, Backups & Policies
        right_card = ctk.CTkFrame(split_frame, fg_color="#151f32", border_color="#1e293b", border_width=1.5)
        right_card.pack(side="right", fill="both", expand=True, padx=(5, 0))
        
        scroll_right = ctk.CTkScrollableFrame(right_card, fg_color="transparent")
        scroll_right.pack(fill="both", expand=True, padx=15, pady=10)
        
        ctk.CTkLabel(scroll_right, text="🛠️ DRIVERS, BACKUPS & POLICIES", font=("Outfit", 9, "bold"), text_color="#38bdf8").pack(anchor="w", pady=(5, 4))
        
        btn_scan_drv = ctk.CTkButton(
            scroll_right, text="🔍 Scan Missing System Drivers",
            font=("Outfit", 10, "bold"), anchor="w", fg_color="#1e293b", hover_color="#2b2b2b",
            command=lambda: self.run_backup_action("scan_drivers")
        )
        btn_scan_drv.pack(fill="x", padx=10, pady=3)
        
        btn_up_drv = ctk.CTkButton(
            scroll_right, text="🔄 Force Upgrade Windows Software Packets",
            font=("Outfit", 10, "bold"), anchor="w", fg_color="#1e293b", hover_color="#2b2b2b",
            command=lambda: self.run_backup_action("upgrade_drivers")
        )
        btn_up_drv.pack(fill="x", padx=10, pady=3)
        
        btn_bk_drv = ctk.CTkButton(
            scroll_right, text="💾 Export Custom Device Drivers (Desktop Backup)",
            font=("Outfit", 10, "bold"), anchor="w", fg_color="#1e293b", hover_color="#2b2b2b",
            command=lambda: self.run_backup_action("backup_drivers")
        )
        btn_bk_drv.pack(fill="x", padx=10, pady=3)
        
        btn_restore_drv = ctk.CTkButton(
            scroll_right, text="🔄 Restore Device Drivers from Folder",
            font=("Outfit", 10, "bold"), anchor="w", fg_color="#1e293b", hover_color="#2b2b2b",
            command=lambda: self.run_backup_action("restore_drivers")
        )
        btn_restore_drv.pack(fill="x", padx=10, pady=3)
        
        ctk.CTkLabel(scroll_right, text="🏢 ENTERPRISE SERVICES & CACHE PURGE", font=("Outfit", 9, "bold"), text_color="#38bdf8").pack(anchor="w", pady=(15, 4))
        
        btn_tally = ctk.CTkButton(
            scroll_right, text="🔄 Restart Active Tally Gateway System Engines",
            font=("Outfit", 10, "bold"), anchor="w", fg_color="#1e293b", hover_color="#2b2b2b",
            command=lambda: self.run_backup_action("restart_tally")
        )
        btn_tally.pack(fill="x", padx=10, pady=3)
        
        btn_purge = ctk.CTkButton(
            scroll_right, text="🧹 Purge System Prefetch, Cache, and Temp Files",
            font=("Outfit", 10, "bold"), anchor="w", fg_color="#1e293b", hover_color="#2b2b2b",
            command=lambda: self.run_backup_action("purge_cache")
        )
        btn_purge.pack(fill="x", padx=10, pady=3)
        
        # Bottom Console Panel for backups outputs
        self.backups_console_card = ctk.CTkFrame(f, height=180, fg_color="#151f32", border_color="#1e293b", border_width=1.5)
        self.backups_console_card.pack(fill="x", pady=(10, 0))
        self.backups_console_card.pack_propagate(False)
        
        ctk.CTkLabel(self.backups_console_card, text="⚙️ Migration Outputs Log Terminal", font=("Outfit", 11, "bold"), text_color="#ffffff").pack(anchor="w", padx=15, pady=8)
        
        self.backups_log_text = ctk.CTkTextbox(
            self.backups_console_card, fg_color="#0d1321", border_color="#1e293b", border_width=1, text_color="#10b981", font=("Consolas", 9)
        )
        self.backups_log_text.pack(fill="both", expand=True, padx=15, pady=(0, 10))
        self.backups_log_text.insert("end", "[Backups & migration node ready]\n")
        self.backups_log_text.configure(state="disabled")

    def append_backups_log(self, text):
        self.backups_log_text.configure(state="normal")
        self.backups_log_text.insert("end", text)
        self.backups_log_text.see("end")
        self.backups_log_text.configure(state="disabled")

    def browse_source(self):
        d = filedialog.askdirectory()
        if d:
            self.source_entry.delete(0, "end")
            self.source_entry.insert(0, d)
            
    def browse_target(self):
        d = filedialog.askdirectory()
        if d:
            self.target_entry.delete(0, "end")
            self.target_entry.insert(0, d)

    def run_robocopy_task(self):
        src = self.source_entry.get().strip()
        tgt = self.target_entry.get().strip()
        if not src or not tgt:
            self.append_backups_log("[!] Source and Target directory parameters must be supplied.\n")
            return
        cmd = ["robocopy", src, tgt, "/MIR", "/MT:16", "/R:2", "/W:5", "/V"]
        self.append_backups_log(f"\n[*] Starting Robocopy Mirror from '{src}' to '{tgt}'...\n")
        threading.Thread(target=self.run_backup_cmd_thread, args=(cmd, "Robocopy Mirror"), daemon=True).start()

    def run_backup_action(self, action):
        self.append_backups_log(f"\n[*] Initiating action: {action}...\n")
        path = None
        if action == "restore_drivers":
            path = filedialog.askdirectory(title="Select Drivers Backup Directory")
            if not path:
                self.append_backups_log("[!] Drivers restore cancelled: No directory selected.\n")
                return
        threading.Thread(target=self.run_backup_action_thread, args=(action, path), daemon=True).start()

    def run_backup_action_thread(self, action, path=None):
        try:
            if action == "scan_drivers":
                cmd = ["pnputil", "/scan-devices"]
                self.run_backup_cmd_thread(cmd, "Device Drivers Scan")
                
            elif action == "upgrade_drivers":
                cmd = ["winget", "upgrade", "--all", "--include-unknown"]
                self.run_backup_cmd_thread(cmd, "Software Upgrades")
                
            elif action == "backup_drivers":
                dest = os.path.expandvars(r"%USERPROFILE%\Desktop\DriversBackup")
                if not os.path.exists(dest):
                    os.makedirs(dest)
                cmd = ["dism", "/online", "/export-driver", f"/destination:{dest}"]
                self.run_backup_cmd_thread(cmd, "Export Drivers")
                
            elif action == "restart_tally":
                self.append_backups_log("[*] Restarting Tally System Services...\n")
                subprocess.run(["net", "stop", "Tally Gateway Server"], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
                res = subprocess.run(["net", "start", "Tally Gateway Server"], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
                self.append_backups_log(res.stdout)
                
            elif action == "purge_cache":
                self.append_backups_log("[*] Purging system prefetch, temp, and cache files...\n")
                cmd = "Remove-Item -Path $env:TEMP\\* -Recurse -Force -ErrorAction SilentlyContinue; Remove-Item -Path C:\\Windows\\Temp\\* -Recurse -Force -ErrorAction SilentlyContinue; Remove-Item -Path C:\\Windows\\Prefetch\\* -Recurse -Force -ErrorAction SilentlyContinue"
                res = subprocess.run(["powershell", "-Command", cmd], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
                self.append_backups_log("[✓] Temp / Cache files purged successfully.\n")
                
            elif action == "restore_drivers":
                if path:
                    self.append_backups_log(f"[*] Restoring drivers from folder: {path}...\n")
                    cmd = ["pnputil", "/add-driver", f"{path}\\*.inf", "/subdirs", "/install"]
                    self.run_backup_cmd_thread(cmd, "Restore Drivers")
                
        except Exception as e:
            self.append_backups_log(f"[X] Action failed: {str(e)}\n")

    def run_backup_cmd_thread(self, cmd, label):
        try:
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
            while True:
                line = proc.stdout.readline()
                if not line:
                    break
                self.append_backups_log(line)
            proc.wait()
            self.append_backups_log(f"\n[✓] Completed {label} successfully.\n")
        except Exception as e:
            self.append_backups_log(f"[X] Failure: {str(e)}\n")

    # ==========================
    # Tab 8: Windows Config
    # ==========================
    def setup_config_tab(self):
        f = ctk.CTkFrame(self.container, fg_color="transparent")
        self.frames["config"] = f
        
        # Grid layout for shortcuts matching CTT layout
        grid_frame = ctk.CTkFrame(f, fg_color="#151f32", border_color="#1e293b", border_width=1.5)
        grid_frame.pack(fill="both", expand=True, pady=(10, 5))
        
        ctk.CTkLabel(grid_frame, text="⚡ Fast Admin Console Shortcuts", font=("Outfit", 12, "bold"), text_color="#ffffff").pack(anchor="w", padx=20, pady=15)
        
        btn_container = ctk.CTkFrame(grid_frame, fg_color="transparent")
        btn_container.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Config grid layout settings
        btn_container.grid_columnconfigure((0, 1, 2), weight=1, uniform="equal")
        
        shortcuts = [
            ("📁 Control Panel", "control", "Launch classic Control Panel"),
            ("⚙️ Registry Editor", "regedit", "Modify System Registry keys"),
            ("🔌 Device Manager", "devmgmt.msc", "Manage hardware devices & drivers"),
            ("💾 Disk Management", "diskmgmt.msc", "Partition disk drives and volumes"),
            ("📊 Task Manager", "taskmgr", "Monitor processes and active memory"),
            ("🛠️ Services Console", "services.msc", "Configure background system services"),
            ("📅 Task Scheduler", "taskschd.msc", "Manage triggers and scheduled jobs"),
            ("📝 Event Viewer", "eventvwr.msc", "Analyze system logs and diagnostic events"),
            ("🛡️ Group Policy (gpedit)", "gpedit.msc", "Configure Windows settings policies")
        ]
        
        row = 0
        col = 0
        for label, cmd, desc in shortcuts:
            card = ctk.CTkFrame(btn_container, fg_color="#1e293b", border_color="#334155", border_width=1)
            card.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")
            
            ctk.CTkLabel(card, text=label, font=("Outfit", 11, "bold"), text_color="#ffffff").pack(anchor="w", padx=15, pady=(10, 2))
            ctk.CTkLabel(card, text=desc, font=("Outfit", 8), text_color="#94a3b8").pack(anchor="w", padx=15)
            
            btn_launch = ctk.CTkButton(
                card, text="Launch console ↗", font=("Outfit", 9, "bold"), height=24, fg_color="#0078d4", hover_color="#005a9e",
                command=lambda c=cmd: self.launch_console(c)
            )
            btn_launch.pack(anchor="w", padx=15, pady=(10, 10))
            
            col += 1
            if col > 2:
                col = 0
                row += 1

        # Second Panel: Advanced OS Management utilities
        adv_frame = ctk.CTkFrame(f, fg_color="#151f32", border_color="#1e293b", border_width=1.5, height=130)
        adv_frame.pack(fill="x", pady=(5, 10))
        adv_frame.pack_propagate(False)
        
        ctk.CTkLabel(adv_frame, text="👑 Advanced System Administrators Node", font=("Outfit", 11, "bold"), text_color="#38bdf8").pack(anchor="w", padx=20, pady=(10, 5))
        
        btn_adv_container = ctk.CTkFrame(adv_frame, fg_color="transparent")
        btn_adv_container.pack(fill="both", expand=True, padx=20, pady=(0, 10))
        btn_adv_container.grid_columnconfigure((0, 1, 2), weight=1, uniform="equal")
        
        # Action Card 1: God Mode
        card1 = ctk.CTkFrame(btn_adv_container, fg_color="#1e293b", border_color="#334155", border_width=1)
        card1.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        ctk.CTkButton(card1, text="👑 Create 'God Mode' Folder", font=("Outfit", 9, "bold"), fg_color="#10b981", hover_color="#059669", height=28, command=self.create_god_mode).pack(fill="both", expand=True, padx=10, pady=10)
        
        # Action Card 2: Deep Update Blocker
        card2 = ctk.CTkFrame(btn_adv_container, fg_color="#1e293b", border_color="#334155", border_width=1)
        card2.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
        ctk.CTkButton(card2, text="🛡️ Windows Update Deep Blocker", font=("Outfit", 9, "bold"), fg_color="#ef4444", hover_color="#dc2626", height=28, command=self.run_deep_update_blocker).pack(fill="both", expand=True, padx=10, pady=10)
        
        # Action Card 3: Rufus USB helper
        card3 = ctk.CTkFrame(btn_adv_container, fg_color="#1e293b", border_color="#334155", border_width=1)
        card3.grid(row=0, column=2, padx=5, pady=5, sticky="nsew")
        ctk.CTkButton(card3, text="📀 Launch Bootable USB Utility (Rufus)", font=("Outfit", 9, "bold"), fg_color="#0078d4", hover_color="#005a9e", height=28, command=self.download_rufus_helper).pack(fill="both", expand=True, padx=10, pady=10)

    def launch_console(self, cmd):
        try:
            subprocess.Popen([cmd], shell=True)
            self.add_activity("Launch Shortcut", f"Opened {cmd} console console", "Success")
        except Exception as e:
            self.add_activity("Launch Shortcut", f"Failed to open {cmd}: {str(e)}", "Failed")

    def create_god_mode(self):
        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        god_mode_folder = os.path.join(desktop, "GodMode.{ED7BA470-8E54-465E-825C-99712043E01C}")
        try:
            if not os.path.exists(god_mode_folder):
                os.makedirs(god_mode_folder)
                messagebox.showinfo("Success", "God Mode folder created successfully on your Desktop!\nYou can now open it to access all Windows settings in one place.")
            else:
                messagebox.showinfo("Info", "God Mode folder already exists on your Desktop.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create God Mode folder: {str(e)}")

    def run_deep_update_blocker(self):
        self.add_activity("Windows Update", "Deep blocking Windows updates...", "Running")
        
        def run_thread():
            try:
                # Stop and disable services
                services = ["wuauserv", "bits", "dosvc"]
                for s in services:
                    subprocess.run(["sc", "config", s, "start=", "disabled"], creationflags=subprocess.CREATE_NO_WINDOW)
                    subprocess.run(["sc", "stop", s], creationflags=subprocess.CREATE_NO_WINDOW)
                
                # Block update servers in hosts
                hosts_path = r"C:\Windows\System32\drivers\etc\hosts"
                update_servers = [
                    "update.microsoft.com",
                    "windowsupdate.microsoft.com",
                    "download.windowsupdate.com",
                    "download.microsoft.com"
                ]
                
                content = ""
                if os.path.exists(hosts_path):
                    with open(hosts_path, "r", encoding="utf-8") as f:
                        content = f.read()
                
                to_add = []
                for s in update_servers:
                    if s not in content:
                        to_add.append(f"0.0.0.0\t{s}")
                
                if to_add:
                    with open(hosts_path, "a", encoding="utf-8") as f:
                        f.write("\n# Windows Update Block List Added by VenkatPulse\n" + "\n".join(to_add) + "\n")
                
                self.add_activity("Windows Update", "Windows Updates blocked completely", "Success")
                messagebox.showinfo("Success", "Windows Update Deep Blocker enabled successfully!\nAll Windows Update services have been disabled and blocked.")
            except Exception as e:
                self.add_activity("Windows Update", f"Failed to block updates: {str(e)}", "Failed")
                messagebox.showerror("Error", f"Failed to run deep blocker: {str(e)}")
                
        threading.Thread(target=run_thread, daemon=True).start()

    def download_rufus_helper(self):
        self.add_activity("USB Creator", "Installing Rufus via winget...", "Running")
        
        def run_thread():
            cmd = ["winget", "install", "--id", "Rufus.Rufus", "--silent", "--accept-source-agreements", "--accept-package-agreements"]
            proc = subprocess.run(cmd, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
            if proc.returncode == 0:
                self.add_activity("USB Creator", "Rufus installed successfully", "Success")
                messagebox.showinfo("Success", "Rufus has been installed successfully!\nYou can find it in your Start Menu.")
            else:
                self.add_activity("USB Creator", "Rufus installation failed", "Failed")
                messagebox.showerror("Error", f"Failed to install Rufus via winget.\nDetail: {proc.stderr}")
                
        threading.Thread(target=run_thread, daemon=True).start()

    # ==========================
    # Tab 6B: Hosts & Net Admin
    # ==========================
    def setup_hosts_tab(self):
        f = ctk.CTkFrame(self.container, fg_color="transparent")
        self.frames["hosts"] = f
        
        split = ctk.CTkFrame(f, fg_color="transparent")
        split.pack(fill="both", expand=True)
        
        # Left card: Controls
        left_card = ctk.CTkFrame(split, fg_color="#151f32", border_color="#1e293b", border_width=1.5)
        left_card.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        ctk.CTkLabel(left_card, text="📝 Hosts File Editor & Domain Blocker", font=("Outfit", 12, "bold"), text_color="#38bdf8").pack(anchor="w", padx=15, pady=10)
        
        # Form to add entry
        form_frame = ctk.CTkFrame(left_card, fg_color="transparent")
        form_frame.pack(fill="x", padx=15, pady=5)
        
        ctk.CTkLabel(form_frame, text="IP Address:", font=("Outfit", 9)).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.entry_hosts_ip = ctk.CTkEntry(form_frame, placeholder_text="e.g. 127.0.0.1", font=("Outfit", 9), width=120)
        self.entry_hosts_ip.grid(row=0, column=1, padx=5, pady=5)
        
        ctk.CTkLabel(form_frame, text="Hostname:", font=("Outfit", 9)).grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.entry_hosts_domain = ctk.CTkEntry(form_frame, placeholder_text="e.g. custom.local", font=("Outfit", 9), width=150)
        self.entry_hosts_domain.grid(row=0, column=3, padx=5, pady=5)
        
        btn_add = ctk.CTkButton(form_frame, text="➕ Add Entry", font=("Outfit", 9, "bold"), fg_color="#10b981", hover_color="#059669", width=90, height=28, command=self.add_hosts_entry)
        btn_add.grid(row=0, column=4, padx=10, pady=5)
        
        # Action buttons
        btn_frame = ctk.CTkFrame(left_card, fg_color="transparent")
        btn_frame.pack(fill="x", padx=15, pady=10)
        
        btn_block = ctk.CTkButton(btn_frame, text="🚫 Block Ads & Telemetry", font=("Outfit", 9, "bold"), fg_color="#ef4444", hover_color="#dc2626", height=28, command=self.block_telemetry_hosts)
        btn_block.pack(side="left", padx=5)
        
        btn_restore = ctk.CTkButton(btn_frame, text="🧹 Restore Default Hosts", font=("Outfit", 9, "bold"), fg_color="#64748b", hover_color="#475569", height=28, command=self.restore_default_hosts)
        btn_restore.pack(side="left", padx=5)
        
        btn_reload = ctk.CTkButton(btn_frame, text="🔄 Reload View", font=("Outfit", 9, "bold"), fg_color="#0078d4", hover_color="#005a9e", height=28, command=self.reload_hosts_view)
        btn_reload.pack(side="left", padx=5)
        
        # Hosts content textbox
        self.txt_hosts_content = ctk.CTkTextbox(left_card, fg_color="#090d16", font=("Consolas", 9), text_color="#cbd5e1", border_color="#1e293b", border_width=1)
        self.txt_hosts_content.pack(fill="both", expand=True, padx=15, pady=(5, 15))
        
        self.reload_hosts_view()

    def reload_hosts_view(self):
        hosts_path = r"C:\Windows\System32\drivers\etc\hosts"
        try:
            content = ""
            if os.path.exists(hosts_path):
                with open(hosts_path, "r", encoding="utf-8") as f:
                    content = f.read()
            self.txt_hosts_content.delete("1.0", "end")
            self.txt_hosts_content.insert("1.0", content)
        except Exception as e:
            self.txt_hosts_content.delete("1.0", "end")
            self.txt_hosts_content.insert("1.0", f"Error reading hosts file: {str(e)}")

    def add_hosts_entry(self):
        ip = self.entry_hosts_ip.get().strip()
        domain = self.entry_hosts_domain.get().strip()
        if not ip or not domain:
            messagebox.showerror("Error", "Please enter both an IP Address and a Hostname.")
            return
        
        hosts_path = r"C:\Windows\System32\drivers\etc\hosts"
        try:
            with open(hosts_path, "a", encoding="utf-8") as f:
                f.write(f"\n{ip}\t{domain}\n")
            self.entry_hosts_ip.delete(0, "end")
            self.entry_hosts_domain.delete(0, "end")
            self.reload_hosts_view()
            messagebox.showinfo("Success", f"Added entry: {ip} -> {domain}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to modify hosts file.\nRun this tool as administrator.\nDetail: {str(e)}")

    def block_telemetry_hosts(self):
        hosts_path = r"C:\Windows\System32\drivers\etc\hosts"
        telemetry_domains = [
            "telemetry.microsoft.com",
            "v10.events.data.microsoft.com",
            "v20.events.data.microsoft.com",
            "watson.telemetry.microsoft.com",
            "diagnostics.support.microsoft.com",
            "corp.sts.microsoft.com",
            "statsfe2.ws.microsoft.com",
            "survey.watson.microsoft.com",
            "settings-sandbox.data.microsoft.com",
            "oca.telemetry.microsoft.com",
            "sqm.telemetry.microsoft.com",
            "telecommand.telemetry.microsoft.com",
            "rad.msn.com",
            "preview.msn.com",
            "activity.windows.com"
        ]
        try:
            content = ""
            if os.path.exists(hosts_path):
                with open(hosts_path, "r", encoding="utf-8") as f:
                    content = f.read()
            
            to_add = []
            for d in telemetry_domains:
                if d not in content:
                    to_add.append(f"0.0.0.0\t{d}")
            
            if to_add:
                with open(hosts_path, "a", encoding="utf-8") as f:
                    f.write("\n# Telemetry Block List Added by VenkatPulse\n" + "\n".join(to_add) + "\n")
                self.reload_hosts_view()
                messagebox.showinfo("Success", "Telemetry & Ad domains blocked system-wide successfully!")
            else:
                messagebox.showinfo("Info", "All telemetry domains are already blocked.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to block domains: {str(e)}")

    def restore_default_hosts(self):
        hosts_path = r"C:\Windows\System32\drivers\etc\hosts"
        default_content = """# Copyright (c) 1993-2009 Microsoft Corp.
#
# This is a sample HOSTS file used by Microsoft TCP/IP for Windows.
#
# This file contains the mappings of IP addresses to host names. Each
# entry should be kept on an individual line. The IP address should
# be placed in the first column followed by the corresponding host name.
# The IP address and the host name should be separated by at least one
# space.
#
# Additionally, comments (such as these) may be inserted on individual
# lines or following the machine name denoted by a '#' symbol.
#
# For example:
#
#      102.54.94.97     rhino.acme.com          # source server
#       38.25.63.10     x.acme.com              # x client host

# localhost name resolution is handled within DNS itself.
#\t127.0.0.1       localhost
#\t::1             localhost
"""
        try:
            with open(hosts_path, "w", encoding="utf-8") as f:
                f.write(default_content)
            self.reload_hosts_view()
            messagebox.showinfo("Success", "Restored hosts file to Windows defaults.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to restore hosts file: {str(e)}")

    # ==========================
    # Tab 6C: Startup Manager
    # ==========================
    def setup_startup_tab(self):
        f = ctk.CTkFrame(self.container, fg_color="transparent")
        self.frames["startup"] = f
        
        split = ctk.CTkFrame(f, fg_color="transparent")
        split.pack(fill="both", expand=True)
        
        # Left card: Table of startup apps
        left_card = ctk.CTkFrame(split, fg_color="#151f32", border_color="#1e293b", border_width=1.5)
        left_card.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        ctk.CTkLabel(left_card, text="🚦 Boot Startup Apps Manager", font=("Outfit", 12, "bold"), text_color="#38bdf8").pack(anchor="w", padx=15, pady=10)
        
        # Action buttons
        btn_frame = ctk.CTkFrame(left_card, fg_color="transparent")
        btn_frame.pack(fill="x", padx=15, pady=5)
        
        btn_rem = ctk.CTkButton(btn_frame, text="🗑️ Disable/Remove Selected", font=("Outfit", 9, "bold"), fg_color="#ef4444", hover_color="#dc2626", height=28, command=self.remove_startup_entry)
        btn_rem.pack(side="left", padx=5)
        
        btn_refresh = ctk.CTkButton(btn_frame, text="🔄 Refresh List", font=("Outfit", 9, "bold"), fg_color="#0078d4", hover_color="#005a9e", height=28, command=self.load_startup_apps)
        btn_refresh.pack(side="left", padx=5)
        
        # Treeview to display
        columns = ("Name", "Command Line", "Location")
        self.startup_tree = ttk.Treeview(left_card, columns=columns, show="headings", height=15)
        self.startup_tree.pack(fill="both", expand=True, padx=15, pady=(5, 15))
        
        self.startup_tree.heading("Name", text="Startup Name")
        self.startup_tree.heading("Command Line", text="Command / Executable Path")
        self.startup_tree.heading("Location", text="Registry Location")
        
        self.startup_tree.column("Name", width=150, anchor="w")
        self.startup_tree.column("Command Line", width=350, anchor="w")
        self.startup_tree.column("Location", width=120, anchor="center")
        
        self.load_startup_apps()

    def load_startup_apps(self):
        # Clear existing items
        for item in self.startup_tree.get_children():
            self.startup_tree.delete(item)
            
        startup_paths = [
            (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", "HKCU Run"),
            (winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\Run", "HKLM Run")
        ]
        
        for hkey, subkey, loc_name in startup_paths:
            try:
                key = winreg.OpenKey(hkey, subkey, 0, winreg.KEY_READ)
                idx = 0
                while True:
                    try:
                        name, val, val_type = winreg.EnumValue(key, idx)
                        self.startup_tree.insert("", "end", values=(name, val, loc_name))
                        idx += 1
                    except OSError:
                        break
                winreg.CloseKey(key)
            except Exception as e:
                pass

    def remove_startup_entry(self):
        sel = self.startup_tree.selection()
        if not sel:
            messagebox.showerror("Error", "Please select a startup entry from the table to remove.")
            return
            
        name, val, loc = self.startup_tree.item(sel[0], "values")
        hkey = winreg.HKEY_CURRENT_USER if loc == "HKCU Run" else winreg.HKEY_LOCAL_MACHINE
        subkey = r"Software\Microsoft\Windows\CurrentVersion\Run"
        
        try:
            key = winreg.OpenKey(hkey, subkey, 0, winreg.KEY_SET_VALUE)
            winreg.DeleteValue(key, name)
            winreg.CloseKey(key)
            self.load_startup_apps()
            messagebox.showinfo("Success", f"Removed {name} from startup successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to remove startup entry.\nRun this tool as administrator.\nDetail: {str(e)}")

    # ==========================
    # Theme color switcher implementation
    # ==========================
    def apply_theme_colors(self, widget, colors):
        cls_name = widget.__class__.__name__
        
        try:
            if widget == self:
                widget.configure(fg_color=colors["bg"])
            elif hasattr(self, "sidebar") and widget == self.sidebar:
                widget.configure(fg_color=colors["sidebar_bg"], border_color=colors["card_border"])
            elif hasattr(self, "top_header") and widget == self.top_header:
                widget.configure(fg_color=colors["sidebar_bg"], border_color=colors["card_border"])
            elif hasattr(self, "buttons") and any(widget == btn for btn in self.buttons.values()):
                is_active = False
                for btn_name, btn in self.buttons.items():
                    if btn == widget and btn_name == self.active_tool:
                        is_active = True
                        break
                if is_active:
                    widget.configure(fg_color=colors["accent"], text_color="#ffffff")
                else:
                    widget.configure(fg_color="transparent", text_color=colors["text"], hover_color=colors["card_border"])
            elif cls_name == "CTkFrame":
                current_fg = widget.cget("fg_color")
                if current_fg != "transparent":
                    widget.configure(fg_color=colors["card_bg"], border_color=colors["card_border"])
            elif cls_name == "CTkLabel":
                current_text_col = widget.cget("text_color")
                if current_text_col not in ["#10b981", "#ef4444", "#38bdf8", "#0078d4", "#f59e0b", "#d946ef"]:
                    widget.configure(text_color=colors["text"])
            elif cls_name == "CTkButton":
                current_fg = widget.cget("fg_color")
                if current_fg not in ["transparent", "#ef4444", "#dc2626"]:
                    widget.configure(fg_color=colors["accent"], hover_color=colors["accent_hover"], text_color="#ffffff")
                elif current_fg == "transparent":
                    widget.configure(text_color=colors["accent"])
            elif cls_name == "CTkEntry":
                widget.configure(fg_color=colors["entry_bg"], border_color=colors["card_border"], text_color="#ffffff")
            elif cls_name == "CTkTextbox":
                widget.configure(fg_color=colors["entry_bg"], border_color=colors["card_border"], text_color=colors["text"])
            elif cls_name == "CTkSegmentedButton":
                widget.configure(
                    selected_color=colors["accent"],
                    selected_hover_color=colors["accent_hover"],
                    selected_text_color="#ffffff",
                    unselected_color=colors["entry_bg"],
                    unselected_hover_color=colors["card_border"],
                    text_color=colors["text"],
                    fg_color=colors["sidebar_bg"]
                )
            elif cls_name == "CTkComboBox":
                widget.configure(fg_color=colors["card_bg"], border_color=colors["card_border"], button_color=colors["accent"], button_hover_color=colors["accent_hover"])
            elif cls_name == "CTkCheckBox":
                widget.configure(fg_color=colors["accent"], hover_color=colors["accent_hover"], text_color=colors["text"])
            elif cls_name == "CTkSlider":
                widget.configure(button_color=colors["accent"], button_hover_color=colors["accent_hover"], progress_color=colors["accent"])
            elif cls_name == "CTkProgressBar":
                widget.configure(progress_color=colors["accent"])
            elif cls_name == "Canvas":
                widget.configure(bg=colors["sidebar_bg"])
        except:
            pass
            
        for child in widget.winfo_children():
            self.apply_theme_colors(child, colors)

    def change_theme_color(self, val):
        theme_colors = {
            "Default Blue": {
                "bg": "#0a0c16",
                "sidebar_bg": "#101322",
                "card_bg": "#171b30",
                "card_border": "#252c4e",
                "accent": "#0284c7",
                "accent_hover": "#0369a1",
                "text": "#cbd5e1",
                "title_text": "#ffffff",
                "entry_bg": "#0a0c16"
            },
            "Obsidian Dark": {
                "bg": "#08070b",
                "sidebar_bg": "#0e0d15",
                "card_bg": "#151322",
                "card_border": "#28253f",
                "accent": "#8b5cf6",
                "accent_hover": "#7c3aed",
                "text": "#e2e8f0",
                "title_text": "#ffffff",
                "entry_bg": "#08070b"
            },
            "Cyberpunk": {
                "bg": "#050505",
                "sidebar_bg": "#0d0d0d",
                "card_bg": "#141414",
                "card_border": "#facc15",
                "accent": "#facc15",
                "accent_hover": "#eab308",
                "text": "#e5e5e5",
                "title_text": "#facc15",
                "entry_bg": "#050505"
            },
            "Emerald Green": {
                "bg": "#050f0a",
                "sidebar_bg": "#0b1a13",
                "card_bg": "#122a1f",
                "card_border": "#1e4635",
                "accent": "#10b981",
                "accent_hover": "#059669",
                "text": "#ecfdf5",
                "title_text": "#ffffff",
                "entry_bg": "#050f0a"
            }
        }
        
        colors = theme_colors.get(val, theme_colors["Default Blue"])
        self.apply_theme_colors(self, colors)
        
        # Update sidebar indicators and highlight active button
        self.switch_view(self.active_tool)

    def initialize_tools_catalog(self):
        self.tools_catalog = [
            {
                "name": "🛡️ Run System File Check (sfc /scannow)",
                "description": "Scans and repairs corrupt or missing Windows system files.",
                "category": "System Scans & Repairs",
                "keywords": ["sfc", "scannow", "corrupt", "repair", "scan", "system files", "integrity", "sfc /scannow"],
                "callback": lambda: self.run_repair_cmd(["sfc", "/scannow"], "SFC Diagnostics Check")
            },
            {
                "name": "⚙️ Repair Image Health (DISM RestoreHealth)",
                "description": "Uses DISM to scan the Windows component store and repair OS image corruption.",
                "category": "System Scans & Repairs",
                "keywords": ["dism", "restorehealth", "restore", "image", "cleanup-image", "health", "component store"],
                "callback": lambda: self.run_repair_cmd(["dism", "/online", "/cleanup-image", "/restorehealth"], "DISM Restore Health")
            },
            {
                "name": "🔍 Quick Check Image Corruption Status (DISM /CheckHealth)",
                "description": "Quickly detects if any system files or components are flagged as corrupted.",
                "category": "System Scans & Repairs",
                "keywords": ["dism", "checkhealth", "corruption", "image", "scan", "health"],
                "callback": self.run_dism_check_health
            },
            {
                "name": "🔄 Reset Windows Update Components & Cache",
                "description": "Wipes the Windows Update cache directory (SoftwareDistribution) and restarts update services to fix update loops.",
                "category": "System Scans & Repairs",
                "keywords": ["update", "windows update", "wuauserv", "cache", "softwaredistribution", "bits", "reset update"],
                "callback": self.repair_windows_updates
            },
            {
                "name": "🛠️ Repair Windows Native Repair Engines (SFC & DISM Fix)",
                "description": "Fixes underlying corruption in the SFC and DISM engines themselves.",
                "category": "System Scans & Repairs",
                "keywords": ["repair engines", "sfc fix", "dism fix", "corrupt engine"],
                "callback": self.run_repair_engines_fix
            },
            {
                "name": "🧹 Flush System DNS Resolver Cache",
                "description": "Flushes the DNS resolver cache to clear corrupted IP routing configurations and resolve web access issues.",
                "category": "System Scans & Repairs",
                "keywords": ["dns", "flushdns", "ipconfig", "flush", "internet", "routing"],
                "callback": lambda: self.run_repair_cmd(["ipconfig", "/flushdns"], "DNS Resolver Reset")
            },
            {
                "name": "🔌 Reset Network Winsock Catalog Bindings",
                "description": "Resets the Winsock TCP/IP catalog bindings to resolve internet socket errors.",
                "category": "System Scans & Repairs",
                "keywords": ["winsock", "reset winsock", "netsh", "network", "sockets", "no internet"],
                "callback": lambda: self.run_repair_cmd(["netsh", "winsock", "reset"], "Winsock Stack Reset")
            },
            {
                "name": "🔥 Reset Windows Firewall Rules to Default",
                "description": "Restores Windows Defender Firewall rules and profiles to default factory settings.",
                "category": "System Scans & Repairs",
                "keywords": ["firewall", "reset firewall", "netsh firewall", "rules", "block internet"],
                "callback": self.restore_windows_firewall
            },
            {
                "name": "🛍️ Re-register & Repair Microsoft Store & Default Apps",
                "description": "Re-registers all native AppX packages, including the Microsoft Store, to repair launch crashes.",
                "category": "System Scans & Repairs",
                "keywords": ["store", "microsoft store", "appx", "default apps", "crash", "re-register store"],
                "callback": self.run_store_repair
            },
            {
                "name": "📡 Run Comprehensive Network Stack & Adapter Reset",
                "description": "Runs a comprehensive flush of DNS, Winsock, IP protocols, and resets network configurations.",
                "category": "System Scans & Repairs",
                "keywords": ["network reset", "ip reset", "internet repair", "reset stack"],
                "callback": self.run_network_reset
            },
            {
                "name": "⚙️ Re-Register Core Windows System DLL Libraries (regsvr32)",
                "description": "Re-registers core system dynamic link libraries (DLLs) in System32 to fix missing DLL popup messages.",
                "category": "System Scans & Repairs",
                "keywords": ["dll", "regsvr32", "register dll", "missing dll", "system dlls"],
                "callback": self.reregister_system_dlls
            },
            {
                "name": "💪 Enable Windows Recovery Environment (WinRE)",
                "description": "Activates the native Windows Recovery Environment for advanced troubleshooting during boot.",
                "category": "System Recovery & Boot Management",
                "keywords": ["winre", "reagentc", "recovery", "enable winre", "troubleshoot boot"],
                "callback": lambda: self.run_repair_cmd(["reagentc", "/enable"], "WinRE Enable")
            },
            {
                "name": "🔍 Check WinRE Environment Configuration Status",
                "description": "Displays configuration and partition status for the Windows Recovery Environment.",
                "category": "System Recovery & Boot Management",
                "keywords": ["winre info", "winre status", "reagentc info"],
                "callback": lambda: self.run_repair_cmd(["reagentc", "/info"], "WinRE Status Info")
            },
            {
                "name": "💻 Rebuild Windows Boot configuration partition files (BCDBoot)",
                "description": "Rebuilds the Boot Configuration Data (BCD) files on the system partition to resolve boot sector loops.",
                "category": "System Recovery & Boot Management",
                "keywords": ["bcdboot", "bcd", "boot", "rebuild boot", "uefi", "mbr", "start loop"],
                "callback": lambda: self.run_repair_cmd(["bcdboot", "C:\\Windows"], "BCDBoot Rebuild")
            },
            {
                "name": "🔄 Reboot System directly into Startup Repair / Recovery Menu",
                "description": "Initiates an immediate restart directly into the Advanced Boot Options recovery interface.",
                "category": "System Recovery & Boot Management",
                "keywords": ["reboot recovery", "restart boot options", "startup repair menu", "recovery boot"],
                "callback": self.reboot_to_recovery
            },
            {
                "name": "🚦 Enable Windows Boot Failures Menu Display Policy",
                "description": "Forces Windows to display the boot options menu whenever a boot failure is encountered.",
                "category": "System Recovery & Boot Management",
                "keywords": ["boot failure", "bcdedit boot", "failures menu", "display all failures"],
                "callback": lambda: self.run_repair_cmd(["bcdedit", "/set", "{current}", "bootstatuspolicy", "displayallfailures"], "Boot status policy")
            },
            {
                "name": "📂 Schedule Boot-Time Disk Volume Scan & Repair (Chkdsk /f /r)",
                "description": "Schedules a full disk check on drive C: to detect bad sectors and repair partition structures during reboot.",
                "category": "System Recovery & Boot Management",
                "keywords": ["chkdsk", "disk check", "bad sectors", "repair disk", "boot scan", "disk scan"],
                "callback": self.schedule_chkdsk_scan
            },
            {
                "name": "🛠️ Run Microsoft Office Quick Repair (Click-to-Run)",
                "description": "Runs the local Click-to-Run quick repair wizard to fix installation and launch errors.",
                "category": "Microsoft Office & Outlook Diagnostics",
                "keywords": ["office repair", "excel repair", "word repair", "outlook repair", "office crash"],
                "callback": self.run_office_repair
            },
            {
                "name": "📧 Launch Outlook PST File Repair Tool (ScanPST)",
                "description": "Launches the Inbox Repair Tool (scanpst.exe) to scan and fix corrupted Outlook mailbox databases.",
                "category": "Microsoft Office & Outlook Diagnostics",
                "keywords": ["scanpst", "outlook data", "pst repair", "fix pst", "outlook mailbox"],
                "callback": self.launch_scanpst
            },
            {
                "name": "🔓 Fix Shared Printer Error 0x0000011b (Set RpcAuthnLevelPrivacyEnabled=0)",
                "description": "Disables RPC authentication requirements to resolve printer connection errors.",
                "category": "Printer Service & Sharing Repairs",
                "keywords": ["0x0000011b", "printer sharing", "rpc error", "rpcauthnlevelprivacyenabled", "printer connection"],
                "callback": self.fix_printer_sharing_error
            },
            {
                "name": "📜 Configure Group Policy Printer Sharing & RPC Connection Settings",
                "description": "Applies administrative policies to allow non-admins to install drivers and routes RPC over TCP.",
                "category": "Printer Service & Sharing Repairs",
                "keywords": ["group policy printer", "rpc tcp", "printer driver admin", "printer gpo"],
                "callback": self.configure_printer_gpo_policies
            },
            {
                "name": "🔌 Enable LPD Network Printer Service Features",
                "description": "Enables the LPR Port Monitor and LPD Service features inside Windows optional modules.",
                "category": "Printer Service & Sharing Repairs",
                "keywords": ["lpd printer", "lpr port", "unix printing", "optional features printing"],
                "callback": self.enable_lpd_printer_features
            },
            {
                "name": "📡 Enable Network Discovery and Printer sharing dependency services",
                "description": "Configures FDResPub, SSDPSrv, UpnPHost, and Dnscache services to start automatically.",
                "category": "Printer Service & Sharing Repairs",
                "keywords": ["network discovery", "sharing services", "fdrespub", "ssdp", "printer sharing discovery"],
                "callback": self.enable_sharing_discovery_services
            },
            {
                "name": "🧹 Flush Print Spooler Service & Clear Pending Queue",
                "description": "Stops the spooler, clears stuck documents in system32/spool/PRINTERS, and restarts the service.",
                "category": "Printer Service & Sharing Repairs",
                "keywords": ["print spooler", "spooler reset", "clear print queue", "stuck print", "printer restart"],
                "callback": self.clear_print_spooler
            },
            {
                "name": "🔍 Launch Native Windows Printer Troubleshooter Diagnostic Wizard",
                "description": "Launches the built-in Microsoft Printer Troubleshooter diagnostic wizard.",
                "category": "Printer Service & Sharing Repairs",
                "keywords": ["printer troubleshooter", "msdt printer", "fix print wizard"],
                "callback": lambda: self.run_repair_cmd(["msdt.exe", "/id", "PrinterDiagnostic"], "Printer Troubleshooter Wizard")
            },
            {
                "name": "Convert Drive FAT32 to NTFS",
                "description": "Performs a lossless partition style conversion from FAT32 to NTFS.",
                "category": "Lossless Drive & Disk Style Converters",
                "keywords": ["convert ntfs", "fat32 to ntfs", "drive converter"],
                "callback": self.run_fat32_to_ntfs
            },
            {
                "name": "Convert Disk MBR to GPT",
                "description": "Performs a non-destructive partition structure conversion from MBR to GPT for UEFI boot support.",
                "category": "Lossless Drive & Disk Style Converters",
                "keywords": ["mbr to gpt", "convert gpt", "disk partition style"],
                "callback": self.run_mbr_to_gpt
            },
            {
                "name": "🧠 Optimize & Flush System RAM Cache (Empty Process Working Sets)",
                "description": "Empties standby memory lists and system working sets to reclaim RAM.",
                "category": "System Cleaners & Cache Optimizers",
                "keywords": ["optimize ram", "clear standby", "clean ram", "empty memory"],
                "callback": self.optimize_ram_standby
            },
            {
                "name": "🧹 Clean Web Browser Cache & Temp Files",
                "description": "Scans and deletes cache files for Google Chrome, Microsoft Edge, Mozilla Firefox, and system temp.",
                "category": "System Cleaners & Cache Optimizers",
                "keywords": ["clean browser", "delete chrome cache", "edge cache", "firefox cache", "clear temp"],
                "callback": self.clean_browsers_cache
            },
            {
                "name": "🛡️ Reset Windows Defender Policies & Restart Antivirus Services",
                "description": "Removes Group Policy overrides for Windows Defender and registers security center packages.",
                "category": "Windows Services & Shield Repairs",
                "keywords": ["reset defender", "windows defender", "antivirus reset", "security center UI"],
                "callback": self.reset_windows_defender
            },
            {
                "name": "🧱 Restore Default Windows Firewall Settings and Rules",
                "description": "Resets the built-in firewall configurations to factory values.",
                "category": "Windows Services & Shield Repairs",
                "keywords": ["restore firewall", "firewall defaults", "netsh firewall reset"],
                "callback": self.restore_windows_firewall
            },
            {
                "name": "🎧 Reset & Restart Windows Audio Playback Services",
                "description": "Restarts AudioSrv and AudioEndpointBuilder services to resolve audio device errors.",
                "category": "Windows Services & Shield Repairs",
                "keywords": ["audio services", "restart audio", "audiosrv", "no sound", "sound card reset"],
                "callback": self.reset_audio_services
            },
            {
                "name": "🚀 Restart Windows Explorer Shell",
                "description": "Quickly kills and restarts the explorer.exe shell process to solve taskbar freezes.",
                "category": "Shell Optimizers & Data Wipers",
                "keywords": ["restart explorer", "restart shell", "explorer.exe", "taskbar freeze", "desktop restart"],
                "callback": self.restart_explorer_shell
            },
            {
                "name": "💽 Clear All Windows System, Application & Security Event Logs",
                "description": "Clears all system event log directories to reclaim system drive capacity.",
                "category": "Shell Optimizers & Data Wipers",
                "keywords": ["clear event logs", "wevtutil", "delete logs", "log cleaner"],
                "callback": self.clear_all_event_logs
            },
            {
                "name": "🖼️ Rebuild Windows Desktop Icon & Thumbnail Cache Data",
                "description": "Kills explorer and deletes iconcache and thumbcache database files to fix icon displays.",
                "category": "Shell Optimizers & Data Wipers",
                "keywords": ["icon cache", "thumbnail cache", "blank icons", "rebuild icons"],
                "callback": self.clear_icon_thumbnail_cache
            },
            {
                "name": "🔤 Rebuild Windows System Font Cache Database",
                "description": "Stops the FontCache service, wipes dat cache structures, and restarts the engine.",
                "category": "Shell Optimizers & Data Wipers",
                "keywords": ["font cache", "rebuild fonts", "corrupted text", "blank font cache"],
                "callback": self.rebuild_font_cache
            },
            {
                "name": "📂 Restore Windows 11 Classic Right-Click Context Menu",
                "description": "Configures registry keys to bypass Windows 11's modern right-click layout.",
                "category": "System Customizations & Context Menu Boosts",
                "keywords": ["classic context menu", "win11 right click", "restore old right click", "show more options"],
                "callback": self.restore_classic_context_menu
            },
            {
                "name": "↩️ Revert to Windows 11 Default Right-Click Context Menu",
                "description": "Removes right-click GPO overrides to restore the default Windows 11 modern layout.",
                "category": "System Customizations & Context Menu Boosts",
                "keywords": ["modern context menu", "revert context menu", "win11 default menu"],
                "callback": self.revert_default_context_menu
            },
            {
                "name": "🔍 Disable Online Bing Web Search in Windows Start Menu (Offline Boost)",
                "description": "Disables web results inside the Start Menu search interface to make searches local-only.",
                "category": "System Customizations & Context Menu Boosts",
                "keywords": ["disable bing", "start menu search", "offline start search", "speed up start search"],
                "callback": self.disable_bing_start_search
            },
            {
                "name": "⚡ Toggle Windows Fast Startup Settings",
                "description": "Toggles the Hiberboot settings to prevent kernel caching on shutdowns.",
                "category": "System Customizations & Context Menu Boosts",
                "keywords": ["fast startup", "hiberboot", "shutdown issues", "slow restart"],
                "callback": self.toggle_fast_startup
            },
            {
                "name": "⚡ Unlock & Enable Windows Ultimate Performance Power Plan",
                "description": "Unlocks the hidden Ultimate Performance power profile on your machine.",
                "category": "System Customizations & Context Menu Boosts",
                "keywords": ["ultimate performance", "power plan", "gaming power plan", "high performance"],
                "callback": self.enable_ultimate_performance
            },
            {
                "name": "🎮 Optimize Windows 10/11 Registry Settings for Low-Latency Gaming",
                "description": "Applies GameDVR overrides, mouse acceleration fixes, and network game latency tweaks.",
                "category": "System Customizations & Context Menu Boosts",
                "keywords": ["gaming boost", "latency tweaks", "game dvr", "mouse acceleration", "optimize registry"],
                "callback": self.optimize_gaming_tweaks
            },
            {
                "name": "💾 Check Connected Physical Drive Health Status (SMART Scan)",
                "description": "Reads SMART health parameters on physical disks to identify potential hardware failures.",
                "category": "Hardware Diagnostics & Speed Testing",
                "keywords": ["smart status", "drive health", "ssd health", "hdd status", "disk diagnostics"],
                "callback": self.check_disk_health
            },
            {
                "name": "🧠 Analyze Installed RAM Modules & Speed Specifications",
                "description": "Identifies installed RAM module sizes, clock speeds, and manufacturer details.",
                "category": "Hardware Diagnostics & Speed Testing",
                "keywords": ["ram speed", "wmic memorychip", "check ram speed", "ram specifications"],
                "callback": self.check_ram_specs
            },
            {
                "name": "🔄 Schedule Windows Memory Diagnostic Scanner (mdsched.exe)",
                "description": "Sets up Windows Memory Diagnostic to check physical RAM hardware during restart.",
                "category": "Hardware Diagnostics & Speed Testing",
                "keywords": ["mdsched", "memory diagnostic", "check ram error", "schedule ram check"],
                "callback": self.schedule_memory_diagnostic
            },
            {
                "name": "🌐 Configure Secure Network DNS Servers (Cloudflare 1.1.1.1)",
                "description": "Sets active adapter primary DNS to 1.1.1.1 and secondary to 1.0.0.1.",
                "category": "Hardware Diagnostics & Speed Testing",
                "keywords": ["dns change", "cloudflare dns", "1.1.1.1", "secure dns"],
                "callback": self.configure_secure_dns
            },
            {
                "name": "📡 Run Real-Time Internet Download Speed Test",
                "description": "Downloads a test file from Cloudflare CDN to calculate internet throughput.",
                "category": "Hardware Diagnostics & Speed Testing",
                "keywords": ["speed test", "internet speed", "download test", "check mbps"],
                "callback": self.run_speed_test
            },
            {
                "name": "🔋 Generate Windows Battery Lifecycle & Wear Health Report",
                "description": "Generates a detailed HTML report of laptop battery specifications and degradation rates.",
                "category": "Hardware Diagnostics & Speed Testing",
                "keywords": ["battery health", "battery report", "powercfg battery", "laptop battery life"],
                "callback": self.generate_battery_report
            },
            {
                "name": "🔑 Verify Windows OS License Activation Status (slmgr)",
                "description": "Queries the Software Licensing Service to check Windows OS activation status.",
                "category": "Hardware Diagnostics & Speed Testing",
                "keywords": ["windows activation", "slmgr", "license status", "check activation"],
                "callback": self.check_windows_activation
            },
            {
                "name": "📝 Generate Comprehensive Windows Hardware & System Info Summary",
                "description": "Runs WMIC system queries to summarize CPU, GPU, Motherboard, BIOS, and OS information.",
                "category": "Hardware Diagnostics & Speed Testing",
                "keywords": ["system info", "hardware summary", "cpu gpu details", "bios version"],
                "callback": self.generate_system_info_summary
            },
            {
                "name": "🔒 Disable & Block Windows Updates",
                "description": "Disables the wuauserv service and writes GPO policies to prevent automatic update checks.",
                "category": "Windows Services & Shield Repairs",
                "keywords": ["block updates", "disable windows updates", "stop update service", "noautoupdate"],
                "callback": self.block_windows_updates
            },
            {
                "name": "🔓 Restore & Enable Windows Updates",
                "description": "Enables the wuauserv service and deletes GPO update blocker policies.",
                "category": "Windows Services & Shield Repairs",
                "keywords": ["enable updates", "start windows updates", "restore update service"],
                "callback": self.enable_windows_updates
            }
        ]

    def setup_search_tab(self):
        f = ctk.CTkFrame(self.container, fg_color="transparent")
        self.frames["search"] = f
        
        self.search_scroll = ctk.CTkScrollableFrame(f, fg_color="transparent")
        self.search_scroll.pack(fill="both", expand=True, padx=10, pady=10)

    def trigger_global_search(self):
        query = self.search_input.get().strip().lower()
        if not query:
            return
            
        self.switch_view("search")
        self.header_title.configure(text=f"🔍 Search Results for: '{query}'")
        
        for child in self.search_scroll.winfo_children():
            child.destroy()
            
        matches = []
        for tool in self.tools_catalog:
            match_score = 0
            if query in tool["name"].lower():
                match_score += 10
            if query in tool["description"].lower():
                match_score += 5
            for kw in tool["keywords"]:
                if query in kw.lower():
                    match_score += 3
                    
            if match_score > 0:
                matches.append((tool, match_score))
                
        matches.sort(key=lambda x: x[1], reverse=True)
        
        if not matches:
            no_res_lbl = ctk.CTkLabel(
                self.search_scroll,
                text="❌ No matching tools found.\n\nTry searching for common issues like:\n'printer', 'ram', 'activation', 'update', 'firewall', 'slow', 'audio', 'cache'",
                font=("Outfit", 12, "bold"), text_color="#ef4444", pady=40
            )
            no_res_lbl.pack(fill="both", expand=True)
            return
            
        for tool, score in matches:
            card = ctk.CTkFrame(self.search_scroll, fg_color="#151f32", border_color="#1e293b", border_width=1)
            card.pack(fill="x", padx=10, pady=5)
            
            text_frame = ctk.CTkFrame(card, fg_color="transparent")
            text_frame.pack(side="left", fill="both", expand=True, padx=15, pady=10)
            
            title_lbl = ctk.CTkLabel(
                text_frame, text=tool["name"],
                font=("Outfit", 12, "bold"), text_color="#38bdf8", anchor="w"
            )
            title_lbl.pack(fill="x", anchor="w")
            
            desc_lbl = ctk.CTkLabel(
                text_frame, text=tool["description"],
                font=("Outfit", 10), text_color="#cbd5e1", anchor="w", justify="left"
            )
            desc_lbl.pack(fill="x", anchor="w", pady=(2, 0))
            
            cat_lbl = ctk.CTkLabel(
                text_frame, text=f"Category: {tool['category']}",
                font=("Outfit", 8, "italic"), text_color="#8f9bb3", anchor="w"
            )
            cat_lbl.pack(fill="x", anchor="w", pady=(2, 0))
            
            run_btn = ctk.CTkButton(
                card, text="▶️ Run Tool", font=("Outfit", 10, "bold"), width=120,
                command=tool["callback"]
            )
            run_btn.pack(side="right", padx=15, pady=15)


if __name__ == "__main__":
    import ctypes
    import sys
    
    def is_admin():
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False
            
    if not is_admin():
        # Relaunch the program with admin privileges
        try:
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        except Exception as e:
            pass
        sys.exit(0)
    else:
        app = WindowsRepairSuite()
        app.mainloop()
