# install_nirsoft.py
# Python script to download and extract password-protected NirSoft zips automatically

import os
import sys
import urllib.request
import zipfile
import tempfile
import subprocess

action = sys.argv[1] if len(sys.argv) > 1 else "download"
temp_dir = os.path.join(tempfile.gettempdir(), "NirLauncher")
os.makedirs(temp_dir, exist_ok=True)

if action == "download":
    url = "https://download.nirsoft.net/nirsoft_package_enc_1.30.24.zip"
    zip_path = os.path.join(temp_dir, "nirsoft.zip")
    dest_dir = "C:\\NirLauncher"
    password = b"nirsoft9876$"
    referer = "https://launcher.nirsoft.net/download.html"
    
    print("============================================================")
    print(f"Downloading NirLauncher Package from: {url}")
    print("============================================================")
    
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0', 'Referer': referer})
        with urllib.request.urlopen(req) as response, open(zip_path, 'wb') as out_file:
            out_file.write(response.read())
        print("Download complete. Extracting password-protected ZIP...")
        
        os.makedirs(dest_dir, exist_ok=True)
        with zipfile.ZipFile(zip_path) as z:
            z.extractall(path=dest_dir, pwd=password)
        print(f"Successfully extracted to {dest_dir}")
        print("Done! You can close this window and launch the tool from the dashboard.")
    except Exception as e:
        print(f"Error occurred during download/extraction: {e}")
        sys.exit(1)

elif action == "mailpv":
    url = "https://www.nirsoft.net/toolsdownload/mailpv.zip"
    zip_path = os.path.join(temp_dir, "mailpv.zip")
    dest_dir = "C:\\NirLauncher\\mailpv"
    password = b"nirsoft9876$"
    referer = "https://www.nirsoft.net/utils/mailpv.html"
    
    print("============================================================")
    print(f"Downloading MailPassView from: {url}")
    print("============================================================")
    
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0', 'Referer': referer})
        with urllib.request.urlopen(req) as response, open(zip_path, 'wb') as out_file:
            out_file.write(response.read())
        print("Download complete. Extracting password-protected ZIP...")
        
        os.makedirs(dest_dir, exist_ok=True)
        with zipfile.ZipFile(zip_path) as z:
            z.extractall(path=dest_dir, pwd=password)
        print(f"Successfully extracted to {dest_dir}")
        
        exe_path = os.path.join(dest_dir, "mailpv.exe")
        if os.path.exists(exe_path):
            print("Launching MailPassView...")
            os.startfile(exe_path)
        print("Done!")
    except Exception as e:
        print(f"Error occurred during download/extraction: {e}")
        sys.exit(1)
