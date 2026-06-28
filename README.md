# 🛠️ PrintPulse Diagnostics & System Recovery Suite

PrintPulse is a premium, all-in-one system optimization, offline diagnostics, and boot recovery toolkit designed for Windows IT Administrators and power users. It combines a conversational AI troubleshooter, a local Web Dashboard server, and a fully featured standalone Python GUI application.

---

## 🚀 Key Feature Modules

### 1. 🤖 Conversational AI Assistant
* **Online Mode:** Guided step-by-step troubleshooting powered by Google Gemini (1.5 Flash / 2.5 Flash) with support for analyzing screenshots of BSODs or error codes.
* **Offline Mode:** Rule-based fallback system diagnostics ensuring tool functionality even when internet access is absent.
* **Preloaded Keys:** Secure automatic key storage in `~/.winpulse_config.json`.

### 2. 💾 Disk Management & Lossless Converters
* **FAT32 to NTFS:** Lossless file system conversion using native Windows `convert.exe` without drive formatting.
* **MBR to GPT:** In-place partition style conversion via `mbr2gpt.exe` without data loss, enabling legacy systems to upgrade to UEFI.

### 3. 🔑 Offline Password Recovery (SAM/Utilman Bypass)
* **Ease of Access Hack:** Replaces utility manager (`utilman.exe`) with Command Prompt (`cmd.exe`) on target offline Windows drives.
* **Administrator Shell:** Boot into the OS, launch the elevated console from the lock screen, and reset/bypass local account passwords offline.
* **Safe Restore:** One-click restoration to put back the original `utilman.exe`.

### 4. 🛠️ Boot Sector & BCD Recovery Suite
* **bootrec Utilities:** Fix Master Boot Records (`/fixmbr`), write new boot sectors (`/fixboot`), and scan/rebuild Boot Configuration Data (`/rebuildbcd`).
* **BCDBoot Builder:** Automatically rebuild bootloader files for both UEFI (GPT) and Legacy (MBR) systems.

### 5. 🚀 OS Installation Setup Error Fixer
* **EFI/UEFI Mismatch:** Automatically scripts `diskpart` to wipe and partition target drives to GPT.
* **Legacy Mismatches & Dynamic Disks:** Converts disks back to MBR or Basic partitions automatically.
* **Setup Failures:** Automated scans and repair scripts resolving Windows installer issues like error `0x80300024` and `0x80070570`.

### 6. 🌐 Removable WinPE USB Builder
* **Dynamic Removable Disk Detection:** Safely lists active USB flash drives while protecting system drives.
* **Bootable Drive Creator:** Formats USB to FAT32, mounts a WinPE source ISO, replicates boot files using multi-threaded `robocopy`, and embeds the PrintPulse diagnostics suite directly onto the root folder.

### 7. 💻 Administrative Super Admin Suite
* **System Repairs:** SFC scans, DISM integrity scans, and Windows Update Agent resets.
* **System Debloater:** Disable telemetry, Cortana, OneDrive, Xbox services, and remove pre-installed bloatware.
* **Activations & Deployments:** Office 365/2021/2024 deployment scripting and HWID/KMS activation helpers.
* **NirSoft Utilities:** Built-in launchers for advanced NirSoft spec logs and password recovery tools.

---

## 📦 Directory Structure

* 📂 **`gui_app.py`** — The primary standalone Tkinter Desktop application (built using CustomTkinter).
* 📂 **`server.py`** / **`main.exe`** — Python web server backend which hosts the local Web Dashboard on port `3000`.
* 📂 **`index.html`** / **`app.js`** / **`styles.css`** — The frontend files for the Web Dashboard interface.
* 📂 **`Start-Admin-Server.bat`** — Auto-elevated startup script to launch the local web server.
* 📂 **`build_exe.bat`** — PyInstaller compilation script to compile `server.py` to `main.exe`.
* 📂 **`PrintPulse.spec`** — Custom PyInstaller spec configuration for building the standalone GUI executable.

---

## 🛠️ Installation & Compilation

### Running from Python Source
Ensure you have Python 3.12+ installed along with dependencies:
```bash
pip install customtkinter pillow psutil
```
* **Launch GUI App:** `python gui_app.py`
* **Launch Web Server:** Run `Start-Admin-Server.bat` or `python server.py`

### Compiling to Standalone Executables
If you need to compile a fresh set of binaries for deployment on offline client machines:
1. **Build Web Server (`main.exe`):**
   ```bash
   pyinstaller --noconfirm --distpath . main.spec
   ```
2. **Build GUI Client (`PrintPulse.exe`):**
   ```bash
   pyinstaller --noconfirm PrintPulse.spec
   ```

---

## ⚠️ Security Notice
This toolkit contains utilities designed to bypass lock screens (`utilman` exploit) and modify low-level partition structures (`diskpart` wipes). These tools should only be run on authorized systems. Some tools require elevation (Administrator privileges) to execute system commands.
