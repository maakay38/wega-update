import os
import json
import urllib.request
import subprocess
import sys
import ctypes
import tkinter as tk
from tkinter import ttk

BASE_DIR = os.path.dirname(os.path.abspath(sys.argv[0]))

APP_EXE = os.path.join(BASE_DIR, "WegaApp.exe")
NEW_EXE = os.path.join(BASE_DIR, "WegaApp_new.exe")
VERSION_FILE = os.path.join(BASE_DIR, "app_version.txt")

MANIFEST_URL = "https://raw.githubusercontent.com/maakay38/wega-update/main/manifest.json"
FALLBACK_URL = "https://github.com/maakay38/wega-update/releases/latest/download/WegaApp.exe"


def msg(title, text):
    try:
        ctypes.windll.user32.MessageBoxW(0, text, title, 0)
    except:
        pass


def get_local_version():
    if not os.path.exists(VERSION_FILE):
        return "0.0.0"
    return open(VERSION_FILE).read().strip()


def set_local_version(v):
    with open(VERSION_FILE, "w") as f:
        f.write(v)


def ver(v):
    try:
        return tuple(map(int, v.split(".")))
    except:
        return (0,)


def get_manifest():
    req = urllib.request.Request(MANIFEST_URL, headers={"User-Agent": "Mozilla"})
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read().decode())


def download_with_progress(url, path):
    response = urllib.request.urlopen(url)
    total = int(response.getheader('Content-Length', 0))

    root = tk.Tk()
    root.title("Güncelleme")
    root.geometry("400x120")

    label = tk.Label(root, text="İndiriliyor...")
    label.pack(pady=10)

    progress = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate")
    progress.pack(pady=10)

    downloaded = 0

    with open(path, 'wb') as f:
        while True:
            chunk = response.read(1024)
            if not chunk:
                break
            f.write(chunk)
            downloaded += len(chunk)
            if total > 0:
                progress["value"] = (downloaded / total) * 100
            root.update()

    label.config(text="Kuruluyor...")
    root.update()
    root.destroy()


def valid_exe(path):
    return os.path.exists(path) and os.path.getsize(path) > 1000000


def update():
    try:
        data = get_manifest()
        latest = data.get("version", "0.0.0")
        url = data.get("download_url", "").strip()

        local = get_local_version()

        if url and ver(latest) > ver(local):

            msg("Güncelleme", f"Yeni sürüm bulundu: {latest}")

            if os.path.exists(NEW_EXE):
                os.remove(NEW_EXE)

            try:
                download_with_progress(url, NEW_EXE)
            except:
                download_with_progress(FALLBACK_URL, NEW_EXE)

            if valid_exe(NEW_EXE):
                if os.path.exists(APP_EXE):
                    try:
                        os.remove(APP_EXE)
                    except:
                        pass

                os.rename(NEW_EXE, APP_EXE)
                set_local_version(latest)

                msg("Güncelleme", "Güncelleme tamamlandı.")
            else:
                msg("Hata", "İndirilen dosya geçersiz.")

    except Exception as e:
        msg("Hata", f"Güncelleme hatası:\n{e}")


def main():
    update()

    if not os.path.exists(APP_EXE):
        msg("Bilgi", "Uygulama indiriliyor...")
        try:
            download_with_progress(FALLBACK_URL, APP_EXE)
        except:
            msg("Hata", "İndirilemedi.")
            return

    subprocess.Popen(APP_EXE, cwd=BASE_DIR)
    sys.exit()


if __name__ == "__main__":
    main()