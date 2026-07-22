import os
import sys
import io
import time
import ctypes
from ctypes import wintypes
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from PIL import Image, ImageTk, ImageGrab, ImageDraw, ImageFilter, ImageFont
import customtkinter as ctk
import pystray
from pystray import MenuItem as item

def get_asset_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

# Configure CustomTkinter appearance
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# Windows Clipboard API
CF_DIB = 8
GMEM_MOVEABLE = 0x0002

OpenClipboard = ctypes.windll.user32.OpenClipboard
OpenClipboard.argtypes = [wintypes.HWND]
OpenClipboard.restype = wintypes.BOOL

EmptyClipboard = ctypes.windll.user32.EmptyClipboard
EmptyClipboard.restype = wintypes.BOOL

SetClipboardData = ctypes.windll.user32.SetClipboardData
SetClipboardData.argtypes = [wintypes.UINT, wintypes.HANDLE]
SetClipboardData.restype = wintypes.HANDLE

CloseClipboard = ctypes.windll.user32.CloseClipboard
CloseClipboard.restype = wintypes.BOOL

GlobalAlloc = ctypes.windll.kernel32.GlobalAlloc
GlobalAlloc.argtypes = [wintypes.UINT, ctypes.c_size_t]
GlobalAlloc.restype = wintypes.HANDLE

GlobalLock = ctypes.windll.kernel32.GlobalLock
GlobalLock.argtypes = [wintypes.HANDLE]
GlobalLock.restype = ctypes.c_void_p

GlobalUnlock = ctypes.windll.kernel32.GlobalUnlock
GlobalUnlock.argtypes = [wintypes.HANDLE]
GlobalUnlock.restype = wintypes.BOOL

def copy_image_to_clipboard(pil_image):
    try:
        output = io.BytesIO()
        pil_image.convert("RGB").save(output, "BMP")
        data = output.getvalue()[14:]  # Strip BMP 14-byte header
        output.close()
        if not OpenClipboard(None):
            return False
        try:
            EmptyClipboard()
            h_global_mem = GlobalAlloc(GMEM_MOVEABLE, len(data))
            p_global_mem = GlobalLock(h_global_mem)
            ctypes.memmove(p_global_mem, data, len(data))
            GlobalUnlock(h_global_mem)
            SetClipboardData(CF_DIB, h_global_mem)
        finally:
            CloseClipboard()
        return True
    except Exception as e:
        print(f"Error copying to clipboard: {e}")
        return False

# Image Stitching for Scrolling Screenshots
def stitch_two_images(img1, img2):
    w1, h1 = img1.size
    w2, h2 = img2.size
    if w1 != w2:
        new_h2 = int(h2 * w1 / w2)
        img2 = img2.resize((w1, new_h2), Image.Resampling.LANCZOS)
        w2, h2 = img2.size
    if h1 > h2:
        img1_match = img1.crop((0, h1 - h2, w1, h1))
        h1_match = h2
    else:
        img1_match = img1
        h1_match = h1
        
    pixels1 = img1_match.load()
    pixels2 = img2.load()
    best_dy = h1_match
    min_score = float('inf')
    cols = [int(w1 * i / 11) for i in range(1, 11)]
    min_shift = max(10, int(h1_match * 0.05))
    max_shift = h1_match - 10
    
    for dy in range(min_shift, max_shift, 2):
        diff_sum = 0
        match_points = 0
        for y in range(dy, h1_match, 3):
            y2 = y - dy
            if y2 >= h2:
                break
            for x in cols:
                p1 = pixels1[x, y]
                p2 = pixels2[x, y2]
                if isinstance(p1, tuple):
                    diff_sum += abs(p1[0] - p2[0]) + abs(p1[1] - p2[1]) + abs(p1[2] - p2[2])
                else:
                    diff_sum += abs(p1 - p2)
                match_points += 1
        if match_points > 0:
            score = diff_sum / match_points
            if score < min_score:
                min_score = score
                best_dy = dy
                
    if min_score < 45:
        new_height = h1 + best_dy
        stitched = Image.new("RGB", (w1, new_height))
        stitched.paste(img1, (0, 0))
        stitched.paste(img2.crop((0, h1_match - best_dy, w1, h2)), (0, h1))
        return stitched
    else:
        new_height = h1 + h2
        stitched = Image.new("RGB", (w1, new_height))
        stitched.paste(img1, (0, 0))
        stitched.paste(img2, (0, h1))
        return stitched

def stitch_all_frames(frames):
    if not frames:
        return None
    if len(frames) == 1:
        return frames[0]
    result = frames[0]
    for i in range(1, len(frames)):
        result = stitch_two_images(result, frames[i])
    return result

def draw_arrow(draw, start, end, color, width=4):
    x1, y1 = start
    x2, y2 = end
    draw.line([x1, y1, x2, y2], fill=color, width=width)
    dx = x2 - x1
    dy = y2 - y1
    length = (dx**2 + dy**2)**0.5
    if length > 0:
        ux = dx / length
        uy = dy / length
        size = 18
        bx = x2 - ux * size
        by = y2 - uy * size
        px = -uy * size * 0.5
        py = ux * size * 0.5
        left = (bx + px, by + py)
        right = (bx - px, by - py)
        draw.polygon([end, left, right], fill=color)

