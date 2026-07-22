import os
import sys
import shutil
import time
import threading
import subprocess
import winreg
import customtkinter as ctk

# Configure theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

def get_resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

def create_shortcut(target_path, shortcut_path):
    ps_cmd = f'$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut("{shortcut_path}"); $Shortcut.TargetPath = "{target_path}"; $Shortcut.Save()'
    subprocess.run(["powershell", "-Command", ps_cmd], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)

def register_startup(exe_path):
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0,
            winreg.KEY_SET_VALUE
        )
        winreg.SetValueEx(key, "PrintPulseScreenshot", 0, winreg.REG_SZ, exe_path)
        winreg.CloseKey(key)
    except Exception as e:
        print(f"Failed to register startup key: {e}")

class SetupWizard(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("PrintPulse Screenshot Editor Setup")
        self.geometry("520x340")
        self.resizable(False, False)
        
        # Calculate screen center
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        self.geometry(f"+{screen_w // 2 - 260}+{screen_h // 2 - 170}")
        
        self.install_dir = os.path.join(os.environ["LOCALAPPDATA"], "Programs", "PrintPulse")
        self.exe_name = "PrintPulse-Screenshot-Editor.exe"
        
        self.setup_ui()
        
    def setup_ui(self):
        self.main_frame = ctk.CTkFrame(self, fg_color="#181818", corner_radius=10)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Header
        self.title_lbl = ctk.CTkLabel(
            self.main_frame, text="PrintPulse Screenshot Editor",
            font=ctk.CTkFont(size=22, weight="bold"), text_color="#00ffcc"
        )
        self.title_lbl.pack(pady=(30, 5))
        
        self.version_lbl = ctk.CTkLabel(
            self.main_frame, text="Setup Version 2.1 (Upgraded Suite)",
            font=ctk.CTkFont(size=12), text_color="gray"
        )
        self.version_lbl.pack(pady=(0, 20))
        
        # Body label
        self.info_lbl = ctk.CTkLabel(
            self.main_frame,
            text="This wizard will install the PrintPulse Screenshot & Annotation Tool\non your computer.\n\nIt will configure keyboard hotkeys (Ctrl+Shift+S), add start menu entries,\nand enable auto-run on startup.",
            font=ctk.CTkFont(size=13), text_color="#dcdcdc"
        )
        self.info_lbl.pack(pady=10)
        
        # Progress Bar (Hidden initially)
        self.progress = ctk.CTkProgressBar(self.main_frame, width=400)
        self.progress.set(0)
        
        # Button container
        self.btn_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.btn_frame.pack(side="bottom", fill="x", pady=25)
        
        self.cancel_btn = ctk.CTkButton(
            self.btn_frame, text="Cancel", fg_color="#333333", hover_color="#444444",
            text_color="white", width=120, command=self.destroy
        )
        self.cancel_btn.pack(side="right", padx=15)
        
        self.install_btn = ctk.CTkButton(
            self.btn_frame, text="Install Now", fg_color="#1f538d", hover_color="#163e6b",
            text_color="white", width=150, font=ctk.CTkFont(weight="bold"), command=self.start_install
        )
        self.install_btn.pack(side="right", padx=5)

    def start_install(self):
        self.install_btn.pack_forget()
        self.cancel_btn.pack_forget()
        self.info_lbl.configure(text="Installing files, creating shortcuts, and configuring registry...")
        self.progress.pack(pady=20)
        
        threading.Thread(target=self.run_installation, daemon=True).start()

    def run_installation(self):
        steps = 5
        for i in range(1, steps + 1):
            time.sleep(0.4)
            self.progress.set(i / steps)
            
            if i == 1:
                # 1. Create Directories
                os.makedirs(self.install_dir, exist_ok=True)
            elif i == 2:
                # 2. Copy Executable
                src_path = get_resource_path(self.exe_name)
                dest_path = os.path.join(self.install_dir, self.exe_name)
                try:
                    # Kill existing process to avoid permission locks
                    subprocess.run(["taskkill", "/f", "/im", self.exe_name], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
                    shutil.copy2(src_path, dest_path)
                except Exception as e:
                    self.after(0, lambda: self.show_error(f"Copying executable failed:\n{e}"))
                    return
            elif i == 3:
                # 3. Create Shortcuts
                exe_path = os.path.join(self.install_dir, self.exe_name)
                
                # Desktop
                desktop = os.path.join(os.environ["USERPROFILE"], "Desktop")
                desktop_shortcut = os.path.join(desktop, "PrintPulse Screenshot Editor.lnk")
                create_shortcut(exe_path, desktop_shortcut)
                
                # Start Menu
                start_menu = os.path.join(os.environ["APPDATA"], "Microsoft", "Windows", "Start Menu", "Programs")
                start_menu_shortcut = os.path.join(start_menu, "PrintPulse Screenshot Editor.lnk")
                create_shortcut(exe_path, start_menu_shortcut)
                
            elif i == 4:
                # 4. Register Registry Startup
                exe_path = os.path.join(self.install_dir, self.exe_name)
                register_startup(exe_path)
                
            elif i == 5:
                # 5. Launch App
                exe_path = os.path.join(self.install_dir, self.exe_name)
                try:
                    os.startfile(exe_path)
                except:
                    pass
                    
        self.after(0, self.show_success)

    def show_error(self, err_msg):
        self.progress.pack_forget()
        self.info_lbl.configure(text=f"An error occurred during installation:\n\n{err_msg}", text_color="#ff5555")
        close_btn = ctk.CTkButton(
            self.btn_frame, text="Close", fg_color="#333333", hover_color="#444444",
            text_color="white", width=120, command=self.destroy
        )
        close_btn.pack(side="right", padx=15)

    def show_success(self):
        self.progress.pack_forget()
        self.info_lbl.configure(
            text="Installation Completed Successfully!\n\nPrintPulse Screenshot Editor is now running in your background.\nPress Ctrl+Shift+S to capture screenshots at any time.",
            text_color="#00ffcc"
        )
        finish_btn = ctk.CTkButton(
            self.btn_frame, text="Finish", fg_color="#22c55e", hover_color="#15803d",
            text_color="white", width=150, font=ctk.CTkFont(weight="bold"), command=self.destroy
        )
        finish_btn.pack(side="right", padx=15)

if __name__ == "__main__":
    app = SetupWizard()
    app.mainloop()
