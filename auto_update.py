import requests
import os, sys, subprocess
import tkinter as tk
from tkinter import ttk, messagebox

MANIFEST_URL = "https://raw.githubusercontent.com/maakay38/wega-update/main/manifest.json"
APP_PATH = "WegaApp.exe"
TEMP_FILE = "WegaApp_new.exe"

def get_remote():
    r = requests.get(MANIFEST_URL)
    d = r.json()
    return d["version"], d["download_url"]

def get_local():
    try:
        return open("version.txt").read().strip()
    except:
        return "0.0.0"

def update_app():
    rv, url = get_remote()
    lv = get_local()

    if rv == lv:
        messagebox.showinfo("Bilgi", "Güncel sürüm")
        return

    root = tk.Toplevel()
    root.title("Güncelleme")
    pb = ttk.Progressbar(root, length=300)
    pb.pack(pady=20)

    r = requests.get(url, stream=True)
    total = int(r.headers.get('content-length', 0))
    done = 0

    with open(TEMP_FILE, "wb") as f:
        for chunk in r.iter_content(1024):
            f.write(chunk)
            done += len(chunk)
            pb["value"] = done/total*100
            root.update()

    subprocess.Popen(f'''
    timeout 2
    del {APP_PATH}
    rename {TEMP_FILE} {APP_PATH}
    start {APP_PATH}
    ''', shell=True)

    sys.exit()