# Draw a beautiful pointing hand gesture cursor (fallback)
def draw_hand_gesture(draw, center, color, pil_image=None):
    asset_path = get_asset_path("hand_pointer.png")
    
    if os.path.exists(asset_path) and pil_image is not None:
        try:
            hand_asset = Image.open(asset_path)
            w, h = hand_asset.size
            px = center[0]
            py = center[1] - (h // 2)
            pil_image.paste(hand_asset, (px, py), hand_asset)
            return
        except Exception as e:
            print(f"Error pasting custom hand pointer: {e}")

    cx, cy = center
    points = [
        (cx, cy),
        (cx + 6, cy + 14),
        (cx + 12, cy + 12),
        (cx + 16, cy + 16),
        (cx + 20, cy + 20),
        (cx + 20, cy + 30),
        (cx + 10, cy + 36),
        (cx - 2, cy + 36),
        (cx - 6, cy + 28),
        (cx - 14, cy + 24),
        (cx - 10, cy + 18),
        (cx - 3, cy + 20),
        (cx - 2, cy + 10)
    ]
    draw.polygon(points, fill="white", outline=color, width=2)
    draw.line([cx + 6, cy + 18, cx + 6, cy + 30], fill=color, width=1)
    draw.line([cx + 11, cy + 20, cx + 11, cy + 32], fill=color, width=1)
    draw.line([cx + 15, cy + 22, cx + 15, cy + 34], fill=color, width=1)

# Windows Native OCR PowerShell command runner
def run_windows_ocr(image_path):
    ps_cmd = f"""
    [void][System.Reflection.Assembly]::LoadWithPartialName("System.Runtime.WindowsRuntime")
    [Windows.Storage.Streams.IRandomAccessStream, Windows.Storage, ContentType=WindowsRuntime] | Out-Null
    [Windows.Graphics.Imaging.BitmapDecoder, Windows.Graphics.Imaging, ContentType=WindowsRuntime] | Out-Null
    [Windows.Media.Ocr.OcrEngine, Windows.Media.Ocr, ContentType=WindowsRuntime] | Out-Null
    [Windows.Media.Ocr.OcrResult, Windows.Media.Ocr, ContentType=WindowsRuntime] | Out-Null
    
    function Await($op, $type) {{
        $asTaskMethod = [System.WindowsRuntimeSystemExtensions].GetMethods() | Where-Object {{ 
            $_.Name -eq 'AsTask' -and 
            $_.GetGenericArguments().Length -eq 1 -and
            $_.GetParameters().Length -eq 1 -and
            $_.GetParameters()[0].ParameterType.Name -eq 'IAsyncOperation`1'
        }}
        $genericMethod = $asTaskMethod.MakeGenericMethod($type)
        $task = $genericMethod.Invoke($null, @($op))
        return $task.Result
    }}
    
    # Open FileStream natively in .NET to bypass COM interface casting issues
    $fileStream = [System.IO.File]::OpenRead("{os.path.abspath(image_path)}")
    $stream = [System.IO.WindowsRuntimeStreamExtensions]::AsRandomAccessStream($fileStream)
    
    $decoderOp = [Windows.Graphics.Imaging.BitmapDecoder]::CreateAsync($stream)
    $decoder = Await $decoderOp ([Windows.Graphics.Imaging.BitmapDecoder])
    
    $bitmapOp = $decoder.GetSoftwareBitmapAsync()
    $bitmap = Await $bitmapOp ([Windows.Graphics.Imaging.SoftwareBitmap])
    
    $engine = [Windows.Media.Ocr.OcrEngine]::TryCreateFromUserProfileLanguages()
    if ($engine -ne $null) {{
        $ocrOp = $engine.RecognizeAsync($bitmap)
        $result = Await $ocrOp ([Windows.Media.Ocr.OcrResult])
        Write-Output $result.Text
    }} else {{
        Write-Output "ERROR: Windows OCR Engine is not available."
    }}
    
    $fileStream.Close()
    """
    try:
        import subprocess
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        res = subprocess.run(
            ["powershell", "-NoProfile", "-Command", ps_cmd],
            capture_output=True, text=True, startupinfo=startupinfo, encoding='utf-8', errors='ignore'
        )
        
        stdout = res.stdout.strip()
        stderr = res.stderr.strip()
        
        if stderr:
            if "Exception" in stderr or "Error" in stderr or "Failed" in stderr or "CategoryInfo" in stderr:
                return f"Error:\n{stderr}"
                
        if not stdout:
            return "No text found"
            
        return stdout
    except Exception as e:
        return f"Error executing OCR process:\n{str(e)}"

# Draw beautiful colorful vector icons at runtime (Fallback)
def create_vector_icon(name, color_hex):
    img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    w = 4
    
    if name == "camera":
        draw.rounded_rectangle([12, 20, 52, 48], radius=6, outline=color_hex, width=w)
        draw.ellipse([22, 24, 42, 44], outline=color_hex, width=w)
        draw.rectangle([18, 14, 28, 20], fill=color_hex)
        draw.ellipse([44, 24, 48, 28], fill=color_hex)
        
    elif name == "timer":
        draw.ellipse([12, 16, 52, 56], outline=color_hex, width=w)
        draw.ellipse([30, 34, 34, 38], fill=color_hex)
        draw.line([32, 36, 32, 24], fill=color_hex, width=w)
        draw.line([32, 36, 44, 36], fill=color_hex, width=w)
        draw.line([28, 12, 36, 12], fill=color_hex, width=w+1)
        draw.line([32, 12, 32, 16], fill=color_hex, width=w)
        
    elif name == "window":
        draw.rounded_rectangle([10, 14, 54, 50], radius=5, outline=color_hex, width=w)
        draw.line([10, 24, 54, 24], fill=color_hex, width=w-1)
        draw.ellipse([16, 18, 20, 22], fill=color_hex)
        draw.ellipse([24, 18, 28, 22], fill=color_hex)
        
    elif name == "scroll":
        draw.rounded_rectangle([14, 12, 50, 52], radius=4, outline=color_hex, width=w)
        draw.line([22, 22, 42, 22], fill=color_hex, width=w-1)
        draw.line([22, 32, 42, 32], fill=color_hex, width=w-1)
        draw.line([22, 42, 34, 42], fill=color_hex, width=w-1)
        
    elif name == "record":
        draw.rounded_rectangle([10, 18, 42, 46], radius=5, outline=color_hex, width=w)
        draw.polygon([42, 26, 54, 18, 54, 46, 42, 38], outline=color_hex, fill=color_hex)
        draw.ellipse([20, 26, 32, 38], fill=color_hex)
        
    elif name == "dropper":
        draw.ellipse([40, 12, 52, 24], fill=color_hex)
        draw.line([20, 44, 44, 20], fill=color_hex, width=w+2)
        draw.line([14, 50, 20, 44], fill=color_hex, width=w)
        
    elif name == "ocr":
        draw.rectangle([10, 10, 54, 54], outline=color_hex, width=2)
        draw.line([20, 44, 32, 18], fill=color_hex, width=w)
        draw.line([32, 18, 44, 44], fill=color_hex, width=w)
        draw.line([25, 34, 39, 34], fill=color_hex, width=w)
        
    elif name == "editor":
        draw.ellipse([12, 16, 52, 48], outline=color_hex, width=w)
        draw.ellipse([20, 28, 26, 34], fill=color_hex)
        draw.ellipse([30, 22, 34, 26], fill="#ff3333")
        draw.ellipse([40, 24, 44, 28], fill="#33cc33")
        draw.ellipse([42, 34, 46, 38], fill="#3388ff")
        draw.ellipse([32, 38, 36, 42], fill="#ffcc00")
        
    elif name == "close":
        draw.line([18, 18, 46, 46], fill=color_hex, width=w+1)
        draw.line([46, 18, 18, 46], fill=color_hex, width=w+1)
        
    elif name == "fullscreen":
        draw.rounded_rectangle([10, 14, 54, 50], radius=4, outline=color_hex, width=w)
        draw.line([16, 22, 22, 22], fill=color_hex, width=w)
        draw.line([16, 22, 16, 28], fill=color_hex, width=w)
        draw.line([48, 22, 42, 22], fill=color_hex, width=w)
        draw.line([48, 22, 48, 28], fill=color_hex, width=w)
        draw.line([16, 42, 22, 42], fill=color_hex, width=w)
        draw.line([16, 42, 16, 36], fill=color_hex, width=w)
        draw.line([48, 42, 42, 42], fill=color_hex, width=w)
        draw.line([48, 42, 48, 36], fill=color_hex, width=w)
        
    elif name == "history":
        draw.ellipse([12, 12, 52, 52], outline=color_hex, width=w)
        draw.line([32, 32, 32, 20], fill=color_hex, width=w)
        draw.line([32, 32, 42, 32], fill=color_hex, width=w)
        
    elif name == "pdfutils":
        draw.rectangle([14, 10, 50, 54], outline=color_hex, width=w)
        draw.line([22, 22, 42, 22], fill=color_hex, width=w-1)
        draw.line([22, 32, 42, 32], fill=color_hex, width=w-1)
        draw.line([22, 42, 42, 42], fill=color_hex, width=w-1)
        
    return img.resize((32, 32), Image.Resampling.LANCZOS)

# Create 24x24 Fluent-style icons for drawing tools
def create_editor_vector_icon(name, color_hex):
    img = Image.new("RGBA", (48, 48), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    w = 3
    
    if name == "select":
        draw.polygon([12, 8, 12, 36, 21, 28, 32, 28], outline=color_hex, fill=color_hex, width=2)
        draw.line([20, 26, 29, 38], fill=color_hex, width=w)
        
    elif name == "pen":
        draw.line([12, 36, 36, 12], fill=color_hex, width=w+1)
        draw.polygon([8, 40, 15, 36, 12, 33], fill=color_hex)
        
    elif name == "highlighter":
        draw.line([12, 36, 33, 15], fill=color_hex, width=w+4)
        draw.rectangle([30, 12, 36, 18], fill=color_hex)
        
    elif name == "rectangle":
        draw.rounded_rectangle([9, 12, 39, 36], radius=3, outline=color_hex, width=w)
        
    elif name == "arrow":
        draw.line([12, 36, 33, 15], fill=color_hex, width=w)
        draw.polygon([36, 12, 27, 12, 36, 21], fill=color_hex)
        
    elif name == "blur":
        for x in range(12, 38, 6):
            for y in range(12, 38, 6):
                draw.rectangle([x, y, x+3, y+3], fill=color_hex)
                
    elif name == "text":
        draw.line([12, 12, 36, 12], fill=color_hex, width=w)
        draw.line([24, 12, 24, 36], fill=color_hex, width=w)
        draw.line([18, 36, 30, 36], fill=color_hex, width=w)
        
    elif name == "hand":
        draw_hand_gesture(draw, (24, 16), color_hex)
        
    elif name == "badge":
        draw.ellipse([10, 10, 38, 38], outline=color_hex, width=w)
        draw.line([24, 16, 24, 32], fill=color_hex, width=w)
        draw.line([21, 18, 24, 16], fill=color_hex, width=w)
        
    elif name == "magnifier":
        draw.ellipse([10, 10, 30, 30], outline=color_hex, width=w)
        draw.line([28, 28, 38, 38], fill=color_hex, width=w+1)
        
    elif name == "emoji":
        draw.ellipse([10, 10, 38, 38], outline=color_hex, width=w)
        draw.ellipse([17, 18, 21, 22], fill=color_hex)
        draw.ellipse([27, 18, 31, 22], fill=color_hex)
        draw.arc([18, 22, 30, 32], 0, 180, fill=color_hex, width=w)
        
    return img.resize((20, 20), Image.Resampling.LANCZOS)


# Floating Toolbar for the Selection Box
class SelectionToolbar(tk.Toplevel):
    def __init__(self, selector_window, on_capture, on_cancel):
        super().__init__(selector_window)
        self.selector = selector_window
        self.on_capture = on_capture
        self.on_cancel = on_cancel
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.configure(bg="#212121")
        self.config(highlightbackground="#1f538d", highlightthickness=2)
        frame = tk.Frame(self, bg="#212121")
        frame.pack(padx=5, pady=5)
        self.btn_cap = tk.Button(
            frame, text="✔ Capture", bg="#28a745", fg="white", 
            font=("Arial", 10, "bold"), relief="flat", padx=12, pady=4,
            cursor="hand2", command=self.on_capture
        )
        self.btn_cap.pack(side="left", padx=4)
        self.btn_can = tk.Button(
            frame, text="✖ Cancel", bg="#dc3545", fg="white", 
            font=("Arial", 10, "bold"), relief="flat", padx=12, pady=4,
            cursor="hand2", command=self.on_cancel
        )
        self.btn_can.pack(side="left", padx=4)


# Full Screen Region Selector overlay
class RegionSelector(tk.Toplevel):
    def __init__(self, parent, on_capture_callback, title_text="Drag to Select Area"):
        super().__init__(parent)
        self.parent = parent
        self.on_capture_callback = on_capture_callback
        self.overrideredirect(True)
        self.state("zoomed")
        self.attributes("-topmost", True)
        
        self.full_screen_img = ImageGrab.grab()
        self.screen_w, self.screen_h = self.full_screen_img.size
        
        overlay = Image.new("RGBA", self.full_screen_img.size, (0, 0, 0, 140))
        self.bg_img = Image.alpha_composite(self.full_screen_img.convert("RGBA"), overlay)
        self.bg_photo = ImageTk.PhotoImage(self.bg_img)
        
        self.canvas = tk.Canvas(self, cursor="cross", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.create_image(0, 0, image=self.bg_photo, anchor="nw", tags="bg")
        
        self.x1, self.y1 = 0, 0
        self.x2, self.y2 = 0, 0
        self.rect_id = None
        self.border_id = None
        self.active_handle = None
        self.handle_ids = {}
        self.handle_size = 8
        self.size_lbl_id = None
        
        self.toolbar_frame = tk.Frame(self.canvas, bg="#212121", highlightbackground="#1f538d", highlightthickness=2)
        btn_cap = tk.Button(
            self.toolbar_frame, text="✔ Capture", bg="#28a745", fg="white", 
            font=("Arial", 10, "bold"), relief="flat", padx=12, pady=4,
            cursor="hand2", command=self.confirm_capture
        )
        btn_cap.pack(side="left", padx=5, pady=5)
        
        btn_can = tk.Button(
            self.toolbar_frame, text="✖ Cancel", bg="#dc3545", fg="white", 
            font=("Arial", 10, "bold"), relief="flat", padx=12, pady=4,
            cursor="hand2", command=self.cancel
        )
        btn_can.pack(side="left", padx=5, pady=5)
        
        self.toolbar_window_id = None
        self.bind_events()
        
    def bind_events(self):
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.bind("<Escape>", self.cancel)
        self.bind("<Return>", self.confirm_capture)
        
    def on_press(self, event):
        self.hide_toolbar()
        clicked_item = self.canvas.find_withtag("current")
        if clicked_item:
            tags = self.canvas.gettags(clicked_item[0])
            for tag in tags:
                if tag.startswith("handle_"):
                    self.active_handle = tag.split("_")[1]
                    return
        self.active_handle = "new"
        self.x1, self.y1 = event.x, event.y
        self.x2, self.y2 = event.x, event.y
        self.update_selection_visual()
        
    def on_drag(self, event):
        x = max(0, min(event.x, self.screen_w))
        y = max(0, min(event.y, self.screen_h))
        if self.active_handle == "new":
            self.x2, self.y2 = x, y
        elif self.active_handle == "tl":
            self.x1, self.y1 = x, y
        elif self.active_handle == "tr":
            self.x2, self.y1 = x, y
        elif self.active_handle == "bl":
            self.x1, self.y2 = x, y
        elif self.active_handle == "br":
            self.x2, self.y2 = x, y
        elif self.active_handle == "t":
            self.y1 = y
        elif self.active_handle == "b":
            self.y2 = y
        elif self.active_handle == "l":
            self.x1 = x
        elif self.active_handle == "r":
            self.x2 = x
        self.update_selection_visual()
        
    def on_release(self, event):
        self.active_handle = None
        rx1, rx2 = min(self.x1, self.x2), max(self.x1, self.x2)
        ry1, ry2 = min(self.y1, self.y2), max(self.y1, self.y2)
        self.x1, self.x2 = rx1, rx2
        self.y1, self.y2 = ry1, ry2
        self.update_selection_visual()
        self.show_toolbar()
        
    def show_toolbar(self):
        rx1, rx2 = self.x1, self.x2
        ry1, ry2 = self.y1, self.y2
        if rx2 - rx1 <= 15 or ry2 - ry1 <= 15:
            self.hide_toolbar()
            return
            
        tb_width = 200
        tb_height = 45
        tb_x = rx1 + (rx2 - rx1) // 2
        tb_y = ry2 + 25
        
        if tb_y + tb_height // 2 > self.screen_h - 10:
            tb_y = ry1 - 25
            if tb_y - tb_height // 2 < 10:
                tb_y = ry2 - 25
                
        if self.toolbar_window_id:
            self.canvas.coords(self.toolbar_window_id, tb_x, tb_y)
        else:
            self.toolbar_window_id = self.canvas.create_window(
                tb_x, tb_y, window=self.toolbar_frame, anchor="center", tags="toolbar"
            )
            
    def hide_toolbar(self):
        if self.toolbar_window_id:
            self.canvas.delete(self.toolbar_window_id)
            self.toolbar_window_id = None
        
    def update_selection_visual(self):
        if self.rect_id:
            self.canvas.delete(self.rect_id)
        if self.border_id:
            self.canvas.delete(self.border_id)
        if self.size_lbl_id:
            self.canvas.delete(self.size_lbl_id)
        for h_id in self.handle_ids.values():
            self.canvas.delete(h_id)
        self.handle_ids.clear()
        
        rx1, rx2 = min(self.x1, self.x2), max(self.x1, self.x2)
        ry1, ry2 = min(self.y1, self.y2), max(self.y1, self.y2)
        if rx2 - rx1 <= 5 or ry2 - ry1 <= 5:
            return
            
        cropped = self.full_screen_img.crop((rx1, ry1, rx2, ry2))
        self.cropped_photo = ImageTk.PhotoImage(cropped)
        self.rect_id = self.canvas.create_image(rx1, ry1, image=self.cropped_photo, anchor="nw")
        self.border_id = self.canvas.create_rectangle(rx1, ry1, rx2, ry2, outline="#1f538d", width=3)
        
        size_text = f" {rx2 - rx1} x {ry2 - ry1} px "
        text_y = ry1 - 15 if ry1 > 30 else ry2 + 15
        self.size_lbl_id = self.canvas.create_text(
            rx1 + 2, text_y, text=size_text, fill="#00ffcc",
            font=("Arial", 11, "bold"), anchor="w"
        )
        
        handles = {
            "tl": (rx1, ry1, "size_nw_se"),
            "tr": (rx2, ry1, "size_ne_sw"),
            "bl": (rx1, ry2, "size_ne_sw"),
            "br": (rx2, ry2, "size_nw_se"),
            "t": ((rx1+rx2)//2, ry1, "size_ns"),
            "b": ((rx1+rx2)//2, ry2, "size_ns"),
            "l": (rx1, (ry1+ry2)//2, "size_we"),
            "r": (rx2, (ry1+ry2)//2, "size_we")
        }
        hs = self.handle_size
        for name, (hx, hy, cursor) in handles.items():
            h_id = self.canvas.create_rectangle(
                hx - hs, hy - hs, hx + hs, hy + hs, 
                fill="#1f538d", outline="white", width=1.5,
                tags=f"handle_{name}"
            )
            self.handle_ids[name] = h_id
            self.canvas.tag_bind(h_id, "<Enter>", lambda e, c=cursor: self.canvas.config(cursor=c))
            self.canvas.tag_bind(h_id, "<Leave>", lambda e: self.canvas.config(cursor="cross"))
            
    def confirm_capture(self, event=None):
        rx1, rx2 = min(self.x1, self.x2), max(self.x1, self.x2)
        ry1, ry2 = min(self.y1, self.y2), max(self.y1, self.y2)
        if rx2 - rx1 > 5 and ry2 - ry1 > 5:
            screenshot = self.full_screen_img.crop((rx1, ry1, rx2, ry2))
            self.hide_toolbar()
            self.destroy()
            self.parent.deiconify()
            self.on_capture_callback(screenshot, (rx1, ry1, rx2, ry2))
        else:
            messagebox.showwarning("Warning", "Please select a valid area first.")
            
    def cancel(self, event=None):
        self.hide_toolbar()
        self.destroy()
        self.parent.deiconify()


# Floating Controller for Manual Scrolling Screenshot
class ScrollController(tk.Toplevel):
    def __init__(self, parent, crop_box, on_stitch_callback, on_cancel_callback):
        super().__init__(parent)
        self.parent = parent
        self.crop_box = crop_box
        self.on_stitch_callback = on_stitch_callback
        self.on_cancel_callback = on_cancel_callback
        
        self.title("Scroll Capture")
        screen_w = self.winfo_screenwidth()
        self.geometry(f"300x200+{screen_w - 340}+80")
        self.attributes("-topmost", True)
        self.resizable(False, False)
        self.configure(bg="#1f1f1f")
        self.config(highlightbackground="#1f538d", highlightthickness=2)
        
        self.frames = []
        self.lbl_title = tk.Label(self, text="📜 Scrolling Screenshot Controller", bg="#1f1f1f", fg="white", font=("Arial", 11, "bold"))
        self.lbl_title.pack(pady=(12, 4))
        self.lbl_info = tk.Label(self, text="1. Scroll down a bit in your target window.\n2. Click 'Capture Section' below.", bg="#1f1f1f", fg="#b0b0b0", font=("Arial", 9), justify="left")
        self.lbl_info.pack(pady=4)
        self.lbl_status = tk.Label(self, text="Sections captured: 0", bg="#1f1f1f", fg="#00ffcc", font=("Arial", 10, "bold"))
        self.lbl_status.pack(pady=4)
        
        btn_frame = tk.Frame(self, bg="#1f1f1f")
        btn_frame.pack(fill="x", padx=15, pady=5)
        self.btn_capture = tk.Button(btn_frame, text="📸 Capture Section", bg="#1f538d", fg="white", font=("Arial", 10, "bold"), relief="flat", height=2, cursor="hand2", command=self.capture_frame)
        self.btn_capture.pack(fill="x", pady=2)
        self.btn_stitch = tk.Button(btn_frame, text="✔ Stitch & Save", bg="#28a745", fg="white", font=("Arial", 10, "bold"), relief="flat", height=1, cursor="hand2", command=self.finish_stitch)
        self.btn_stitch.pack(side="left", fill="x", expand=True, pady=2, padx=(0, 2))
        self.btn_cancel = tk.Button(btn_frame, text="✖ Cancel", bg="#dc3545", fg="white", font=("Arial", 10, "bold"), relief="flat", height=1, cursor="hand2", command=self.cancel)
        self.btn_cancel.pack(side="right", fill="x", expand=True, pady=2, padx=(2, 0))
        
        self.capture_frame()
        
    def capture_frame(self):
        self.withdraw()
        self.update_idletasks()
        self.update()
        self.after(300, self._do_capture)
        
    def _do_capture(self):
        full_img = ImageGrab.grab()
        frame = full_img.crop(self.crop_box)
        self.frames.append(frame)
        self.deiconify()
        self.lbl_status.config(text=f"Sections captured: {len(self.frames)}")
        
    def finish_stitch(self):
        if len(self.frames) < 1:
            messagebox.showerror("Error", "No frames were captured.")
            self.destroy()
            return
        self.withdraw()
        self.update()
        stitched_img = stitch_all_frames(self.frames)
        self.destroy()
        self.on_stitch_callback(stitched_img)
        
    def cancel(self):
        self.destroy()
        self.on_cancel_callback()


# Floating Controller for GIF Recording
class GIFRecorderController(tk.Toplevel):
    def __init__(self, parent, crop_box, on_finish_callback):
        super().__init__(parent)
        self.parent = parent
        self.crop_box = crop_box
        self.on_finish = on_finish_callback
        
        self.title("Recording Screen")
        screen_w = self.winfo_screenwidth()
        self.geometry(f"260x130+{screen_w - 300}+80")
        self.attributes("-topmost", True)
        self.resizable(False, False)
        self.configure(bg="#1f1f1f")
        self.config(highlightbackground="red", highlightthickness=2)
        
        self.frames = []
        self.max_frames = 150  # 15 seconds limit at 10 FPS
        self.is_recording = True
        self.elapsed_ms = 0
        
        self.lbl_status = tk.Label(self, text="● REC", bg="#1f1f1f", fg="red", font=("Arial", 11, "bold"))
        self.lbl_status.pack(pady=(12, 4))
        
        self.lbl_timer = tk.Label(self, text="00:00 / 00:15", bg="#1f1f1f", fg="white", font=("Arial", 12, "bold"))
        self.lbl_timer.pack(pady=4)
        
        self.btn_stop = tk.Button(
            self, text="⏹ Stop & Compile GIF", bg="#dc3545", fg="white", 
            font=("Arial", 10, "bold"), relief="flat", height=1, cursor="hand2",
            activebackground="#c82333", activeforeground="white",
            command=self.stop_recording
        )
        self.btn_stop.pack(fill="x", padx=20, pady=5)
        
        self.blink_dot()
        self.record_loop()
        
    def blink_dot(self):
        if not self.is_recording:
            return
        curr_fg = self.lbl_status.cget("fg")
        new_fg = "gray" if curr_fg == "red" else "red"
        self.lbl_status.config(fg=new_fg)
        self.after(500, self.blink_dot)
        
    def record_loop(self):
        if not self.is_recording:
            return
            
        full_img = ImageGrab.grab()
        frame = full_img.crop(self.crop_box)
        
        w, h = frame.size
        max_dim = 600
        if max(w, h) > max_dim:
            ratio = max_dim / max(w, h)
            frame = frame.resize((int(w * ratio), int(h * ratio)), Image.Resampling.NEAREST)
            
        self.frames.append(frame)
        self.elapsed_ms += 100
        
        seconds = self.elapsed_ms // 1000
        self.lbl_timer.config(text=f"00:{seconds:02d} / 00:15")
        
        if len(self.frames) >= self.max_frames:
            self.stop_recording()
        else:
            self.after(100, self.record_loop) # 10 FPS
            
    def stop_recording(self):
        self.is_recording = False
        self.withdraw()
        self.update()
        if self.frames:
            self.destroy()
            self.on_finish(self.frames)
        else:
            self.destroy()
            self.on_finish(None)


# Eye-Dropper Color Picker Overlay Window
class ColorPickerOverlay(tk.Toplevel):
    def __init__(self, parent, on_color_picked_callback):
        super().__init__(parent)
        self.parent = parent
        self.on_picked = on_color_picked_callback
        
        self.overrideredirect(True)
        self.state("zoomed")
        self.attributes("-topmost", True)
        
        self.full_screen_img = ImageGrab.grab()
        self.screen_w, self.screen_h = self.full_screen_img.size
        self.bg_photo = ImageTk.PhotoImage(self.full_screen_img)
        
        self.canvas = tk.Canvas(self, cursor="tcross", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.create_image(0, 0, image=self.bg_photo, anchor="nw")
        
        self.tip_rect = self.canvas.create_rectangle(0, 0, 110, 30, fill="#212121", outline="white", width=1, state="hidden")
        self.tip_text = self.canvas.create_text(0, 0, text="", fill="white", font=("Arial", 10, "bold"), state="hidden")
        self.bind_events()
        
    def bind_events(self):
        self.canvas.bind("<Motion>", self.on_mouse_move)
        self.canvas.bind("<ButtonPress-1>", self.on_click)
        self.bind("<Escape>", self.cancel)
        
    def on_mouse_move(self, event):
        x = max(0, min(event.x, self.screen_w - 1))
        y = max(0, min(event.y, self.screen_h - 1))
        pixel = self.full_screen_img.getpixel((x, y))
        r, g, b = pixel[:3]
        hex_color = f"#{r:02X}{g:02X}{b:02X}"
        
        tx = x + 15
        ty = y + 15
        if tx + 110 > self.screen_w:
            tx = x - 125
        if ty + 30 > self.screen_h:
            ty = y - 45
            
        self.canvas.coords(self.tip_rect, tx, ty, tx + 110, ty + 30)
        self.canvas.itemconfig(self.tip_rect, fill=hex_color, outline="white" if (r+g+b)/3 < 128 else "black", state="normal")
        
        text_color = "white" if (r+g+b)/3 < 128 else "black"
        self.canvas.coords(self.tip_text, tx + 55, ty + 15)
        self.canvas.itemconfig(self.tip_text, text=hex_color, fill=text_color, state="normal")
        
    def on_click(self, event):
        x = max(0, min(event.x, self.screen_w - 1))
        y = max(0, min(event.y, self.screen_h - 1))
        pixel = self.full_screen_img.getpixel((x, y))
        r, g, b = pixel[:3]
        hex_color = f"#{r:02X}{g:02X}{b:02X}"
        self.destroy()
        self.on_picked(hex_color)
        
    def cancel(self, event=None):
        self.destroy()
        self.parent.deiconify()


# OCR Result viewer and editor
class OCRResultWindow(ctk.CTkToplevel):
    def __init__(self, parent, text):
        super().__init__(parent)
        self.title("Extracted Text (OCR) 🔤")
        self.geometry("520x420")
        self.attributes("-topmost", True)
        
        lbl = ctk.CTkLabel(self, text="Extracted Text from Screen Capture:", font=ctk.CTkFont(size=14, weight="bold"))
        lbl.pack(pady=12)
        
        self.textbox = ctk.CTkTextbox(self, font=("Segoe UI", 11))
        self.textbox.pack(fill="both", expand=True, padx=20, pady=10)
        self.textbox.insert("1.0", text)
        
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", pady=15, padx=20)
        
        btn_copy = ctk.CTkButton(btn_frame, text="Copy to Clipboard 📋", command=self.copy_text)
        btn_copy.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        btn_close = ctk.CTkButton(btn_frame, text="Close", fg_color="#dc3545", hover_color="#c82333", command=self.destroy)
        btn_close.pack(side="right", fill="x", expand=True, padx=(5, 0))
        
    def copy_text(self):
        text = self.textbox.get("1.0", "end-1c")
        self.clipboard_clear()
        self.clipboard_append(text)
        messagebox.showinfo("Success", "Text copied to clipboard!")


# Main Image Editor / Preview Window
class EditorWindow(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("PrintPulse Screenshot Editor 🎨")
        self.geometry("1120x720")
        self.setup_ui()
        self.protocol("WM_DELETE_WINDOW", self.hide_window)
        
    def setup_ui(self):
        self.toolbar = ctk.CTkFrame(self, height=60)
        self.toolbar.pack(fill="x", padx=15, pady=10)
        
        self.btn_copy = ctk.CTkButton(
            self.toolbar, text="Copy to Clipboard 📋", font=ctk.CTkFont(size=13),
            height=40, width=150, state="disabled", fg_color="#333333", text_color="gray",
            command=self.copy_to_clipboard
        )
        self.btn_copy.pack(side="left", padx=5, pady=12)
        
        self.btn_save = ctk.CTkButton(
            self.toolbar, text="Save to File 💾", font=ctk.CTkFont(size=13),
            height=40, width=150, state="disabled", fg_color="#333333", text_color="gray",
            command=self.save_screenshot
        )
        self.btn_save.pack(side="left", padx=5, pady=12)

        self.btn_share = ctk.CTkButton(
            self.toolbar, text="Upload & Share 🔗", font=ctk.CTkFont(size=13),
            height=40, width=150, state="disabled", fg_color="#333333", text_color="gray",
            command=self.share_screenshot
        )
        self.btn_share.pack(side="left", padx=5, pady=12)

        self.btn_pdf = ctk.CTkButton(
            self.toolbar, text="PDF & Image Tools 📄", font=ctk.CTkFont(size=13),
            height=40, width=170, fg_color=["#3b8ed0", "#1f538d"], text_color="white",
            command=self.open_pdf_utils_window
        )
        self.btn_pdf.pack(side="left", padx=5, pady=12)
        
        self.main_layout = ctk.CTkFrame(self, fg_color="transparent")

    def open_pdf_utils_window(self):
        if hasattr(self, 'pdf_window') and self.pdf_window.winfo_exists():
            self.pdf_window.lift()
        else:
            self.pdf_window = PDFUtilsWindow(self)
        self.main_layout.pack(fill="both", expand=True, padx=15, pady=(0, 5))
        
        # Left markup options panel
        self.markup_panel = ctk.CTkScrollableFrame(self.main_layout, width=200)
        self.markup_panel.pack(side="left", fill="y", padx=(0, 10))
        
        lbl_panel = ctk.CTkLabel(self.markup_panel, text="Drawing Tools ✏️", font=ctk.CTkFont(size=14, weight="bold"))
        lbl_panel.pack(pady=(10, 8))
        
        # Drawing tools list: (tool_name, display_label, icon_name, color)
        self.drawing_tools = [
            ("None", "Cursor (Select)", "select", "#00ffcc"),
            ("Pen", "Freehand Pen", "pen", "#ffcc00"),
            ("Highlighter", "Highlight Marker", "highlighter", "#9966ff"),
            ("Rectangle", "Draw Rectangle", "rectangle", "#33cc33"),
            ("Arrow", "Draw Arrow", "arrow", "#ff3333"),
            ("Blur", "Blur / Pixelate", "blur", "#ff33cc"),
            ("Text", "Text Annotation", "text", "#ff9900"),
            ("Hand", "Hand Pointer", "hand", "#00ccff"),
            ("Badge", "Step Badge", "badge", "#ff5555"),
            ("Magnifier", "Detail Magnifier", "magnifier", "#00ffcc"),
            ("Emoji", "Emoji Sticker", "emoji", "#ffcc00")
        ]
        
        self.tool_buttons = {}
        
        for tool_name, display_label, icon_name, color in self.drawing_tools:
            btn = ctk.CTkButton(
                self.markup_panel,
                text=display_label,
                image=self.parent.editor_icons[icon_name],
                compound="left",
                anchor="w",
                height=34,
                fg_color="transparent",
                text_color="white",
                hover_color="#2c2c2c",
                command=lambda name=tool_name: self.select_tool(name)
            )
            btn.pack(fill="x", padx=5, pady=3)
            self.tool_buttons[tool_name] = btn
            
        self.update_tool_highlights()
        
        # Reset Badge counter button
        self.btn_reset_badge = ctk.CTkButton(self.markup_panel, text="Reset Badge Count", width=140, height=24, fg_color="#3c3f41", text_color="white", command=self.parent.reset_badge_count)
        self.btn_reset_badge.pack(padx=10, pady=(8, 12))
        
        lbl_color = ctk.CTkLabel(self.markup_panel, text="Color Palette 🎨", font=ctk.CTkFont(size=13, weight="bold"))
        lbl_color.pack(pady=(5, 5))
        
        self.color_menu = ctk.CTkOptionMenu(
            self.markup_panel, variable=self.parent.current_color,
            values=["red", "green", "blue", "yellow", "black", "white"]
        )
        self.color_menu.pack(padx=10, pady=5, fill="x")
        
        self.btn_undo = ctk.CTkButton(self.markup_panel, text="Undo last ↩️", fg_color="#3c3f41", text_color="white", command=self.parent.undo_last_drawing)
        self.btn_undo.pack(padx=10, pady=(20, 5), fill="x")
        
        self.btn_clear = ctk.CTkButton(self.markup_panel, text="Clear All 🗑️", fg_color="#dc3545", hover_color="#c82333", text_color="white", command=self.parent.clear_all_drawings)
        self.btn_clear.pack(padx=10, pady=5, fill="x")
        
        # Watermark Frame
        lbl_watermark = ctk.CTkLabel(self.markup_panel, text="Watermark Settings 🏷️", font=ctk.CTkFont(size=13, weight="bold"))
        lbl_watermark.pack(pady=(15, 5))
        
        self.watermark_enabled = ctk.BooleanVar(value=False)
        self.chk_watermark = ctk.CTkCheckBox(self.markup_panel, text="Enable Watermark", variable=self.watermark_enabled, font=ctk.CTkFont(size=11))
        self.chk_watermark.pack(padx=10, pady=5, fill="x")
        
        self.txt_watermark = ctk.CTkEntry(self.markup_panel, placeholder_text="Watermark text...", font=ctk.CTkFont(size=11), height=24)
        self.txt_watermark.insert(0, "Venkat Windows Tool Kit")
        self.txt_watermark.pack(padx=10, pady=5, fill="x")
        
        # Right Gallery Sidebar Panel
        self.gallery_panel = ctk.CTkFrame(self.main_layout, width=140)
        self.gallery_panel.pack(side="right", fill="y", padx=(10, 0))
        self.gallery_panel.pack_propagate(False)
        
        lbl_gallery = ctk.CTkLabel(self.gallery_panel, text="Gallery History 📂", font=ctk.CTkFont(size=12, weight="bold"))
        lbl_gallery.pack(pady=(12, 6))
        
        self.gallery_scroll = ctk.CTkScrollableFrame(self.gallery_panel, fg_color="transparent")
        self.gallery_scroll.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Center preview board
        self.preview_frame = ctk.CTkFrame(self.main_layout)
        self.preview_frame.pack(side="left", fill="both", expand=True)
        
        self.preview_canvas = tk.Canvas(self.preview_frame, bg="#1a1a1a", highlightthickness=0)
        self.preview_canvas.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.preview_canvas.create_text(
            350, 200, text="No screenshot loaded.\nCapture an image or window to start editing!",
            fill="gray", font=("Arial", 14, "italic"), justify="center", tags="placeholder"
        )
        
        # Bind drawing events
        self.preview_canvas.bind("<ButtonPress-1>", self.parent.on_draw_start)
        self.preview_canvas.bind("<B1-Motion>", self.parent.on_draw_drag)
        self.preview_canvas.bind("<ButtonRelease-1>", self.parent.on_draw_end)
        
        # Bind interactive items dragging events
        self.preview_canvas.tag_bind("movable_item", "<ButtonPress-1>", self.parent.on_item_press)
        self.preview_canvas.tag_bind("movable_item", "<B1-Motion>", self.parent.on_item_drag)
        self.preview_canvas.tag_bind("movable_item", "<ButtonRelease-1>", self.parent.on_item_release)
        self.preview_canvas.tag_bind("movable_item", "<Double-Button-1>", lambda e: self.parent.delete_active_item())
        self.preview_canvas.tag_bind("movable_item", "<Button-3>", self.parent.on_item_right_click)
        
        # Bind MouseWheel to canvas for scroll-to-rotate support
        self.preview_canvas.bind("<MouseWheel>", self.parent.on_canvas_scroll)
        
        # Bind keyboard Delete and Backspace keys to canvas
        self.preview_canvas.bind("<Delete>", self.parent.on_key_delete)
        self.preview_canvas.bind("<BackSpace>", self.parent.on_key_delete)
        
        # Bind canvas Configure for window resize layout recalculations
        self.preview_canvas.bind("<Configure>", self.parent.on_canvas_configure)
        
    def select_tool(self, tool_name):
        self.parent.current_tool.set(tool_name)
        self.update_tool_highlights()
        
    def update_tool_highlights(self):
        active_tool = self.parent.current_tool.get()
        for name, btn in self.tool_buttons.items():
            if name == active_tool:
                btn.configure(fg_color="#1f538d", hover_color="#2464a0")
            else:
                btn.configure(fg_color="transparent", hover_color="#2c2c2c")
                
    def load_screenshot(self, img):
        self.btn_copy.configure(state="normal", fg_color=["#3b8ed0", "#1f538d"], text_color="white")
        self.btn_save.configure(state="normal", fg_color=["#3b8ed0", "#1f538d"], text_color="white")
        self.btn_share.configure(state="normal", fg_color=["#10b981", "#059669"], text_color="white")

    def share_screenshot(self):
        baked = self.parent.get_baked_screenshot()
        if not baked:
            return
            
        self.btn_share.configure(state="disabled", text="Uploading... ⏳")
        self.update()
        
        def do_upload():
            import urllib.request
            import urllib.parse
            import json
            import base64
            import io
            import webbrowser
            
            try:
                buffer = io.BytesIO()
                baked.save(buffer, format="PNG")
                img_b64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
                
                url = "https://api.imgur.com/3/image"
                headers = {
                    "Authorization": "Client-ID 544cc6e65b5c15f",
                    "Content-Type": "application/x-www-form-urlencoded"
                }
                
                data = urllib.parse.urlencode({"image": img_b64}).encode('utf-8')
                
                req = urllib.request.Request(url, data=data, headers=headers, method="POST")
                with urllib.request.urlopen(req) as response:
                    res_data = json.loads(response.read().decode('utf-8'))
                    link = res_data["data"]["link"]
                    
                def success():
                    self.clipboard_clear()
                    self.clipboard_append(link)
                    self.btn_share.configure(state="normal", text="Upload & Share 🔗")
                    messagebox.showinfo("Success", f"Screenshot uploaded successfully!\n\nLink: {link}\n\n(Link copied to clipboard!)", parent=self)
                    webbrowser.open(link)
                    
                self.after(0, success)
                
            except Exception as e:
                def fail(err_msg=str(e)):
                    self.btn_share.configure(state="normal", text="Upload & Share 🔗")
                    messagebox.showerror("Upload Failed", f"Failed to upload screenshot to Imgur:\n{err_msg}", parent=self)
                self.after(0, fail)
                
        threading.Thread(target=do_upload, daemon=True).start()
        
    def copy_to_clipboard(self):
        baked = self.parent.get_baked_screenshot()
        if baked:
            success = copy_image_to_clipboard(baked)
            if success:
                messagebox.showinfo("Success", "Copied to clipboard! You can paste it directly using Ctrl+V.")
                
    def save_screenshot(self):
        baked = self.parent.get_baked_screenshot()
        if baked:
            file_path = filedialog.asksaveasfilename(
                title="Save Screenshot", defaultextension=".png",
                filetypes=[("PNG Image", "*.png"), ("JPEG Image", "*.jpg"), ("All Files", "*.*")]
            )
            if file_path:
                baked.save(file_path)
                self.parent.refresh_gallery()
                messagebox.showinfo("Success", f"Saved successfully to:\n{file_path}")
                
    def hide_window(self):
        self.withdraw()


class PDFUtilsWindow(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("PDF & Image Utilities")
        self.geometry("820x540")
        self.resizable(False, False)
        self.attributes("-topmost", True)
        self.configure(fg_color="#1a1a1a")
        
        # Grid layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        # Title Label
        title_lbl = ctk.CTkLabel(self, text="📄 PDF & Image Converter Tools", font=ctk.CTkFont(size=18, weight="bold"))
        title_lbl.pack(pady=(15, 5), padx=20, anchor="w")
        
        # Main Scrollable Frame
        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent", width=780, height=440)
        scroll.pack(fill="both", expand=True, padx=15, pady=(5, 15))
        scroll.grid_columnconfigure(0, weight=1)
        scroll.grid_columnconfigure(1, weight=1)

        # Panel 1: Image to PDF
        p1 = ctk.CTkFrame(scroll, corner_radius=10, fg_color="#242424")
        p1.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        p1.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(p1, text="🖼️ Convert Images to PDF", font=ctk.CTkFont(size=14, weight="bold")).grid(row=0, column=0, padx=15, pady=(10, 5), sticky="w")
        ctk.CTkLabel(p1, text="Compile multiple image files (PNG, JPG) sequentially into a PDF.", text_color="gray", font=ctk.CTkFont(size=11)).grid(row=1, column=0, padx=15, pady=(0, 10), sticky="w")
        
        self.lbl_img2pdf_status = ctk.CTkLabel(p1, text="No files selected", text_color="gray", font=ctk.CTkFont(size=11))
        self.lbl_img2pdf_status.grid(row=2, column=0, padx=15, pady=(0, 10), sticky="w")
        
        self.img2pdf_paths = []
        def select_images():
            from tkinter import filedialog
            files = filedialog.askopenfilenames(filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp")], parent=self)
            if files:
                self.img2pdf_paths = list(files)
                self.lbl_img2pdf_status.configure(text=f"{len(files)} file(s) selected", text_color="#10b981")
        
        def run_img2pdf():
            if not self.img2pdf_paths:
                messagebox.showerror("Error", "Please select images first!", parent=self)
                return
            from tkinter import filedialog
            out_pdf = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF Files", "*.pdf")], parent=self)
            if not out_pdf:
                return
            try:
                from PIL import Image
                pil_images = []
                for p in self.img2pdf_paths:
                    img = Image.open(p)
                    if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
                        bg = Image.new('RGB', img.size, (255, 255, 255))
                        bg.paste(img, mask=img.split()[3] if img.mode == 'RGBA' else None)
                        pil_images.append(bg)
                    else:
                        pil_images.append(img.convert('RGB'))
                if pil_images:
                    pil_images[0].save(out_pdf, save_all=True, append_images=pil_images[1:])
                    messagebox.showinfo("Success", f"Successfully converted and saved PDF to:\n{out_pdf}", parent=self)
                    self.img2pdf_paths = []
                    self.lbl_img2pdf_status.configure(text="No files selected", text_color="gray")
            except Exception as ex:
                messagebox.showerror("Error", f"Failed to convert: {ex}", parent=self)
                
        btn_sel = ctk.CTkButton(p1, text="Browse Images...", width=140, command=select_images)
        btn_sel.grid(row=3, column=0, padx=15, pady=(0, 10), sticky="w")
        btn_conv = ctk.CTkButton(p1, text="Convert to PDF", fg_color="#10b981", hover_color="#059669", font=ctk.CTkFont(weight="bold"), command=run_img2pdf)
        btn_conv.grid(row=4, column=0, padx=15, pady=(0, 15), sticky="ew")

        # Panel 2: Merge Images
        p2 = ctk.CTkFrame(scroll, corner_radius=10, fg_color="#242424")
        p2.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        p2.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(p2, text="🥞 Merge Images", font=ctk.CTkFont(size=14, weight="bold")).grid(row=0, column=0, padx=15, pady=(10, 5), sticky="w")
        ctk.CTkLabel(p2, text="Combine multiple images side-by-side or top-to-bottom.", text_color="gray", font=ctk.CTkFont(size=11)).grid(row=1, column=0, padx=15, pady=(0, 10), sticky="w")
        
        self.lbl_mergeimg_status = ctk.CTkLabel(p2, text="No files selected", text_color="gray", font=ctk.CTkFont(size=11))
        self.lbl_mergeimg_status.grid(row=2, column=0, padx=15, pady=(0, 10), sticky="w")
        
        self.mergeimg_paths = []
        def select_merge_images():
            from tkinter import filedialog
            files = filedialog.askopenfilenames(filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp")], parent=self)
            if files:
                self.mergeimg_paths = list(files)
                self.lbl_mergeimg_status.configure(text=f"{len(files)} file(s) selected", text_color="#10b981")
                
        def run_merge_images():
            if not self.mergeimg_paths:
                messagebox.showerror("Error", "Please select images first!", parent=self)
                return
            from tkinter import filedialog
            out_img = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG Image", "*.png"), ("JPEG Image", "*.jpg")], parent=self)
            if not out_img:
                return
            try:
                from PIL import Image
                pil_images = [Image.open(p) for p in self.mergeimg_paths]
                orientation = self.opt_orientation.get().lower()
                widths, heights = zip(*(img.size for img in pil_images))
                
                if "horizontal" in orientation:
                    total_width = sum(widths)
                    max_height = max(heights)
                    new_img = Image.new('RGBA', (total_width, max_height), (255, 255, 255, 0))
                    x_offset = 0
                    for img in pil_images:
                        new_img.paste(img, (x_offset, 0))
                        x_offset += img.size[0]
                else:
                    max_width = max(widths)
                    total_height = sum(heights)
                    new_img = Image.new('RGBA', (max_width, total_height), (255, 255, 255, 0))
                    y_offset = 0
                    for img in pil_images:
                        new_img.paste(img, (0, y_offset))
                        y_offset += img.size[1]
                
                new_img.save(out_img)
                messagebox.showinfo("Success", f"Successfully merged and saved image to:\n{out_img}", parent=self)
                self.mergeimg_paths = []
                self.lbl_mergeimg_status.configure(text="No files selected", text_color="gray")
            except Exception as ex:
                messagebox.showerror("Error", f"Failed to merge: {ex}", parent=self)

        btn_sel_merge = ctk.CTkButton(p2, text="Browse Images...", width=140, command=select_merge_images)
        btn_sel_merge.grid(row=3, column=0, padx=15, pady=(0, 10), sticky="w")
        
        opt_frame = ctk.CTkFrame(p2, fg_color="transparent")
        opt_frame.grid(row=4, column=0, padx=15, pady=(0, 10), sticky="w")
        ctk.CTkLabel(opt_frame, text="Orientation:").pack(side="left", padx=(0, 5))
        self.opt_orientation = ctk.CTkOptionMenu(opt_frame, width=120, values=["Vertical", "Horizontal"])
        self.opt_orientation.pack(side="left")
        
        btn_merge = ctk.CTkButton(p2, text="Merge Images", fg_color="#8b5cf6", hover_color="#7c3aed", font=ctk.CTkFont(weight="bold"), command=run_merge_images)
        btn_merge.grid(row=5, column=0, padx=15, pady=(0, 15), sticky="ew")

        # Panel 3: PDF to Image
        p3 = ctk.CTkFrame(scroll, corner_radius=10, fg_color="#242424")
        p3.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        p3.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(p3, text="📑 Convert PDF to Images", font=ctk.CTkFont(size=14, weight="bold")).grid(row=0, column=0, padx=15, pady=(10, 5), sticky="w")
        ctk.CTkLabel(p3, text="Extract all PDF pages as standalone high-quality PNG images.", text_color="gray", font=ctk.CTkFont(size=11)).grid(row=1, column=0, padx=15, pady=(0, 10), sticky="w")
        
        self.lbl_pdf2img_status = ctk.CTkLabel(p3, text="No PDF selected", text_color="gray", font=ctk.CTkFont(size=11))
        self.lbl_pdf2img_status.grid(row=2, column=0, padx=15, pady=(0, 10), sticky="w")
        
        self.pdf2img_path = ""
        def select_pdf():
            from tkinter import filedialog
            f = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")], parent=self)
            if f:
                self.pdf2img_path = f
                self.lbl_pdf2img_status.configure(text=os.path.basename(f), text_color="#10b981")
                
        def run_pdf2img():
            if not self.pdf2img_path:
                messagebox.showerror("Error", "Please select a PDF file first!", parent=self)
                return
            from tkinter import filedialog
            out_dir = filedialog.askdirectory(parent=self)
            if not out_dir:
                return
            try:
                import fitz
                doc = fitz.open(self.pdf2img_path)
                for i, page in enumerate(doc):
                    pix = page.get_pixmap(dpi=150)
                    pix.save(os.path.join(out_dir, f"page_{i+1}.png"))
                messagebox.showinfo("Success", f"Extracted {len(doc)} pages as PNGs to:\n{out_dir}", parent=self)
                self.pdf2img_path = ""
                self.lbl_pdf2img_status.configure(text="No PDF selected", text_color="gray")
            except Exception as ex:
                messagebox.showerror("Error", f"Failed to extract pages: {ex}", parent=self)
                
        btn_sel_pdf = ctk.CTkButton(p3, text="Browse PDF...", width=140, command=select_pdf)
        btn_sel_pdf.grid(row=3, column=0, padx=15, pady=(0, 10), sticky="w")
        
        btn_extract = ctk.CTkButton(p3, text="Extract Pages", fg_color="#3b82f6", hover_color="#2563eb", font=ctk.CTkFont(weight="bold"), command=run_pdf2img)
        btn_extract.grid(row=4, column=0, padx=15, pady=(0, 15), sticky="ew")

        # Panel 4: Merge PDFs
        p4 = ctk.CTkFrame(scroll, corner_radius=10, fg_color="#242424")
        p4.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
        p4.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(p4, text="📚 Merge PDF Files", font=ctk.CTkFont(size=14, weight="bold")).grid(row=0, column=0, padx=15, pady=(10, 5), sticky="w")
        ctk.CTkLabel(p4, text="Combine multiple PDF documents sequentially into one.", text_color="gray", font=ctk.CTkFont(size=11)).grid(row=1, column=0, padx=15, pady=(0, 10), sticky="w")
        
        self.lbl_mergepdf_status = ctk.CTkLabel(p4, text="No PDFs selected", text_color="gray", font=ctk.CTkFont(size=11))
        self.lbl_mergepdf_status.grid(row=2, column=0, padx=15, pady=(0, 10), sticky="w")
        
        self.mergepdf_paths = []
        def select_merge_pdfs():
            from tkinter import filedialog
            files = filedialog.askopenfilenames(filetypes=[("PDF Files", "*.pdf")], parent=self)
            if files:
                self.mergepdf_paths = list(files)
                self.lbl_mergepdf_status.configure(text=f"{len(files)} file(s) selected", text_color="#10b981")
                
        def run_merge_pdfs():
            if not self.mergepdf_paths:
                messagebox.showerror("Error", "Please select PDFs first!", parent=self)
                return
            from tkinter import filedialog
            out_pdf = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF Files", "*.pdf")], parent=self)
            if not out_pdf:
                return
            try:
                from pypdf import PdfMerger
                merger = PdfMerger()
                for p in self.mergepdf_paths:
                    merger.append(p)
                merger.write(out_pdf)
                merger.close()
                messagebox.showinfo("Success", f"Successfully merged and saved PDF to:\n{out_pdf}", parent=self)
                self.mergepdf_paths = []
                self.lbl_mergepdf_status.configure(text="No PDFs selected", text_color="gray")
            except Exception as ex:
                messagebox.showerror("Error", f"Failed to merge PDFs: {ex}", parent=self)
                
        btn_sel_merge_pdf = ctk.CTkButton(p4, text="Browse PDFs...", width=140, command=select_merge_pdfs)
        btn_sel_merge_pdf.grid(row=3, column=0, padx=15, pady=(0, 10), sticky="w")
        btn_merge_pdf = ctk.CTkButton(p4, text="Merge PDFs", fg_color="#ef4444", hover_color="#dc2626", font=ctk.CTkFont(weight="bold"), command=run_merge_pdfs)
        btn_merge_pdf.grid(row=4, column=0, padx=15, pady=(0, 15), sticky="ew")


# Main Floating Dock Widget (System Capsule Bar)
class FloatingDock(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.configure(fg_color="#1e1e1e")
        self.config(highlightbackground="#1f538d", highlightthickness=2)
        
        w = 592
        h = 52
        screen_w = self.winfo_screenwidth()
        self.geometry(f"{w}x{h}+{screen_w // 2 - w // 2}+20")
        
        self._drag_x = 0
        self._drag_y = 0
        
        # Markup variables
        self.current_screenshot = None
        self.history_stack = []
        self.current_tool = ctk.StringVar(value="None")
        self.current_color = ctk.StringVar(value="red")
        
        self.draw_start_x = 0
        self.draw_start_y = 0
        self.last_draw_x = 0
        self.last_draw_y = 0
        self.temp_shape_id = None
        self.scale_ratio = 1.0
        self.img_x_offset = 0
        self.img_y_offset = 0
        self.bg_image_id = None
        
        # Placed interactive items registry
        self.current_step_number = 1
        self.hand_data = {}
        self.badge_data = {}
        self.text_data = {}
        self.zoom_data = {}
        self.emoji_data = {}
        self.gallery_photos = []
        
        # Interactive items dragging variables
        self.is_dragging_item = False
        self.dragged_item_tag = None
        self.drag_start_x = 0
        self.drag_start_y = 0
        self.active_context_item_tag = None
        
        self.icons = {}
        self.editor_icons = {}
        self.setup_icons()
        
        self.setup_ui()
        self.bind_drag()
        
        self.editor = EditorWindow(self)
        self.editor.withdraw()
        
        self.tray_icon = None
        self.setup_tray_icon()
        self.setup_global_hotkey()
        
        self.refresh_gallery()
        
    def setup_icons(self):
        # Setup Float Dock icons
        icon_definitions = [
            ("camera", "#00ffcc"),
            ("timer", "#ffcc00"),
            ("fullscreen", "#ff3366"),
            ("window", "#9966ff"),
            ("scroll", "#33cc33"),
            ("record", "#ff3333"),
            ("dropper", "#ff33cc"),
            ("ocr", "#ff9900"),
            ("history", "#00ffcc"),
            ("pdfutils", "#a7f3d0"),
            ("editor", "#00ccff"),
            ("close", "#ff5555")
        ]
        for name, color in icon_definitions:
            png_path = get_asset_path(f"{name}.png")
            if os.path.exists(png_path):
                try:
                    pil_img = Image.open(png_path).resize((32, 32), Image.Resampling.LANCZOS)
                    self.icons[name] = ImageTk.PhotoImage(pil_img)
                    continue
                except Exception as e:
                    print(f"Error loading realistic icon {name}.png: {e}")
                    
            pil_img = create_vector_icon(name, color)
            self.icons[name] = ImageTk.PhotoImage(pil_img)
            
        # Setup Editor sidebar drawing tool icons
        editor_icon_definitions = [
            ("select", "#00ffcc"),
            ("pen", "#ffcc00"),
            ("highlighter", "#9966ff"),
            ("rectangle", "#33cc33"),
            ("arrow", "#ff3333"),
            ("blur", "#ff33cc"),
            ("text", "#ff9900"),
            ("hand", "#00ccff"),
            ("badge", "#ff5555"),
            ("magnifier", "#00ffcc"),
            ("emoji", "#ffcc00")
        ]
        for name, color in editor_icon_definitions:
            png_path = get_asset_path(f"{name}.png")
            if os.path.exists(png_path):
                try:
                    pil_img = Image.open(png_path).resize((20, 20), Image.Resampling.LANCZOS)
                    self.editor_icons[name] = ImageTk.PhotoImage(pil_img)
                    continue
                except Exception as e:
                    print(f"Error loading realistic editor icon {name}.png: {e}")
                    
            pil_img = create_editor_vector_icon(name, color)
            self.editor_icons[name] = ImageTk.PhotoImage(pil_img)
            
    def setup_ui(self):
        self.top_bar = tk.Frame(self, bg="#1e1e1e", height=48)
        self.top_bar.pack(fill="x", side="top", padx=5)
        
        drag_lbl = tk.Label(self.top_bar, text=" ⋮ ", bg="#1e1e1e", fg="#555555", font=("Arial", 14, "bold"), cursor="fleur")
        drag_lbl.pack(side="left", padx=(5, 10))
        drag_lbl.bind("<ButtonPress-1>", self.start_drag)
        drag_lbl.bind("<B1-Motion>", self.drag_motion)
        
        buttons = [
            ("camera", self.start_area_capture),
            ("timer", self.start_delayed_capture),
            ("fullscreen", self.start_fullscreen_capture),
            ("window", self.start_window_capture),
            ("scroll", self.start_scroll_capture),
            ("record", self.start_gif_recorder),
            ("dropper", self.start_color_picker),
            ("ocr", self.start_ocr_grabber),
            ("history", self.toggle_history_panel),
            ("pdfutils", self.open_pdf_utils_window),
            ("editor", self.open_editor_window),
            ("close", self.hide_dock)
        ]
        
        for name, cmd in buttons:
            btn = tk.Button(
                self.top_bar, image=self.icons[name],
                bg="#1e1e1e", activebackground="#2c2c2c",
                relief="flat", width=36, height=36, cursor="hand2", command=cmd
            )
            btn.pack(side="left", padx=4, pady=6)

    def toggle_history_panel(self):
        if hasattr(self, 'history_frame') and self.history_frame.winfo_viewable():
            self.history_frame.pack_forget()
            w = 592
            h = 52
            self.geometry(f"{w}x{h}")
        else:
            self.show_dock_history()

    def show_dock_history(self):
        if not hasattr(self, 'history_frame'):
            self.history_frame = ctk.CTkFrame(self, fg_color="#1a1a1a", height=180)
            
            lbl = ctk.CTkLabel(self.history_frame, text="🕒 Capture History (Recent)", font=ctk.CTkFont(size=12, weight="bold"))
            lbl.pack(pady=(5, 5), padx=10, anchor="w")
            
            self.dock_scroll = ctk.CTkScrollableFrame(self.history_frame, orientation="horizontal", height=120, fg_color="transparent")
            self.dock_scroll.pack(fill="both", expand=True, padx=5, pady=(0, 5))
            
        for child in self.dock_scroll.winfo_children():
            child.destroy()
            
        pictures_dir = os.path.join(os.path.expanduser("~"), "Pictures")
        captures_dir = os.path.join(pictures_dir, "VenkatCaptures")
        if os.path.exists(captures_dir):
            files = [os.path.join(captures_dir, f) for f in os.listdir(captures_dir) if f.endswith(".png")]
            files.sort(key=os.path.getmtime, reverse=True)
            files = files[:12]
            
            self.dock_gallery_photos = []
            for f in files:
                try:
                    img = Image.open(f)
                    img.thumbnail((100, 75))
                    photo = ImageTk.PhotoImage(img)
                    self.dock_gallery_photos.append(photo)
                    
                    item_f = ctk.CTkFrame(self.dock_scroll, fg_color="transparent", width=110)
                    item_f.pack(side="left", padx=6, fill="y")
                    
                    btn = tk.Button(
                        item_f, image=photo, relief="flat",
                        bg="#2a2a2a", activebackground="#3a3a3a", cursor="hand2",
                        command=lambda path=f: self.load_screenshot_from_gallery(path)
                    )
                    btn.pack(pady=(2, 2))
                    
                    basename = os.path.basename(f)
                    time_str = basename.replace("cap_", "").replace(".png", "")
                    if len(time_str) >= 15:
                        formatted_time = f"{time_str[9:11]}:{time_str[11:13]}"
                        lbl_time = ctk.CTkLabel(item_f, text=formatted_time, font=ctk.CTkFont(size=9), text_color="gray")
                        lbl_time.pack()
                except Exception as e:
                    print(e)
                    
        self.history_frame.pack(fill="both", expand=True, padx=5, pady=(0, 5))
        w = 592
        h = 240
        self.geometry(f"{w}x{h}")

    def open_pdf_utils_window(self):
        if hasattr(self, 'pdf_window') and self.pdf_window.winfo_exists():
            self.pdf_window.lift()
        else:
            self.pdf_window = PDFUtilsWindow(self)
            
    def bind_drag(self):
        self.bind("<ButtonPress-1>", self.start_drag)
        self.bind("<B1-Motion>", self.drag_motion)
        
    def start_drag(self, event):
        self._drag_x = event.x
        self._drag_y = event.y
        
    def drag_motion(self, event):
        x = self.winfo_x() - self._drag_x + event.x
        y = self.winfo_y() - self._drag_y + event.y
        self.geometry(f"+{x}+{y}")
        
    def start_area_capture(self):
        self.withdraw()
        self.editor.withdraw()
        self.update_idletasks()
        self.after(350, lambda: RegionSelector(self, self.on_area_captured, "Drag to select screenshot area"))
        
    def start_fullscreen_capture(self):
        self.withdraw()
        self.editor.withdraw()
        self.update_idletasks()
        self.after(350, self._do_fullscreen_capture)

    def _do_fullscreen_capture(self):
        try:
            img = ImageGrab.grab()
            self.deiconify()
            self.current_screenshot = img
            self.history_stack.clear()
            self.auto_save_screenshot()
            copy_image_to_clipboard(img)
            self.open_editor_window()
            self.show_preview(img)
        except Exception as e:
            self.deiconify()
            messagebox.showerror("Error", f"Failed to capture fullscreen:\n{e}")
        
    def on_area_captured(self, img, crop_box):
        self.deiconify()
        self.current_screenshot = img
        self.history_stack.clear()
        
        self.auto_save_screenshot()
        copy_image_to_clipboard(img)
        self.open_editor_window()
        self.show_preview(img)
        
    def auto_save_screenshot(self):
        if not self.current_screenshot:
            return
        pictures_dir = os.path.join(os.path.expanduser("~"), "Pictures")
        captures_dir = os.path.join(pictures_dir, "VenkatCaptures")
        os.makedirs(captures_dir, exist_ok=True)
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filepath = os.path.join(captures_dir, f"cap_{timestamp}.png")
        self.current_screenshot.save(filepath)
        self.refresh_gallery()

    def refresh_gallery(self):
        if not hasattr(self, 'editor') or not self.editor.winfo_exists():
            return
            
        for child in self.editor.gallery_scroll.winfo_children():
            child.destroy()
            
        pictures_dir = os.path.join(os.path.expanduser("~"), "Pictures")
        captures_dir = os.path.join(pictures_dir, "VenkatCaptures")
        if not os.path.exists(captures_dir):
            return
            
        files = [os.path.join(captures_dir, f) for f in os.listdir(captures_dir) if f.endswith(".png")]
        files.sort(key=os.path.getmtime, reverse=True)
        files = files[:8]
        
        self.gallery_photos.clear()
        
        for f in files:
            try:
                img = Image.open(f)
                img.thumbnail((110, 80))
                photo = ImageTk.PhotoImage(img)
                self.gallery_photos.append(photo)
                
                # Image thumbnail frame
                item_frame = ctk.CTkFrame(self.editor.gallery_scroll, fg_color="transparent")
                item_frame.pack(pady=6, fill="x")
                
                btn = tk.Button(
                    item_frame, image=photo, relief="flat",
                    bg="#2a2a2a", activebackground="#3a3a3a", cursor="hand2",
                    command=lambda path=f: self.load_screenshot_from_gallery(path)
                )
                btn.pack(pady=(0, 2), padx=5)
                btn.bind("<Button-3>", lambda e, path=f: self.show_gallery_context_menu(e, path))
                
                basename = os.path.basename(f)
                time_str = basename.replace("cap_", "").replace(".png", "")
                if len(time_str) >= 15:
                    formatted_time = f"{time_str[9:11]}:{time_str[11:13]}:{time_str[13:15]}"
                    
                    info_row = ctk.CTkFrame(item_frame, fg_color="transparent")
                    info_row.pack(fill="x", padx=5)
                    
                    lbl = ctk.CTkLabel(info_row, text=formatted_time, font=ctk.CTkFont(size=10), text_color="gray")
                    lbl.pack(side="left", padx=(2, 0))
                    
                    btn_del = ctk.CTkButton(
                        info_row, text="🗑️", width=20, height=20, fg_color="transparent",
                        text_color="#ff4d4d", hover_color="#331111", cursor="hand2",
                        command=lambda path=f: self.delete_gallery_item(path)
                    )
                    btn_del.pack(side="right", padx=(0, 2))
            except Exception as e:
                print(f"Error loading gallery thumbnail: {e}")

    def show_gallery_context_menu(self, event, filepath):
        menu = tk.Menu(self.editor, tearoff=0, bg="#212121", fg="white", activebackground="#1f538d", activeforeground="white")
        menu.add_command(label="Delete 🗑️", command=lambda: self.delete_gallery_item(filepath))
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def delete_gallery_item(self, filepath):
        if messagebox.askyesno("Delete Capture", "Are you sure you want to delete this screenshot from history?", parent=self.editor):
            try:
                if os.path.exists(filepath):
                    os.remove(filepath)
                self.refresh_gallery()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete file:\n{e}", parent=self.editor)

    def load_screenshot_from_gallery(self, path):
        try:
            img = Image.open(path)
            self.current_screenshot = img.convert("RGB")
            self.history_stack.clear()
            self.editor.preview_canvas.delete("movable_item")
            self.editor.preview_canvas.delete("active_item_border")
            self.hand_data.clear()
            self.badge_data.clear()
            self.text_data.clear()
            self.zoom_data.clear()
            self.show_preview(self.current_screenshot, save_history=False)
            copy_image_to_clipboard(self.current_screenshot)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load image from gallery:\n{e}")

    def start_delayed_capture(self):
        self.withdraw()
        self.editor.withdraw()
        self.update_idletasks()
        
        countdown_win = tk.Toplevel(self)
        countdown_win.overrideredirect(True)
        countdown_win.attributes("-topmost", True)
        countdown_win.configure(bg="#212121")
        countdown_win.config(highlightbackground="#1f538d", highlightthickness=2)
        
        w, h = 150, 100
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        countdown_win.geometry(f"{w}x{h}+{screen_w // 2 - w // 2}+{screen_h // 2 - h // 2}")
        
        lbl = tk.Label(countdown_win, text="3", bg="#212121", fg="#00ffcc", font=("Arial", 28, "bold"))
        lbl.pack(expand=True)
        countdown_win.update()
        
        def count(ticks):
            if ticks > 0:
                lbl.config(text=str(ticks))
                countdown_win.update()
                self.after(1000, lambda: count(ticks - 1))
            else:
                countdown_win.destroy()
                self.after(150, lambda: RegionSelector(self, self.on_area_captured, "Drag to select screenshot area"))
                
        self.after(1000, lambda: count(2))
        
    def start_window_capture(self):
        self.withdraw()
        self.editor.withdraw()
        self.update_idletasks()
        self.after(350, self._do_window_capture)
        
    def _do_window_capture(self):
        hwnd = ctypes.windll.user32.GetForegroundWindow()
        if hwnd:
            rect = wintypes.RECT()
            ctypes.windll.user32.GetWindowRect(hwnd, ctypes.byref(rect))
            x1, y1, x2, y2 = rect.left, rect.top, rect.right, rect.bottom
            x1, y1 = max(0, x1), max(0, y1)
            full_img = ImageGrab.grab()
            img = full_img.crop((x1, y1, x2, y2))
            self.deiconify()
            self.current_screenshot = img
            self.history_stack.clear()
            self.auto_save_screenshot()
            copy_image_to_clipboard(img)
            self.open_editor_window()
            self.show_preview(img)
        else:
            self.deiconify()
            messagebox.showerror("Error", "No active window found to capture.")
            
    def start_scroll_capture(self):
        self.withdraw()
        self.editor.withdraw()
        self.update_idletasks()
        self.after(350, lambda: RegionSelector(self, self.on_scroll_region_selected, "Select the scrollable page area"))
        
    def on_scroll_region_selected(self, first_frame, crop_box):
        ScrollController(self, crop_box, self.on_scroll_finished, self.on_scroll_cancelled)
        
    def on_scroll_finished(self, stitched_img):
        self.deiconify()
        if stitched_img:
            self.current_screenshot = stitched_img
            self.history_stack.clear()
            self.auto_save_screenshot()
            copy_image_to_clipboard(stitched_img)
            self.open_editor_window()
            self.show_preview(stitched_img)
            
    def on_scroll_cancelled(self):
        self.deiconify()
        
    def start_gif_recorder(self):
        menu = tk.Menu(self, tearoff=0, bg="#1e1e1e", fg="white", activebackground="#10b981", activeforeground="white")
        menu.add_command(label="🎥 Record as MP4 Video", command=lambda: self.launch_recorder(mode="mp4"))
        menu.add_command(label="🖼️ Record as Animated GIF", command=lambda: self.launch_recorder(mode="gif"))
        cursor_x = self.winfo_pointerx()
        cursor_y = self.winfo_pointery()
        try:
            menu.tk_popup(cursor_x, cursor_y)
        finally:
            menu.grab_release()

    def launch_recorder(self, mode="gif"):
        self.recorder_mode = mode
        self.withdraw()
        self.editor.withdraw()
        self.update_idletasks()
        title = "Select area to record (MP4 Video)" if mode == "mp4" else "Select area to record (GIF)"
        self.after(350, lambda: RegionSelector(self, self.on_gif_region_selected, title))
        
    def on_gif_region_selected(self, first_frame, crop_box):
        GIFRecorderController(self, crop_box, self.on_gif_finished)
        
    def on_gif_finished(self, frames):
        self.deiconify()
        if not frames:
            return
            
        pictures_dir = os.path.join(os.path.expanduser("~"), "Pictures")
        captures_dir = os.path.join(pictures_dir, "VenkatCaptures")
        os.makedirs(captures_dir, exist_ok=True)
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        
        self.config(cursor="watch")
        self.update()
        
        mode = getattr(self, 'recorder_mode', 'gif')
        if mode == "mp4":
            output_path = os.path.join(captures_dir, f"rec_{timestamp}.mp4")
            try:
                import cv2
                import numpy as np
                first_frame = frames[0]
                w, h = first_frame.size
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                out = cv2.VideoWriter(output_path, fourcc, 10.0, (w, h))
                for f in frames:
                    img_bgr = cv2.cvtColor(np.array(f), cv2.COLOR_RGB2BGR)
                    out.write(img_bgr)
                out.release()
                
                self.config(cursor="")
                self.clipboard_clear()
                self.clipboard_append(output_path)
                messagebox.showinfo(
                    "Video Saved 🎥", 
                    f"Screen recording compiled successfully!\n\nSaved to:\n{output_path}\n\n(File path copied to clipboard!)"
                )
                os.startfile(output_path)
            except Exception as e:
                self.config(cursor="")
                messagebox.showerror("Error Saving MP4", f"Failed to compile MP4 video:\n{str(e)}")
        else:
            output_path = os.path.join(captures_dir, f"rec_{timestamp}.gif")
            try:
                frames[0].save(
                    output_path, save_all=True, append_images=frames[1:], 
                    duration=100, loop=0, optimize=True
                )
                self.config(cursor="")
                self.clipboard_clear()
                self.clipboard_append(output_path)
                messagebox.showinfo(
                    "GIF Saved 🎥", 
                    f"Screen recording compiled successfully!\n\nSaved to:\n{output_path}\n\n(File path copied to clipboard!)"
                )
                os.startfile(output_path)
            except Exception as e:
                self.config(cursor="")
                messagebox.showerror("Error Saving GIF", f"Failed to compile screen recording:\n{str(e)}")
            
    def start_color_picker(self):
        self.withdraw()
        self.editor.withdraw()
        self.update_idletasks()
        self.after(350, lambda: ColorPickerOverlay(self, self.on_color_picked))
        
    def on_color_picked(self, hex_color):
        self.deiconify()
        self.clipboard_clear()
        self.clipboard_append(hex_color)
        messagebox.showinfo("Color Picked 🧪", f"Hex Color: {hex_color}\nSuccessfully copied to clipboard!")
        
    def start_ocr_grabber(self):
        self.withdraw()
        self.editor.withdraw()
        self.update_idletasks()
        self.after(350, lambda: RegionSelector(self, self.on_ocr_region_captured, "Select text area to extract"))
        
    def on_ocr_region_captured(self, img, crop_box):
        self.deiconify()
        temp_dir = os.path.join(os.environ.get("TEMP", "C:\\Temp"), "pp_ocr_temp.png")
        img.save(temp_dir)
        
        self.config(cursor="watch")
        self.update()
        extracted_text = run_windows_ocr(temp_dir)
        self.config(cursor="")
        
        try:
            os.remove(temp_dir)
        except:
            pass
            
        if extracted_text == "No text found":
            messagebox.showwarning(
                "No Text Found 🔤", 
                "No text was recognized in the selected area.\n\nPlease make sure the selected area contains clear, readable text."
            )
        elif extracted_text.startswith("Error"):
            messagebox.showerror("OCR Failed 🔤", f"Failed to extract text:\n{extracted_text}")
        else:
            self.clipboard_clear()
            self.clipboard_append(extracted_text)
            ocr_window = OCRResultWindow(self, extracted_text)
            ocr_window.focus_force()
            
    def open_editor_window(self):
        self.editor.deiconify()
        self.editor.focus_force()
        self.refresh_gallery()
        if self.current_screenshot:
            self.show_preview(self.current_screenshot, save_history=False)
            
    def show_preview(self, img, save_history=True):
        if save_history:
            self.save_to_history()
            
        pw = self.editor.preview_canvas.winfo_width()
        ph = self.editor.preview_canvas.winfo_height()
        if pw <= 1: pw = 750
        if ph <= 1: ph = 420
        pw -= 20
        ph -= 20
        
        w, h = img.size
        self.scale_ratio = min(pw / w, ph / h, 1.0)
        new_w = int(w * self.scale_ratio)
        new_h = int(h * self.scale_ratio)
        
        display_img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        self.tk_preview = ImageTk.PhotoImage(display_img)
        
        # Load and scale hand photo
        hand_path = get_asset_path("hand_pointer.png")
        if os.path.exists(hand_path):
            try:
                hand_pil = Image.open(hand_path)
                hw, hh = hand_pil.size
                sw = int(hw * self.scale_ratio)
                sh = int(hh * self.scale_ratio)
                if sw < 8: sw = 8
                if sh < 8: sh = 8
                scaled_hand = hand_pil.resize((sw, sh), Image.Resampling.LANCZOS)
                self.editor_hand_photo = ImageTk.PhotoImage(scaled_hand)
            except Exception as e:
                print(f"Error loading hand photo: {e}")
                self.editor_hand_photo = None
        
        # Delete old background image and placeholder
        self.editor.preview_canvas.delete("placeholder")
        if self.bg_image_id:
            self.editor.preview_canvas.delete(self.bg_image_id)
            
        self.img_x_offset = (pw + 20 - new_w) // 2
        self.img_y_offset = (ph + 20 - new_h) // 2
        
        self.bg_image_id = self.editor.preview_canvas.create_image(
            self.img_x_offset, self.img_y_offset, 
            image=self.tk_preview, anchor="nw"
        )
        self.editor.preview_canvas.tag_lower(self.bg_image_id)
        self.editor.load_screenshot(img)
        
        # Reposition items after recalculating ratios
        self.reposition_canvas_items()
        
    def save_to_history(self):
        if self.current_screenshot:
            self.history_stack.append(self.current_screenshot.copy())
            if len(self.history_stack) > 10:
                self.history_stack.pop(0)
                
    def undo_last_drawing(self):
        if self.history_stack:
            self.current_screenshot = self.history_stack.pop()
            self.show_preview(self.current_screenshot, save_history=False)
            copy_image_to_clipboard(self.current_screenshot)
            
    def clear_all_drawings(self):
        if self.history_stack:
            self.current_screenshot = self.history_stack[0].copy()
            self.history_stack.clear()
            self.show_preview(self.current_screenshot, save_history=False)
            self.editor.preview_canvas.delete("movable_item")
            self.editor.preview_canvas.delete("active_item_border")
            self.hand_data.clear()
            self.badge_data.clear()
            self.text_data.clear()
            self.zoom_data.clear()
            copy_image_to_clipboard(self.current_screenshot)

    def reset_badge_count(self):
        self.current_step_number = 1
        messagebox.showinfo("Badge Counter", "Step badge sequence reset to ①.")

    def on_canvas_configure(self, event):
        if event.width > 50 and event.height > 50:
            if self.current_screenshot:
                self.show_preview(self.current_screenshot, save_history=False)

    def reposition_canvas_items(self):
        # Reposition Hands
        for tag, data in self.hand_data.items():
            if 'x_ratio' in data:
                cx = data['x_ratio'] * self.scale_ratio + self.img_x_offset
                cy = data['y_ratio'] * self.scale_ratio + self.img_y_offset
                items = self.editor.preview_canvas.find_withtag(tag)
                for item_id in items:
                    self.editor.preview_canvas.coords(item_id, cx, cy)
                    
        # Reposition Step Badges
        for tag, data in self.badge_data.items():
            cx = data['x_ratio'] * self.scale_ratio + self.img_x_offset
            cy = data['y_ratio'] * self.scale_ratio + self.img_y_offset
            items = self.editor.preview_canvas.find_withtag(tag)
            for item_id in items:
                t = self.editor.preview_canvas.type(item_id)
                if t == "oval":
                    self.editor.preview_canvas.coords(item_id, cx - 13, cy - 13, cx + 13, cy + 13)
                elif t == "text":
                    self.editor.preview_canvas.coords(item_id, cx, cy)
                    
        # Reposition Text Annotations
        for tag, data in self.text_data.items():
            cx = data['x_ratio'] * self.scale_ratio + self.img_x_offset
            cy = data['y_ratio'] * self.scale_ratio + self.img_y_offset
            items = self.editor.preview_canvas.find_withtag(tag)
            text_item = None
            rect_item = None
            for item_id in items:
                t = self.editor.preview_canvas.type(item_id)
                if t == "text":
                    text_item = item_id
                elif t == "rectangle":
                    rect_item = item_id
            if text_item:
                self.editor.preview_canvas.coords(text_item, cx, cy)
                bbox = self.editor.preview_canvas.bbox(text_item)
                if bbox and rect_item:
                    x1, y1, x2, y2 = bbox
                    p = 6
                    self.editor.preview_canvas.coords(rect_item, x1 - p, y1 - p, x2 + p, y2 + p)
                    
        # Reposition Magnifier Zoom Callouts
        for tag, data in self.zoom_data.items():
            fx = data['fx_ratio'] * self.scale_ratio + self.img_x_offset
            fy = data['fy_ratio'] * self.scale_ratio + self.img_y_offset
            tx = data['tx_ratio'] * self.scale_ratio + self.img_x_offset
            ty = data['ty_ratio'] * self.scale_ratio + self.img_y_offset
            
            # Move bubble
            items = self.editor.preview_canvas.find_withtag(tag)
            for item_id in items:
                self.editor.preview_canvas.coords(item_id, tx, ty)
                
            # Move line and dot
            line_ids = self.editor.preview_canvas.find_withtag(f"line_{tag}")
            for item_id in line_ids:
                t = self.editor.preview_canvas.type(item_id)
                if t == "line":
                    self.editor.preview_canvas.coords(item_id, fx, fy, tx, ty)
                elif t == "oval":
                    self.editor.preview_canvas.coords(item_id, fx - 3, fy - 3, fx + 3, fy + 3)

        # Reposition Emoji stickers
        for tag, data in self.emoji_data.items():
            cx = data['x_ratio'] * self.scale_ratio + self.img_x_offset
            cy = data['y_ratio'] * self.scale_ratio + self.img_y_offset
            
            # Rescale emoji image to match new scale_ratio
            emoji_char = data['char']
            size = data['size']
            emoji_pil = self.render_emoji_to_image(emoji_char, size)
            sw = int(size * self.scale_ratio)
            if sw < 16: sw = 16
            scaled_emoji = emoji_pil.resize((sw, sw), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(scaled_emoji)
            data['photo'] = photo
            
            items = self.editor.preview_canvas.find_withtag(tag)
            for item_id in items:
                self.editor.preview_canvas.coords(item_id, cx, cy)
                if self.editor.preview_canvas.type(item_id) == "image":
                    self.editor.preview_canvas.itemconfig(item_id, image=photo)

    # Generic Items Dragging Handlers
    def on_item_press(self, event):
        self.editor.preview_canvas.focus_set()
        self.is_dragging_item = True
        clicked = self.editor.preview_canvas.find_withtag("current")
        if clicked:
            item_id = clicked[0]
            tags = self.editor.preview_canvas.gettags(item_id)
            self.dragged_item_tag = None
            for t in tags:
                if (t.startswith("hand_group_") or t.startswith("badge_group_") or 
                    t.startswith("text_group_") or t.startswith("zoom_group_") or 
                    t.startswith("emoji_group_")):
                    self.dragged_item_tag = t
                    break
            if self.dragged_item_tag:
                self.drag_start_x = event.x
                self.drag_start_y = event.y
                self.active_context_item_tag = self.dragged_item_tag
                self.show_active_item_border(self.dragged_item_tag)

    def on_item_drag(self, event):
        if getattr(self, 'dragged_item_tag', None) is not None:
            tag = self.dragged_item_tag
            dx = event.x - self.drag_start_x
            dy = event.y - self.drag_start_y
            self.editor.preview_canvas.move(tag, dx, dy)
            self.drag_start_x = event.x
            self.drag_start_y = event.y
            
            if tag.startswith("zoom_group_"):
                self.update_zoom_connector_line(tag)
                
            self.update_active_item_border_position(tag)

    def on_item_release(self, event):
        if getattr(self, 'dragged_item_tag', None) is not None:
            tag = self.dragged_item_tag
            coords = self.editor.preview_canvas.coords(tag)
            if coords:
                if len(coords) == 4:
                    cx = (coords[0] + coords[2]) / 2
                    cy = (coords[1] + coords[3]) / 2
                else:
                    cx = coords[0]
                    cy = coords[1]
                
                fx = (cx - self.img_x_offset) / self.scale_ratio
                fy = (cy - self.img_y_offset) / self.scale_ratio
                
                if tag in self.hand_data:
                    self.hand_data[tag]['x_ratio'] = fx
                    self.hand_data[tag]['y_ratio'] = fy
                elif tag in self.badge_data:
                    self.badge_data[tag]['x_ratio'] = fx
                    self.badge_data[tag]['y_ratio'] = fy
                elif tag in self.text_data:
                    self.text_data[tag]['x_ratio'] = fx
                    self.text_data[tag]['y_ratio'] = fy
                elif tag in self.zoom_data:
                    self.zoom_data[tag]['tx_ratio'] = fx
                    self.zoom_data[tag]['ty_ratio'] = fy
                elif tag in self.emoji_data:
                    self.emoji_data[tag]['x_ratio'] = fx
                    self.emoji_data[tag]['y_ratio'] = fy
                    
            self.dragged_item_tag = None
            self.after(50, lambda: setattr(self, 'is_dragging_item', False))

    def delete_active_item(self):
        tag = getattr(self, 'active_context_item_tag', None)
        if tag:
            self.editor.preview_canvas.delete(tag)
            self.editor.preview_canvas.delete(f"line_{tag}")
            if tag in self.hand_data:
                del self.hand_data[tag]
            elif tag in self.badge_data:
                del self.badge_data[tag]
            elif tag in self.text_data:
                del self.text_data[tag]
            elif tag in self.zoom_data:
                del self.zoom_data[tag]
            elif tag in self.emoji_data:
                del self.emoji_data[tag]
            self.active_context_item_tag = None
            self.editor.preview_canvas.delete("active_item_border")

    def on_key_delete(self, event):
        self.delete_active_item()

    def show_active_item_border(self, tag):
        self.editor.preview_canvas.delete("active_item_border")
        bbox = self.editor.preview_canvas.bbox(tag)
        if bbox:
            x1, y1, x2, y2 = bbox
            self.editor.preview_canvas.create_rectangle(
                x1 - 4, y1 - 4, x2 + 4, y2 + 4,
                outline="#00ffcc", width=1.5, dash=(4, 4), tags="active_item_border"
            )

    def update_active_item_border_position(self, tag):
        bbox = self.editor.preview_canvas.bbox(tag)
        if bbox:
            x1, y1, x2, y2 = bbox
            borders = self.editor.preview_canvas.find_withtag("active_item_border")
            if borders:
                self.editor.preview_canvas.coords(borders[0], x1 - 4, y1 - 4, x2 + 4, y2 + 4)

    def update_zoom_connector_line(self, tag):
        if tag in self.zoom_data:
            fx = self.zoom_data[tag]['fx_ratio'] * self.scale_ratio + self.img_x_offset
            fy = self.zoom_data[tag]['fy_ratio'] * self.scale_ratio + self.img_y_offset
            coords = self.editor.preview_canvas.coords(tag)
            if coords:
                cx, cy = coords[0], coords[1]
                line_id = self.editor.preview_canvas.find_withtag(f"line_{tag}")
                if line_id:
                    self.editor.preview_canvas.coords(line_id[0], fx, fy, cx, cy)

    def on_canvas_scroll(self, event):
        clicked = self.editor.preview_canvas.find_withtag("current")
        if clicked:
            tags = self.editor.preview_canvas.gettags(clicked[0])
            for t in tags:
                if t.startswith("hand_group_") and t in self.hand_data:
                    delta = 45 if event.delta > 0 else -45
                    self.rotate_hand_by_item(t, delta)
                    break
                elif t.startswith("zoom_group_") and t in self.zoom_data:
                    delta = 0.2 if event.delta > 0 else -0.2
                    self.adjust_magnifier_zoom(t, delta)
                    break
                elif t.startswith("emoji_group_") and t in self.emoji_data:
                    delta = 4 if event.delta > 0 else -4
                    self.adjust_emoji_size(t, delta)
                    break

    def rotate_hand_by_item(self, tag, angle_delta):
        if tag in self.hand_data:
            current_angle = self.hand_data[tag]['angle']
            new_angle = (current_angle - angle_delta) % 360
            self.hand_data[tag]['angle'] = new_angle
            self.update_hand_rendering(tag)
            
    def update_hand_rendering(self, tag):
        if tag in self.hand_data and self.current_screenshot:
            angle = self.hand_data[tag]['angle']
            color = self.current_color.get()
            
            hand_path = get_asset_path("hand_pointer.png")
            hand_pil = None
            if os.path.exists(hand_path):
                try:
                    hand_pil = Image.open(hand_path)
                except Exception as e:
                    print(f"Error loading hand PNG: {e}")
                    
            if hand_pil is None:
                # Fallback: Draw vector hand pointer
                hand_pil = Image.new("RGBA", (48, 48), (0, 0, 0, 0))
                draw_hand = ImageDraw.Draw(hand_pil)
                draw_hand_gesture(draw_hand, (24, 24), color)
                
            try:
                hw, hh = hand_pil.size
                sw = int(hw * self.scale_ratio)
                sh = int(hh * self.scale_ratio)
                if sw < 8: sw = 8
                if sh < 8: sh = 8
                scaled_hand = hand_pil.resize((sw, sh), Image.Resampling.LANCZOS)
                
                square_size = sw * 2
                square = Image.new("RGBA", (square_size, square_size), (0, 0, 0, 0))
                px = sw
                py = sw - (sh // 2)
                
                mask = scaled_hand.split()[3] if len(scaled_hand.split()) == 4 else None
                square.paste(scaled_hand, (px, py), mask=mask)
                
                rotated = square.rotate(angle, resample=Image.Resampling.BICUBIC, center=(sw, sw))
                photo = ImageTk.PhotoImage(rotated)
                
                self.hand_data[tag]['photo'] = photo
                
                items = self.editor.preview_canvas.find_withtag(tag)
                for item_id in items:
                    if self.editor.preview_canvas.type(item_id) == "image":
                        self.editor.preview_canvas.itemconfig(item_id, image=photo)
                        break
            except Exception as e:
                print(f"Error rotating hand: {e}")

    def adjust_magnifier_zoom(self, tag, delta_scale):
        if tag in self.zoom_data and self.current_screenshot:
            current_scale = self.zoom_data[tag].get('scale', 2.2)
            new_scale = max(1.2, min(5.0, current_scale + delta_scale))
            self.zoom_data[tag]['scale'] = new_scale
            self.update_magnifier_rendering(tag)

    def update_magnifier_rendering(self, tag):
        if tag in self.zoom_data and self.current_screenshot:
            fx = self.zoom_data[tag]['fx_ratio']
            fy = self.zoom_data[tag]['fy_ratio']
            scale = self.zoom_data[tag].get('scale', 2.2)
            
            # Re-create circular zoom image at new scale
            zoom_pil = self.create_circular_zoom_image(self.current_screenshot, (fx, fy), 40, scale=scale)
            display_zoom = zoom_pil.resize((120, 120), Image.Resampling.LANCZOS)
            zoom_photo = ImageTk.PhotoImage(display_zoom)
            
            self.zoom_data[tag]['photo'] = zoom_photo
            
            items = self.editor.preview_canvas.find_withtag(tag)
            for item_id in items:
                if self.editor.preview_canvas.type(item_id) == "image":
                    self.editor.preview_canvas.itemconfig(item_id, image=zoom_photo)
                    break
            self.update_active_item_border_position(tag)

    def render_emoji_to_image(self, stamp_name, size=64):
        size = max(16, size)
        img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        if stamp_name == "checkmark":
            w = max(2, size // 8)
            draw.line([size * 0.25, size * 0.55, size * 0.45, size * 0.75], fill="#22c55e", width=w, joint="round")
            draw.line([size * 0.45, size * 0.75, size * 0.75, size * 0.3], fill="#22c55e", width=w, joint="round")
            
        elif stamp_name == "cross":
            w = max(2, size // 8)
            draw.line([size * 0.25, size * 0.25, size * 0.75, size * 0.75], fill="#ef4444", width=w, joint="round")
            draw.line([size * 0.75, size * 0.25, size * 0.25, size * 0.75], fill="#ef4444", width=w, joint="round")
            
        elif stamp_name == "warning":
            p1 = (size * 0.5, size * 0.15)
            p2 = (size * 0.15, size * 0.8)
            p3 = (size * 0.85, size * 0.8)
            draw.polygon([p1, p2, p3], fill="#eab308", outline="black", width=max(1, size // 24))
            w = max(2, size // 16)
            draw.line([size * 0.5, size * 0.4, size * 0.5, size * 0.62], fill="black", width=w)
            draw.ellipse([size * 0.5 - w/2, size * 0.7 - w/2, size * 0.5 + w/2, size * 0.7 + w/2], fill="black")
            
        elif stamp_name == "target":
            r1 = size * 0.45
            draw.ellipse([size * 0.5 - r1, size * 0.5 - r1, size * 0.5 + r1, size * 0.5 + r1], fill="#ef4444")
            r2 = size * 0.3
            draw.ellipse([size * 0.5 - r2, size * 0.5 - r2, size * 0.5 + r2, size * 0.5 + r2], fill="white")
            r3 = size * 0.15
            draw.ellipse([size * 0.5 - r3, size * 0.5 - r3, size * 0.5 + r3, size * 0.5 + r3], fill="#ef4444")
            
        elif stamp_name == "star":
            points = []
            cx, cy = size * 0.5, size * 0.5
            r_outer = size * 0.45
            r_inner = size * 0.2
            import math
            for i in range(10):
                r = r_outer if i % 2 == 0 else r_inner
                angle = i * math.pi / 5 - math.pi / 2
                points.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))
            draw.polygon(points, fill="#fbbf24", outline="white", width=max(1, size // 32))
            
        elif stamp_name == "idea":
            draw.ellipse([size * 0.1, size * 0.1, size * 0.9, size * 0.9], fill="#eab308", outline="white", width=max(1, size // 24))
            w = max(2, size // 16)
            draw.arc([size * 0.35, size * 0.3, size * 0.65, size * 0.6], 180, 360, fill="white", width=w)
            draw.line([size * 0.35, size * 0.6, size * 0.65, size * 0.6], fill="white", width=w)
            draw.line([size * 0.45, size * 0.6, size * 0.45, size * 0.75], fill="white", width=w)
            draw.line([size * 0.55, size * 0.6, size * 0.55, size * 0.75], fill="white", width=w)
            
        elif stamp_name == "question":
            draw.ellipse([size * 0.1, size * 0.1, size * 0.9, size * 0.9], fill="#06b6d4", outline="white", width=max(1, size // 24))
            try:
                font = ImageFont.truetype("arial.ttf", int(size * 0.5))
            except:
                font = ImageFont.load_default()
            draw.text((size * 0.5, size * 0.48), "?", fill="white", font=font, anchor="mm")
            
        elif stamp_name == "thumbsup":
            draw.ellipse([size * 0.1, size * 0.1, size * 0.9, size * 0.9], fill="#22c55e", outline="white", width=max(1, size // 24))
            try:
                font = ImageFont.truetype("seguiemj.ttf", int(size * 0.5))
            except:
                font = ImageFont.load_default()
            draw.text((size * 0.5, size * 0.48), "👍", fill="white", font=font, anchor="mm")
            
        elif stamp_name == "fire":
            draw.ellipse([size * 0.1, size * 0.1, size * 0.9, size * 0.9], fill="#f97316", outline="white", width=max(1, size // 24))
            try:
                font = ImageFont.truetype("seguiemj.ttf", int(size * 0.5))
            except:
                font = ImageFont.load_default()
            draw.text((size * 0.5, size * 0.48), "🔥", fill="white", font=font, anchor="mm")
            
        elif stamp_name == "heart":
            draw.ellipse([size * 0.1, size * 0.1, size * 0.9, size * 0.9], fill="#ec4899", outline="white", width=max(1, size // 24))
            try:
                font = ImageFont.truetype("seguiemj.ttf", int(size * 0.5))
            except:
                font = ImageFont.load_default()
            draw.text((size * 0.5, size * 0.48), "❤️", fill="white", font=font, anchor="mm")

        elif stamp_name == "info":
            draw.ellipse([size * 0.1, size * 0.1, size * 0.9, size * 0.9], fill="#3b82f6", outline="white", width=max(1, size // 24))
            try:
                font = ImageFont.truetype("arial.ttf", int(size * 0.5))
            except:
                font = ImageFont.load_default()
            draw.text((size * 0.5, size * 0.48), "i", fill="white", font=font, anchor="mm")
            
        elif stamp_name == "smile":
            draw.ellipse([size * 0.1, size * 0.1, size * 0.9, size * 0.9], fill="#facc15", outline="black", width=max(1, size // 24))
            w = max(2, size // 16)
            draw.ellipse([size * 0.32, size * 0.35, size * 0.42, size * 0.45], fill="black")
            draw.ellipse([size * 0.58, size * 0.35, size * 0.68, size * 0.45], fill="black")
            draw.arc([size * 0.3, size * 0.45, size * 0.7, size * 0.75], 0, 180, fill="black", width=w)
            
        elif stamp_name == "sad":
            draw.ellipse([size * 0.1, size * 0.1, size * 0.9, size * 0.9], fill="#60a5fa", outline="white", width=max(1, size // 24))
            w = max(2, size // 16)
            draw.ellipse([size * 0.32, size * 0.35, size * 0.42, size * 0.45], fill="black")
            draw.ellipse([size * 0.58, size * 0.35, size * 0.68, size * 0.45], fill="black")
            draw.arc([size * 0.3, size * 0.55, size * 0.7, size * 0.85], 180, 360, fill="black", width=w)
            
        elif stamp_name == "arrow_up":
            draw.ellipse([size * 0.1, size * 0.1, size * 0.9, size * 0.9], fill="#10b981", outline="white", width=max(1, size // 24))
            w = max(2, size // 8)
            draw.line([size * 0.5, size * 0.75, size * 0.5, size * 0.25], fill="white", width=w)
            draw.line([size * 0.28, size * 0.47, size * 0.5, size * 0.25], fill="white", width=w, joint="round")
            draw.line([size * 0.72, size * 0.47, size * 0.5, size * 0.25], fill="white", width=w, joint="round")
            
        elif stamp_name == "arrow_down":
            draw.ellipse([size * 0.1, size * 0.1, size * 0.9, size * 0.9], fill="#ef4444", outline="white", width=max(1, size // 24))
            w = max(2, size // 8)
            draw.line([size * 0.5, size * 0.25, size * 0.5, size * 0.75], fill="white", width=w)
            draw.line([size * 0.28, size * 0.53, size * 0.5, size * 0.75], fill="white", width=w, joint="round")
            draw.line([size * 0.72, size * 0.53, size * 0.5, size * 0.75], fill="white", width=w, joint="round")
            
        elif stamp_name == "shield":
            p1 = (size * 0.5, size * 0.1)
            p2 = (size * 0.85, size * 0.25)
            p3 = (size * 0.8, size * 0.65)
            p4 = (size * 0.5, size * 0.9)
            p5 = (size * 0.2, size * 0.65)
            p6 = (size * 0.15, size * 0.25)
            draw.polygon([p1, p2, p3, p4, p5, p6], fill="#3b82f6", outline="white", width=max(1, size // 24))
            draw.polygon([p1, (size * 0.5, size * 0.9), p5, p6], fill="#1d4ed8")
            
        elif stamp_name == "bug":
            w = max(1, size // 24)
            for offset in [size*0.4, size*0.55, size*0.7]:
                draw.line([size*0.15, offset, size*0.85, offset], fill="black", width=w)
            draw.line([size*0.38, size*0.2, size*0.25, size*0.08], fill="black", width=w)
            draw.line([size*0.62, size*0.2, size*0.75, size*0.08], fill="black", width=w)
            draw.ellipse([size * 0.3, size * 0.28, size * 0.7, size * 0.85], fill="#10b981", outline="black", width=max(1, size // 32))
            draw.ellipse([size * 0.35, size * 0.15, size * 0.65, size * 0.38], fill="#064e3b")
            
        elif stamp_name == "lock":
            w = max(2, size // 10)
            draw.arc([size*0.28, size*0.15, size*0.72, size*0.55], 180, 360, fill="#94a3b8", width=w)
            draw.rounded_rectangle([size*0.2, size*0.42, size*0.8, size*0.88], radius=size//12, fill="#fbbf24", outline="black", width=max(1, size // 32))
            draw.ellipse([size*0.45, size*0.58, size*0.55, size*0.68], fill="black")
            draw.line([size*0.5, size*0.65, size*0.5, size*0.78], fill="black", width=max(2, size//16))
            
        elif stamp_name == "flag":
            w = max(2, size // 16)
            draw.line([size*0.25, size*0.1, size*0.25, size*0.9], fill="black", width=w)
            draw.polygon([(size*0.25, size*0.15), (size*0.8, size*0.35), (size*0.25, size*0.55)], fill="#ef4444", outline="black", width=max(1, size // 32))
            
        elif stamp_name == "check_double":
            w = max(2, size // 10)
            draw.line([size * 0.15, size * 0.55, size * 0.35, size * 0.75], fill="#10b981", width=w, joint="round")
            draw.line([size * 0.35, size * 0.75, size * 0.65, size * 0.3], fill="#10b981", width=w, joint="round")
            draw.line([size * 0.3, size * 0.55, size * 0.5, size * 0.75], fill="#22c55e", width=w, joint="round")
            draw.line([size * 0.5, size * 0.75, size * 0.8, size * 0.3], fill="#22c55e", width=w, joint="round")
            
        return img

    def adjust_emoji_size(self, tag, delta_size):
        if tag in self.emoji_data:
            curr_size = self.emoji_data[tag].get('size', 64)
            new_size = max(16, min(256, curr_size + delta_size))
            self.emoji_data[tag]['size'] = new_size
            self.update_emoji_rendering(tag)

    def update_emoji_rendering(self, tag):
        if tag in self.emoji_data:
            emoji_char = self.emoji_data[tag]['char']
            size = self.emoji_data[tag]['size']
            
            emoji_pil = self.render_emoji_to_image(emoji_char, size)
            sw = int(size * self.scale_ratio)
            if sw < 16: sw = 16
            scaled_emoji = emoji_pil.resize((sw, sw), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(scaled_emoji)
            
            self.emoji_data[tag]['photo'] = photo
            
            items = self.editor.preview_canvas.find_withtag(tag)
            for item_id in items:
                if self.editor.preview_canvas.type(item_id) == "image":
                    self.editor.preview_canvas.itemconfig(item_id, image=photo)
                    break
            self.update_active_item_border_position(tag)

    def show_emoji_selector_popup(self, x, y):
        popup = tk.Toplevel(self.editor)
        popup.overrideredirect(True)
        popup.attributes("-topmost", True)
        popup.configure(bg="#212121")
        popup.config(highlightbackground="#1f538d", highlightthickness=1.5)
        
        # Grid of 20 colorful stamps
        stamps = [
            ["checkmark", "cross", "warning", "target", "star"],
            ["idea", "question", "thumbsup", "fire", "heart"],
            ["info", "smile", "sad", "arrow_up", "arrow_down"],
            ["shield", "bug", "lock", "flag", "check_double"]
        ]
        
        # Position popup near mouse click
        root_x = self.editor.preview_canvas.winfo_rootx() + x
        root_y = self.editor.preview_canvas.winfo_rooty() + y
        popup.geometry(f"+{root_x - 100}+{root_y - 90}")
        
        # Build grid labels
        self.popup_photos = [] # Reference to prevent GC
        for r_idx, row in enumerate(stamps):
            row_frame = tk.Frame(popup, bg="#212121")
            row_frame.pack(fill="x", padx=4, pady=2)
            for stamp_name in row:
                stamp_pil = self.render_emoji_to_image(stamp_name, 28)
                photo = ImageTk.PhotoImage(stamp_pil)
                self.popup_photos.append(photo)
                
                lbl = tk.Label(
                    row_frame, image=photo, bg="#2a2a2a", cursor="hand2",
                    relief="flat", width=34, height=34
                )
                lbl.pack(side="left", padx=2)
                
                lbl.bind("<Enter>", lambda e, l=lbl: l.configure(bg="#3a3a3a"))
                lbl.bind("<Leave>", lambda e, l=lbl: l.configure(bg="#2a2a2a"))
                lbl.bind("<Button-1>", lambda e, val=stamp_name: self.place_emoji_sticker(x, y, val, popup))
                
        popup.bind("<Leave>", lambda e: self.on_popup_leave(e, popup))

    def on_popup_leave(self, event, popup):
        rx = popup.winfo_pointerx()
        ry = popup.winfo_pointery()
        px = popup.winfo_rootx()
        py = popup.winfo_rooty()
        pw = popup.winfo_width()
        ph = popup.winfo_height()
        if not (px - 2 <= rx <= px + pw + 2 and py - 2 <= ry <= py + ph + 2):
            popup.destroy()

    def place_emoji_sticker(self, x, y, emoji_char, popup):
        popup.destroy()
        tag_id = int(time.time() * 1000)
        tag_name = f"emoji_group_{tag_id}"
        
        emoji_pil = self.render_emoji_to_image(emoji_char, 64)
        sw = int(64 * self.scale_ratio)
        if sw < 16: sw = 16
        scaled_emoji = emoji_pil.resize((sw, sw), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(scaled_emoji)
        
        item_id = self.editor.preview_canvas.create_image(
            x, y, image=photo, anchor="center", tags=("movable_item", tag_name)
        )
        
        fx = (x - self.img_x_offset) / self.scale_ratio
        fy = (y - self.img_y_offset) / self.scale_ratio
        
        self.emoji_data[tag_name] = {
            'char': emoji_char,
            'size': 64,
            'photo': photo,
            'x_ratio': fx,
            'y_ratio': fy
        }
        
        self.editor.preview_canvas.tag_bind(tag_name, "<Enter>", lambda e: self.editor.preview_canvas.config(cursor="fleur"))
        self.editor.preview_canvas.tag_bind(tag_name, "<Leave>", lambda e: self.editor.preview_canvas.config(cursor="arrow"))
        
        self.active_context_item_tag = tag_name
        self.show_active_item_border(tag_name)

    def on_item_right_click(self, event):
        clicked = self.editor.preview_canvas.find_withtag("current")
        if clicked:
            item_id = clicked[0]
            tags = self.editor.preview_canvas.gettags(item_id)
            for t in tags:
                if (t.startswith("hand_group_") or t.startswith("badge_group_") or 
                    t.startswith("text_group_") or t.startswith("zoom_group_") or 
                    t.startswith("emoji_group_")):
                    self.active_context_item_tag = t
                    self.show_active_item_border(t)
                    self.show_item_context_menu(event, t)
                    break
            
    def show_item_context_menu(self, event, tag):
        menu = tk.Menu(self.editor, tearoff=0, bg="#212121", fg="white", activebackground="#1f538d", activeforeground="white")
        if tag.startswith("hand_group_"):
            menu.add_command(label="Rotate 45° 🔄", command=lambda: self.rotate_hand_by_item(tag, 45))
            menu.add_command(label="Rotate 90° 🔄", command=lambda: self.rotate_hand_by_item(tag, 90))
            menu.add_separator()
        menu.add_command(label="Delete 🗑️", command=self.delete_active_item)
        
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def create_circular_zoom_image(self, pil_img, center, radius, scale=2.2):
        cx, cy = center
        w, h = pil_img.size
        x1 = max(0, int(cx - radius))
        y1 = max(0, int(cy - radius))
        x2 = min(w, int(cx + radius))
        y2 = min(h, int(cy + radius))
        
        cropped = pil_img.crop((x1, y1, x2, y2))
        new_dim = int(radius * 2 * scale)
        upscaled = cropped.resize((new_dim, new_dim), Image.Resampling.LANCZOS)
        
        mask = Image.new("L", (new_dim, new_dim), 0)
        draw_mask = ImageDraw.Draw(mask)
        draw_mask.ellipse([0, 0, new_dim - 1, new_dim - 1], fill=255)
        
        circular = Image.new("RGBA", (new_dim, new_dim), (0, 0, 0, 0))
        circular.paste(upscaled.convert("RGBA"), (0, 0), mask=mask)
        
        draw_border = ImageDraw.Draw(circular)
        draw_border.ellipse([0, 0, new_dim - 1, new_dim - 1], outline="white", width=4)
        
        return circular

    def get_baked_screenshot(self):
        if not self.current_screenshot:
            return None
            
        baked_img = self.current_screenshot.copy()
        draw = ImageDraw.Draw(baked_img)
        
        # 1. Bake Hand pointers
        if self.hand_data:
            hand_path = get_asset_path("hand_pointer.png")
            hand_asset = None
            if os.path.exists(hand_path):
                try:
                    hand_asset = Image.open(hand_path)
                except Exception as e:
                    print(f"Error loading hand PNG: {e}")
                    
            for tag, data in self.hand_data.items():
                items = self.editor.preview_canvas.find_withtag(tag)
                if items:
                    coords = self.editor.preview_canvas.coords(items[0])
                    if coords:
                        cx, cy = coords[0], coords[1]
                        angle = data['angle']
                        fx = (cx - self.img_x_offset) / self.scale_ratio
                        fy = (cy - self.img_y_offset) / self.scale_ratio
                        
                        curr_hand = hand_asset
                        if curr_hand is None:
                            # Fallback: Draw vector hand
                            curr_hand = Image.new("RGBA", (48, 48), (0, 0, 0, 0))
                            draw_hand = ImageDraw.Draw(curr_hand)
                            draw_hand_gesture(draw_hand, (24, 24), self.current_color.get())
                            
                        hw, hh = curr_hand.size
                        square_size = hw * 2
                        square = Image.new("RGBA", (square_size, square_size), (0, 0, 0, 0))
                        
                        mask = curr_hand.split()[3] if len(curr_hand.split()) == 4 else None
                        square.paste(curr_hand, (hw, hw - (hh // 2)), mask=mask)
                        
                        rotated = square.rotate(angle, resample=Image.Resampling.BICUBIC, center=(hw, hw))
                        baked_img.paste(rotated, (int(fx - hw), int(fy - hw)), rotated)
                        
        # 2. Bake Step Badges
        if self.badge_data:
            for tag, data in self.badge_data.items():
                fx = data['x_ratio']
                fy = data['y_ratio']
                num_str = str(data['number'])
                color = data['color']
                text_color = "white" if color != "yellow" else "black"
                
                r = 16
                draw.ellipse([fx - r, fy - r, fx + r, fy + r], fill=color, outline="white", width=2)
                
                try:
                    font = ImageFont.truetype("arial.ttf", 18)
                except:
                    font = ImageFont.load_default()
                draw.text((fx, fy), num_str, fill=text_color, font=font, anchor="mm")
                
        # 3. Bake Text Annotations
        if self.text_data:
            for tag, data in self.text_data.items():
                fx = data['x_ratio']
                fy = data['y_ratio']
                text = data['text']
                color = data['color']
                
                try:
                    font = ImageFont.truetype("arial.ttf", 22)
                except:
                    font = ImageFont.load_default()
                    
                l, t, r, b = draw.textbbox((fx, fy), text, font=font, anchor="mm")
                p = 8
                draw.rounded_rectangle([l - p, t - p, r + p, b + p], radius=5, fill="#212121", outline=color, width=2)
                draw.text((fx, fy), text, fill=color, font=font, anchor="mm")

        # 4. Bake Magnifier Glasses
        if self.zoom_data:
            for tag, data in self.zoom_data.items():
                fx = data['fx_ratio']
                fy = data['fy_ratio']
                tx = data['tx_ratio']
                ty = data['ty_ratio']
                scale = data.get('scale', 2.2)
                
                draw.line([fx, fy, tx, ty], fill="white", width=3)
                draw.ellipse([fx - 4, fy - 4, fx + 4, fy + 4], fill="#00ffcc")
                
                zoom_pil = self.create_circular_zoom_image(baked_img, (fx, fy), 40, scale=scale)
                zoom_r = zoom_pil.size[0] // 2
                baked_img.paste(zoom_pil, (int(tx - zoom_r), int(ty - zoom_r)), zoom_pil)

        # 5. Bake Emojis
        if self.emoji_data:
            for tag, data in self.emoji_data.items():
                fx = data['x_ratio']
                fy = data['y_ratio']
                char = data['char']
                size = data['size']
                
                # Render color emoji to PIL image and paste with alpha mask
                emoji_pil = self.render_emoji_to_image(char, size)
                baked_img.paste(emoji_pil, (int(fx - size // 2), int(fy - size // 2)), emoji_pil)
                
        # 6. Bake Watermark if enabled
        if hasattr(self, 'editor') and self.editor.winfo_exists() and self.editor.watermark_enabled.get():
            text = self.editor.txt_watermark.get()
            if text:
                from PIL import ImageDraw, ImageFont
                draw_wm = ImageDraw.Draw(baked_img)
                try:
                    font = ImageFont.truetype("arial.ttf", 16)
                except Exception:
                    font = ImageFont.load_default()
                w, h = baked_img.size
                try:
                    bbox = draw_wm.textbbox((0, 0), text, font=font)
                    tw = bbox[2] - bbox[0]
                    th = bbox[3] - bbox[1]
                except AttributeError:
                    tw, th = draw_wm.textsize(text, font=font) if hasattr(draw_wm, 'textsize') else (150, 15)
                tx = w - tw - 20
                ty = h - th - 20
                # Draw black background outline
                draw_wm.rectangle([tx - 6, ty - 6, w - 10, h - 10], fill=(0, 0, 0, 160))
                draw_wm.text((tx, ty), text, fill=(255, 255, 255, 255), font=font)
                
        return baked_img

    # Drawing board handlers
    def on_draw_start(self, event):
        self.active_context_item_tag = None
        self.editor.preview_canvas.delete("active_item_border")
        
        if not self.current_screenshot or self.current_tool.get() == "None":
            return
            
        w, h = self.current_screenshot.size
        scaled_w = int(w * self.scale_ratio)
        scaled_h = int(h * self.scale_ratio)
        
        if not (self.img_x_offset <= event.x <= self.img_x_offset + scaled_w and
                self.img_y_offset <= event.y <= self.img_y_offset + scaled_h):
            return
            
        tool = self.current_tool.get()
        color = self.current_color.get()
        
        # A. Click-to-place Hand Pointer Tool
        if tool == "Hand":
            if getattr(self, 'is_dragging_item', False):
                return
            
            hand_path = get_asset_path("hand_pointer.png")
            hand_pil = None
            if os.path.exists(hand_path):
                try:
                    hand_pil = Image.open(hand_path)
                except Exception as e:
                    print(f"Error loading hand PNG: {e}")
                    
            if hand_pil is None:
                # Fallback: Draw vector hand pointer on transparent canvas
                hand_pil = Image.new("RGBA", (48, 48), (0, 0, 0, 0))
                draw_hand = ImageDraw.Draw(hand_pil)
                draw_hand_gesture(draw_hand, (24, 24), color) # Draw hand in center
                
            try:
                hw, hh = hand_pil.size
                sw = int(hw * self.scale_ratio)
                sh = int(hh * self.scale_ratio)
                if sw < 8: sw = 8
                if sh < 8: sh = 8
                scaled_hand = hand_pil.resize((sw, sh), Image.Resampling.LANCZOS)
                
                square_size = sw * 2
                square = Image.new("RGBA", (square_size, square_size), (0, 0, 0, 0))
                
                # Check for alpha channel mask
                mask = scaled_hand.split()[3] if len(scaled_hand.split()) == 4 else None
                square.paste(scaled_hand, (sw, sw - (sh // 2)), mask=mask)
                photo = ImageTk.PhotoImage(square)
                
                tag_id = int(time.time() * 1000)
                tag_name = f"hand_group_{tag_id}"
                
                item_id = self.editor.preview_canvas.create_image(
                    event.x, event.y, image=photo, anchor="center", tags=("movable_item", tag_name)
                )
                
                fx = (event.x - self.img_x_offset) / self.scale_ratio
                fy = (event.y - self.img_y_offset) / self.scale_ratio
                
                self.hand_data[tag_name] = { 'angle': 0, 'photo': photo, 'x_ratio': fx, 'y_ratio': fy }
                
                self.editor.preview_canvas.tag_bind(tag_name, "<Enter>", lambda e: self.editor.preview_canvas.config(cursor="fleur"))
                self.editor.preview_canvas.tag_bind(tag_name, "<Leave>", lambda e: self.editor.preview_canvas.config(cursor="arrow"))
                
                self.active_context_item_tag = tag_name
                self.show_active_item_border(tag_name)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to place hand pointer:\n{e}", parent=self.editor)
            return

        # Emoji Sticker Tool click listener
        elif tool == "Emoji":
            if getattr(self, 'is_dragging_item', False):
                return
            self.show_emoji_selector_popup(event.x, event.y)
            return
            
        # B. Click-to-place Step Badge Tool
        elif tool == "Badge":
            tag_id = int(time.time() * 1000)
            tag_name = f"badge_group_{tag_id}"
            
            badge_num = self.current_step_number
            self.current_step_number += 1
            text_color = "white" if color != "yellow" else "black"
            
            c_item = self.editor.preview_canvas.create_oval(
                event.x - 13, event.y - 13, event.x + 13, event.y + 13,
                fill=color, outline="white", width=1.5, tags=("movable_item", tag_name)
            )
            t_item = self.editor.preview_canvas.create_text(
                event.x, event.y, text=str(badge_num),
                fill=text_color, font=("Arial", 11, "bold"), tags=("movable_item", tag_name)
            )
            
            fx = (event.x - self.img_x_offset) / self.scale_ratio
            fy = (event.y - self.img_y_offset) / self.scale_ratio
            self.badge_data[tag_name] = {
                'number': badge_num,
                'color': color,
                'x_ratio': fx,
                'y_ratio': fy
            }
            
            self.active_context_item_tag = tag_name
            self.show_active_item_border(tag_name)
            return

        # C. Click-to-place Text Annotations Tool
        elif tool == "Text":
            text_str = simpledialog.askstring("Add Text", "Enter annotation text:", parent=self.editor)
            if text_str:
                tag_id = int(time.time() * 1000)
                tag_name = f"text_group_{tag_id}"
                
                txt_item = self.editor.preview_canvas.create_text(
                    event.x, event.y, text=text_str, fill=color,
                    font=("Arial", 12, "bold"), tags=("movable_item", tag_name)
                )
                bbox = self.editor.preview_canvas.bbox(txt_item)
                if bbox:
                    x1, y1, x2, y2 = bbox
                    p = 6
                    rect_item = self.editor.preview_canvas.create_rectangle(
                        x1 - p, y1 - p, x2 + p, y2 + p,
                        fill="#212121", outline=color, width=1.5,
                        tags=("movable_item", tag_name)
                    )
                    self.editor.preview_canvas.tag_lower(rect_item, txt_item)
                    
                fx = (event.x - self.img_x_offset) / self.scale_ratio
                fy = (event.y - self.img_y_offset) / self.scale_ratio
                self.text_data[tag_name] = {
                    'text': text_str,
                    'color': color,
                    'x_ratio': fx,
                    'y_ratio': fy
                }
                
                self.active_context_item_tag = tag_name
                self.show_active_item_border(tag_name)
            return

        self.save_to_history()
        self.draw_start_x = event.x
        self.draw_start_y = event.y
        self.last_draw_x = event.x
        self.last_draw_y = event.y
        
    def on_draw_drag(self, event):
        if not self.current_screenshot or self.current_tool.get() in ("None", "Hand", "Badge", "Text"):
            return
            
        tool = self.current_tool.get()
        color = self.current_color.get()
        
        w, h = self.current_screenshot.size
        scaled_w = int(w * self.scale_ratio)
        scaled_h = int(h * self.scale_ratio)
        
        ex = max(self.img_x_offset, min(event.x, self.img_x_offset + scaled_w))
        ey = max(self.img_y_offset, min(event.y, self.img_y_offset + scaled_h))
        
        if tool == "Pen" or tool == "Highlighter":
            x1 = int((self.last_draw_x - self.img_x_offset) / self.scale_ratio)
            y1 = int((self.last_draw_y - self.img_y_offset) / self.scale_ratio)
            x2 = int((ex - self.img_x_offset) / self.scale_ratio)
            y2 = int((ey - self.img_y_offset) / self.scale_ratio)
            
            if tool == "Pen":
                draw = ImageDraw.Draw(self.current_screenshot)
                draw.line([x1, y1, x2, y2], fill=color, width=4)
            else:  # Highlighter
                rgba_img = self.current_screenshot.convert("RGBA")
                overlay = Image.new("RGBA", rgba_img.size, (0, 0, 0, 0))
                draw_overlay = ImageDraw.Draw(overlay)
                color_map = {
                    "red": (255, 0, 0, 80),
                    "green": (0, 255, 0, 80),
                    "blue": (0, 0, 255, 80),
                    "yellow": (255, 255, 0, 80),
                    "black": (0, 0, 0, 80),
                    "white": (255, 255, 255, 80)
                }
                rgba_color = color_map.get(color, (255, 255, 0, 80))
                draw_overlay.line([x1, y1, x2, y2], fill=rgba_color, width=18)
                self.current_screenshot = Image.alpha_composite(rgba_img, overlay).convert("RGB")
                
            self.last_draw_x = ex
            self.last_draw_y = ey
            self.show_preview(self.current_screenshot, save_history=False)
            
        elif tool == "Rectangle" or tool == "Blur":
            if self.temp_shape_id:
                self.editor.preview_canvas.delete(self.temp_shape_id)
            self.temp_shape_id = self.editor.preview_canvas.create_rectangle(
                self.draw_start_x, self.draw_start_y, ex, ey,
                outline=color if tool == "Rectangle" else "white",
                width=3, dash=(4, 4) if tool == "Blur" else None
            )
            
        elif tool == "Arrow":
            if self.temp_shape_id:
                self.editor.preview_canvas.delete(self.temp_shape_id)
            self.temp_shape_id = self.editor.preview_canvas.create_line(
                self.draw_start_x, self.draw_start_y, ex, ey, fill=color, width=3, arrow="last"
            )
            
        elif tool == "Magnifier":
            if self.temp_shape_id:
                self.editor.preview_canvas.delete(self.temp_shape_id)
            self.temp_shape_id = self.editor.preview_canvas.create_oval(
                self.draw_start_x - 30, self.draw_start_y - 30,
                self.draw_start_x + 30, self.draw_start_y + 30,
                outline="white", width=2, dash=(3, 3)
            )

    def on_draw_end(self, event):
        if not self.current_screenshot or self.current_tool.get() in ("None", "Hand", "Badge", "Text"):
            return
            
        tool = self.current_tool.get()
        color = self.current_color.get()
        
        if self.temp_shape_id:
            self.editor.preview_canvas.delete(self.temp_shape_id)
            self.temp_shape_id = None
            
        w, h = self.current_screenshot.size
        scaled_w = int(w * self.scale_ratio)
        scaled_h = int(h * self.scale_ratio)
        
        ex = max(self.img_x_offset, min(event.x, self.img_x_offset + scaled_w))
        ey = max(self.img_y_offset, min(event.y, self.img_y_offset + scaled_h))
        
        x1 = int((self.draw_start_x - self.img_x_offset) / self.scale_ratio)
        y1 = int((self.draw_start_y - self.img_y_offset) / self.scale_ratio)
        x2 = int((ex - self.img_x_offset) / self.scale_ratio)
        y2 = int((ey - self.img_y_offset) / self.scale_ratio)
        
        if abs(x2 - x1) < 2 and abs(y2 - y1) < 2 and tool != "Magnifier":
            return
            
        draw = ImageDraw.Draw(self.current_screenshot)
        
        if tool == "Rectangle":
            draw.rectangle([x1, y1, x2, y2], outline=color, width=4)
            self.show_preview(self.current_screenshot, save_history=False)
            copy_image_to_clipboard(self.current_screenshot)
            
        elif tool == "Arrow":
            draw_arrow(draw, (x1, y1), (x2, y2), color, width=4)
            self.show_preview(self.current_screenshot, save_history=False)
            copy_image_to_clipboard(self.current_screenshot)
            
        elif tool == "Blur":
            bx1, bx2 = min(x1, x2), max(x1, x2)
            by1, by2 = min(y1, y2), max(y1, y2)
            if bx2 - bx1 > 4 and by2 - by1 > 4:
                cropped = self.current_screenshot.crop((bx1, by1, bx2, by2))
                # Apply strong radius=25 blur for great high-res and low-res legibility
                blurred = cropped.filter(ImageFilter.GaussianBlur(radius=25))
                self.current_screenshot.paste(blurred, (bx1, by1))
                self.show_preview(self.current_screenshot, save_history=False)
                copy_image_to_clipboard(self.current_screenshot)
                
        elif tool == "Magnifier":
            tx_ratio = (event.x - self.img_x_offset) / self.scale_ratio
            ty_ratio = (event.y - self.img_y_offset) / self.scale_ratio
            
            if abs(tx_ratio - x1) < 10 and abs(ty_ratio - y1) < 10:
                tx_ratio = x1 + 100
                ty_ratio = y1 - 100
                
            tag_id = int(time.time() * 1000)
            tag_name = f"zoom_group_{tag_id}"
            
            l_start_x = x1 * self.scale_ratio + self.img_x_offset
            l_start_y = y1 * self.scale_ratio + self.img_y_offset
            l_end_x = tx_ratio * self.scale_ratio + self.img_x_offset
            l_end_y = ty_ratio * self.scale_ratio + self.img_y_offset
            
            line_id = self.editor.preview_canvas.create_line(
                l_start_x, l_start_y, l_end_x, l_end_y,
                fill="white", width=2, tags=(f"line_{tag_name}")
            )
            dot_id = self.editor.preview_canvas.create_oval(
                l_start_x - 3, l_start_y - 3, l_start_x + 3, l_start_y + 3,
                fill="#00ffcc", outline="white", tags=(f"line_{tag_name}")
            )
            
            zoom_pil = self.create_circular_zoom_image(self.current_screenshot, (x1, y1), 40)
            
            display_zoom = zoom_pil.resize((120, 120), Image.Resampling.LANCZOS)
            zoom_photo = ImageTk.PhotoImage(display_zoom)
            
            bubble_id = self.editor.preview_canvas.create_image(
                l_end_x, l_end_y, image=zoom_photo, anchor="center", tags=("movable_item", tag_name)
            )
            
            self.zoom_data[tag_name] = {
                'photo': zoom_photo,
                'fx_ratio': x1,
                'fy_ratio': y1,
                'tx_ratio': tx_ratio,
                'ty_ratio': ty_ratio,
                'scale': 2.2
            }
            
            self.editor.preview_canvas.tag_bind(tag_name, "<Enter>", lambda e: self.editor.preview_canvas.config(cursor="fleur"))
            self.editor.preview_canvas.tag_bind(tag_name, "<Leave>", lambda e: self.editor.preview_canvas.config(cursor="arrow"))
            
            self.active_context_item_tag = tag_name
            self.show_active_item_border(tag_name)

    # Dock control
    def hide_dock(self):
        self.withdraw()
        self.editor.withdraw()
        if self.tray_icon:
            self.tray_icon.notify(
                "PrintPulse Screenshot tool is running in the background.\nPress Ctrl+Shift+S to capture area!",
                "Screenshot Tool Minimized"
            )
            
    def restore_dock(self):
        self.deiconify()
        self.focus_force()
        
    def quit_app(self):
        if self.tray_icon:
            self.tray_icon.stop()
        self.destroy()
        sys.exit(0)

    # Background Tray Icon
    def setup_tray_icon(self):
        def create_tray_image():
            image = Image.new("RGB", (64, 64), (33, 33, 33))
            draw = ImageDraw.Draw(image)
            draw.rectangle([16, 24, 48, 48], fill="#1f538d", outline="white", width=2)
            draw.ellipse([26, 28, 38, 40], fill="#00ffcc", outline="white", width=1)
            draw.rectangle([24, 18, 40, 24], fill="#1f538d", outline="white", width=2)
            return image

        def on_show(icon, item):
            self.after(0, self.restore_dock)
            
        def on_capture(icon, item):
            self.after(0, self.start_area_capture)
            
        def on_fullscreen(icon, item):
            self.after(0, self.start_fullscreen_capture)
            
        def on_quit(icon, item):
            self.after(0, self.quit_app)

        menu = pystray.Menu(
            item('Show Floating Dock 🖥', on_show),
            item('Capture Area 📸 (Ctrl+Shift+S)', on_capture),
            item('Capture Fullscreen 🖥', on_fullscreen),
            item('Exit completely ✖', on_quit)
        )
        self.tray_icon = pystray.Icon("PrintPulseScreenshot", create_tray_image(), "PrintPulse Screenshot Utility", menu)
        threading.Thread(target=self.tray_icon.run, daemon=True).start()

    # Background Keyboard Hotkey
    def setup_global_hotkey(self):
        MOD_CONTROL = 0x0002
        MOD_SHIFT = 0x0004
        WM_HOTKEY = 0x0312
        HOTKEY_ID = 127
        user32 = ctypes.windll.user32
        
        def hotkey_loop():
            registered = user32.RegisterHotKey(None, HOTKEY_ID, MOD_CONTROL | MOD_SHIFT, 0x53)
            if not registered:
                print("Failed to register global hotkey Ctrl+Shift+S.")
                return
            try:
                msg = wintypes.MSG()
                while user32.GetMessageW(ctypes.byref(msg), None, 0, 0) != 0:
                    if msg.message == WM_HOTKEY:
                        self.after(0, self.start_area_capture)
                    user32.TranslateMessage(ctypes.byref(msg))
                    user32.DispatchMessageW(ctypes.byref(msg))
            except Exception as e:
                print(f"Error in hotkey loop: {e}")
            finally:
                user32.UnregisterHotKey(None, HOTKEY_ID)
                
        threading.Thread(target=hotkey_loop, daemon=True).start()

if __name__ == '__main__':
    app = FloatingDock()
    app.mainloop()
