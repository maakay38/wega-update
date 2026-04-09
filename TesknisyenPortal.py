import os
import json
import urllib.request
import subprocess
import sys
import ctypes
from ctypes import wintypes

# --------------------------------------------------
# BASE PATH (launcher nerede ise her şey orada)
# --------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(sys.argv[0]))

APP_EXE_PATH = os.path.join(BASE_DIR, "WegaApp.exe")
VERSION_FILE = os.path.join(BASE_DIR, "app_version.txt")
TMP_EXE_PATH = os.path.join(BASE_DIR, "WegaApp_new.exe")

MANIFEST_URL = "https://raw.githubusercontent.com/maakay38/wega-update/main/manifest.json"
EXE_FALLBACK_URL = "https://raw.githubusercontent.com/maakay38/wega-update/main/fallback/WegaApp.exe"


# --------------------------------------------------
# UI helpers
# --------------------------------------------------
def show_message(title: str, message: str) -> None:
    """Basit Windows MessageBox (hata durumlarında kullanıcı bilgilendirme)."""
    try:
        ctypes.windll.user32.MessageBoxW(None, message, title, 0x00000000)  # MB_OK
    except Exception:
        pass


# --------------------------------------------------
# Desktop shortcut
# --------------------------------------------------
def _get_desktop_dir() -> str:
    try:
        class GUID(ctypes.Structure):
            _fields_ = [
                ("Data1", wintypes.DWORD),
                ("Data2", wintypes.WORD),
                ("Data3", wintypes.WORD),
                ("Data4", wintypes.BYTE * 8),
            ]

        import uuid

        def guid_from_str(s: str) -> GUID:
            u = uuid.UUID(s)
            g = GUID()
            g.Data1 = u.time_low
            g.Data2 = u.time_mid
            g.Data3 = u.time_hi_version
            g.Data4 = (wintypes.BYTE * 8).from_buffer_copy(u.bytes[8:])
            return g

        shell32 = ctypes.windll.shell32
        ole32 = ctypes.windll.ole32

        fid = guid_from_str("B4BFCC3A-DB2C-424C-B029-7FE99A87C641")  # Desktop
        ppath = ctypes.c_wchar_p()
        shell32.SHGetKnownFolderPath(ctypes.byref(fid), 0, None, ctypes.byref(ppath))
        path = ppath.value
        ole32.CoTaskMemFree(ppath)
        return path
    except Exception:
        return os.path.join(os.path.expanduser("~"), "Desktop")


def ensure_desktop_shortcut() -> None:
    """Masaüstünde TeknisyenPortal.lnk yoksa oluşturur (launcher exe'sine işaret eder)."""
    try:
        desktop = _get_desktop_dir()
        shortcut_path = os.path.join(desktop, "TeknisyenPortal.lnk")
        if os.path.exists(shortcut_path):
            return

        target = sys.executable  # PyInstaller exe
        workdir = BASE_DIR

        ps = (
            "$s=(New-Object -ComObject WScript.Shell).CreateShortcut"
            f"('{shortcut_path}');"
            f"$s.TargetPath='{target}';"
            f"$s.WorkingDirectory='{workdir}';"
            f"$s.IconLocation='{target},0';"
            "$s.Save()"
        )
        subprocess.run(
            ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            check=False,
        )
    except Exception:
        pass


# --------------------------------------------------
# Update helpers
# --------------------------------------------------
def ver_tuple(v: str):
    """'1.0.12' -> (1,0,12)"""
    try:
        return tuple(int(x) for x in v.strip().split("."))
    except Exception:
        return (0,)


def get_local_version() -> str:
    if not os.path.exists(VERSION_FILE):
        return "0.0.0"
    try:
        with open(VERSION_FILE, "r", encoding="utf-8") as f:
            return f.read().strip() or "0.0.0"
    except Exception:
        return "0.0.0"


def set_local_version(v: str) -> None:
    try:
        with open(VERSION_FILE, "w", encoding="utf-8") as f:
            f.write(v)
    except Exception:
        pass


def fetch_manifest() -> dict:
    req = urllib.request.Request(
        MANIFEST_URL,
        headers={"User-Agent": "Mozilla/5.0"},
        method="GET",
    )
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read().decode("utf-8", errors="ignore"))


def download(url: str, target: str) -> None:
    # urlretrieve bazı network ortamlarında daha stabil
    urllib.request.urlretrieve(url, target)


def is_valid_exe(path: str) -> bool:
    """Basit exe doğrulaması: dosya var mı, boyut makul mü, MZ header var mı."""
    try:
        if not os.path.exists(path):
            return False
        # Çok küçük dosyalar genelde HTML error sayfası vs. olur.
        if os.path.getsize(path) < 1 * 1024 * 1024:  # 1MB altını şüpheli say
            return False
        with open(path, "rb") as f:
            return f.read(2) == b"MZ"
    except Exception:
        return False


def download_with_fallback(primary_url: str, fallback_url: str, target: str) -> bool:
    """Primary indirme başarısızsa veya bozuk dosya geldiyse fallback'e düşer."""
    # 1) Primary
    try:
        download(primary_url, target)
        if is_valid_exe(target):
            return True
    except Exception:
        pass

    # 2) Fallback
    try:
        download(fallback_url, target)
        return is_valid_exe(target)
    except Exception:
        return False


def safe_remove(path: str) -> None:
    try:
        if os.path.exists(path):
            os.remove(path)
    except Exception:
        pass


def safe_replace(src: str, dst: str) -> None:
    """
    src -> dst değişimini güvenli yapmaya çalışır.
    Aynı diskteyse os.replace atomiktir.
    """
    try:
        os.replace(src, dst)
    except Exception:
        try:
            safe_remove(dst)
            os.rename(src, dst)
        except Exception:
            pass


# --------------------------------------------------
# Main
# --------------------------------------------------
def main() -> None:
    ensure_desktop_shortcut()

    try:
        manifest = fetch_manifest()
        latest = str(manifest.get("version", "0.0.0")).strip() or "0.0.0"
        url = str(manifest.get("download_url", "")).strip()

        local = get_local_version()

        # Güncelleme koşulu: manifest versiyonu daha büyükse VE download_url varsa
        if url and ver_tuple(latest) > ver_tuple(local):
            safe_remove(TMP_EXE_PATH)

            ok = download_with_fallback(url, EXE_FALLBACK_URL, TMP_EXE_PATH)
            if ok:
                safe_replace(TMP_EXE_PATH, APP_EXE_PATH)
                set_local_version(latest)
            else:
                safe_remove(TMP_EXE_PATH)

    except Exception:
        # Güncelleme hatasında sessizce mevcut app'i açmayı dene
        pass

    # Eğer APP_EXE yoksa fallback'ten bir kez çekmeyi dene
    if not os.path.exists(APP_EXE_PATH):
        try:
            safe_remove(TMP_EXE_PATH)
            if download_with_fallback(EXE_FALLBACK_URL, EXE_FALLBACK_URL, TMP_EXE_PATH):
                safe_replace(TMP_EXE_PATH, APP_EXE_PATH)
        except Exception:
            pass

    if os.path.exists(APP_EXE_PATH):
        subprocess.Popen([APP_EXE_PATH], cwd=BASE_DIR, shell=False)
        sys.exit(0)

    show_message(
        "TeknisyenPortal",
        "WegaApp.exe bulunamadı ve indirilemedi.\n"
        "İnternet bağlantınızı kontrol edip tekrar deneyin.",
    )
    sys.exit(1)


if __name__ == "__main__":
    main()
