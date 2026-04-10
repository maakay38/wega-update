import requests
import os
import sys
import subprocess
import tkinter as tk
from tkinter import messagebox

CURRENT_VERSION = "1.0.1"

VERSION_URL = "https://raw.githubusercontent.com/maakay38/wega-update/main/version.txt"
EXE_URL = "https://github.com/maakay38/wega-update/releases/latest/download/WegaApp.exe"


def check_for_update():
    try:
        response = requests.get(VERSION_URL)
        latest_version = response.text.strip()

        if latest_version != CURRENT_VERSION:
            answer = messagebox.askyesno(
                "Güncelleme Var",
                f"Yeni sürüm bulundu ({latest_version}). Güncellemek ister misiniz?"
            )

            if answer:
                download_update()

    except Exception as e:
        print("Update kontrol hatası:", e)


def download_update():
    try:
        response = requests.get(EXE_URL, stream=True)

        with open("WegaApp_new.exe", "wb") as f:
            for chunk in response.iter_content(1024):
                if chunk:
                    f.write(chunk)

        replace_and_restart()

    except Exception as e:
        messagebox.showerror("Hata", f"Güncelleme indirilemedi:\n{e}")


def replace_and_restart():
    try:
        bat_file = "update.bat"

        with open(bat_file, "w") as f:
            f.write(f"""
@echo off
timeout /t 2 > nul
del WegaApp.exe
rename WegaApp_new.exe WegaApp.exe
start WegaApp.exe
del %0
""")

        subprocess.Popen(bat_file, shell=True)
        sys.exit()

    except Exception as e:
        print("Update hata:", e)
# =========================
# GLOBAL STATE
# =========================
show_browser_var = None  # GUI'de tanımlanır (lint için placeholder)
STATE = {
    "driver": None,
    "wait": None,
    "logged_in": False,
}

# =========================
# WEGA TEK GUI OTOMASYON
# =========================

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import time
import threading

# =========================
# APP UPDATE (manifest)
# =========================
APP_VERSION = None  # app_version.txt varsa oradan okunur
MANIFEST_URL = "https://raw.githubusercontent.com/maakay38/wega-update/main/manifest.json"
EXE_FALLBACK_URL = "https://github.com/maakay38/wega-update/releases/latest/download/WegaApp.exe"

import json
import urllib.request
import webbrowser
import os
import sys

def ensure_workdir():
    """PyInstaller/_MEI gibi geçici dizinlerde cwd sorunlarını önlemek için.
    Çalışma dizinini uygulama dizinine (sys.argv[0]) çeker.
    """
    try:
        base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
        if base_dir and os.path.isdir(base_dir):
            os.chdir(base_dir)
    except Exception:
        pass
import traceback


# =========================
# NDF MODÜLÜ (GÖMÜLÜ)
# =========================
import pandas as pd
from tkinter import filedialog

NDF_URL = "https://docs.google.com/spreadsheets/d/1By97L4X7g-YVN6MiytOtvvf1gWOAzdE9pQWSXfhP4IM/export?format=csv&gid=759489617"

def open_ndf_window(parent=None):
    """NDF takip ekranını ayrı Toplevel pencerede açar."""
    try:
        df = pd.read_csv(NDF_URL)
        df.columns = df.columns.str.strip()

        teknisyen_col = "Adınızı Seçiniz"
        ulasildi_col = "Kullanıcıya Ulaşıldı Mı?"
        tarih_col = "Zaman damgası"

        eksik = [c for c in (teknisyen_col, ulasildi_col, tarih_col) if c not in df.columns]
        if eksik:
            raise ValueError("Eksik kolon(lar): " + ", ".join(eksik))

        df["Tarih"] = pd.to_datetime(df[tarih_col], dayfirst=True, errors="coerce")
        df["Ay"] = df["Tarih"].dt.month

        ay_sira = ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran", "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"]
        df["Ay_Ad"] = df["Ay"].map({i + 1: ay_sira[i] for i in range(12)})

        df["Durum"] = df[ulasildi_col].apply(
            lambda x: "Görüşme Yapıldı" if "Görüşme Yapıldı" in str(x) else "Cevap Yok"
        )

        win = tk.Toplevel(parent)
        win.title("NDF DURUM RAPORU")
        # RESPONSIVE SIZE
        screen_w = win.winfo_screenwidth()
        screen_h = win.winfo_screenheight()
        win_w = int(screen_w * 0.9)
        win_h = int(screen_h * 0.9)
        pos_x = int((screen_w - win_w) / 2)
        pos_y = int((screen_h - win_h) / 2)
        win.geometry(f"{win_w}x{win_h}+{pos_x}+{pos_y}")
        try:
            win.transient(parent)
        except Exception:
            pass

        title = tk.Label(win, text="NDF DURUM RAPORU", font=("Arial", 26, "bold"))
        title.pack(pady=10)

        frame_kpi = tk.Frame(win, bg="#1f2c3c")
        frame_kpi.pack(fill="x")

        kpi_toplam = tk.Label(frame_kpi, text="Toplam: 0", fg="white", bg="#1f2c3c", font=("Arial", 14, "bold"))
        kpi_basarili = tk.Label(frame_kpi, text="Başarılı: 0", fg="white", bg="#1f2c3c", font=("Arial", 14, "bold"))
        kpi_oran = tk.Label(frame_kpi, text="Başarı %: 0", fg="white", bg="#1f2c3c", font=("Arial", 14, "bold"))

        kpi_toplam.pack(side="left", padx=30, pady=10)
        kpi_basarili.pack(side="left", padx=30)
        kpi_oran.pack(side="left", padx=30)

        frame_top = tk.Frame(win)
        frame_top.pack(anchor="w", padx=20, pady=10)

        tk.Label(frame_top, text="Teknisyen:").grid(row=0, column=0)
        combo_teknisyen = ttk.Combobox(frame_top, values=sorted(df[teknisyen_col].dropna().astype(str).unique()), width=25, state="readonly")
        combo_teknisyen.grid(row=0, column=1, padx=(4, 16))

        tk.Label(frame_top, text="Ay:").grid(row=0, column=2)
        combo_ay = ttk.Combobox(frame_top, values=ay_sira, width=15, state="readonly")
        combo_ay.grid(row=0, column=3, padx=(4, 0))

        frame_main = tk.Frame(win)
        frame_main.pack(fill="both", expand=True)

        tree_detay = ttk.Treeview(frame_main, show="headings")
        tree_detay.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        tree_genel = ttk.Treeview(frame_main, show="headings")
        tree_genel.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        def autosize(tree, dataf):
            for col in dataf.columns:
                try:
                    max_len = max(dataf[col].astype(str).map(len).max(), len(str(col))) + 2
                except Exception:
                    max_len = len(str(col)) + 2
                tree.column(col, width=max_len * 8, anchor="center")
                tree.heading(col, text=col, anchor="center")

        pivot = pd.pivot_table(
            df,
            index=[teknisyen_col, "Durum"],
            columns="Ay_Ad",
            aggfunc="size",
            fill_value=0
        )
        pivot = pivot.reindex(columns=ay_sira, fill_value=0)
        pivot["Toplam"] = pivot.sum(axis=1)
        pivot = pivot.reset_index()

        tree_genel["columns"] = list(pivot.columns)
        autosize(tree_genel, pivot)
        for _, r in pivot.iterrows():
            tree_genel.insert("", "end", values=list(r))

        def analiz(event=None):
            teknisyen = combo_teknisyen.get()
            ay = combo_ay.get()
            if not teknisyen or not ay:
                return

            ay_num = ay_sira.index(ay) + 1
            f = df[(df[teknisyen_col].astype(str) == teknisyen) & (df["Ay"] == ay_num)]

            toplam = len(f)
            basarili = len(f[f["Durum"] == "Görüşme Yapıldı"])
            oran = round((basarili / toplam) * 100, 1) if toplam > 0 else 0

            kpi_toplam.config(text=f"Toplam: {toplam}")
            kpi_basarili.config(text=f"Başarılı: {basarili}")
            kpi_oran.config(text=f"Başarı %: {oran}")

            g = pd.DataFrame({
                "Durum": ["Görüşme Yapıldı", "Cevap Yok"],
                "Adet": [
                    len(f[f["Durum"] == "Görüşme Yapıldı"]),
                    len(f[f["Durum"] != "Görüşme Yapıldı"])
                ]
            })

            tree_detay["columns"] = ["Durum", "Adet"]
            autosize(tree_detay, g)
            tree_detay.delete(*tree_detay.get_children())
            for _, row in g.iterrows():
                tree_detay.insert("", "end", values=list(row))

        def excel_indir():
            file = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel", "*.xlsx")])
            if not file:
                return
            df.to_excel(file, index=False)

        bottom_frame = tk.Frame(win)
        bottom_frame.pack(fill="x", side="bottom")

        btn_excel = tk.Button(
            bottom_frame, text="📥 Excel İndir", command=excel_indir,
            bg="#1f2c3c", fg="white", font=("Arial", 10, "bold")
        )
        btn_excel.pack(pady=5)

        combo_teknisyen.bind("<<ComboboxSelected>>", analiz)
        combo_ay.bind("<<ComboboxSelected>>", analiz)

    except Exception as e:
        try:
            messagebox.showerror("NDF Hatası", f"NDF ekranı açılamadı.\n\nDetay: {e}", parent=parent)
        except Exception:
            print("NDF ekranı açılamadı:", e)


def get_local_chromedriver_path():
    """Uygulama klasöründeki chromedriver.exe yolunu döner (varsa)."""
    try:
        base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
        cd = os.path.join(base_dir, 'chromedriver.exe')
        return cd if os.path.exists(cd) else None
    except Exception:
        return None


def get_artifacts_dir():
    """Artifacts (screenshot/html) klasörü: yazma izni garanti olan dizin."""
    base = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")
    p = os.path.join(base, "WegaApp", "artifacts")
    os.makedirs(p, exist_ok=True)
    return p



def get_app_version() -> str:
    """Paket içindeki app_version.txt varsa onu okur; yoksa 0.0.0 döner."""
    try:
        base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
        vf = os.path.join(base_dir, "app_version.txt")
        if os.path.exists(vf):
            v = open(vf, "r", encoding="utf-8").read().strip()
            return v or "0.0.0"
    except Exception:
        pass
    return "0.0.0"

APP_VERSION = get_app_version()

SON_TEST_URL = "https://docs.google.com/spreadsheets/d/1OtFUevdr-B0AV9dz3lq1AboZF1z8ZfS_mddqtPp1-HA/edit?gid=196653180#gid=196653180"

ADMIN_CLEAR_PASSWORD = "1234"
REFRESH_AKTIF = True





def _is_onedrive_or_sharepoint(url: str) -> bool:
    low = (url or "").lower()
    return ("1drv.ms" in low) or ("onedrive.live.com" in low) or (".sharepoint.com" in low)

def normalize_download_url(url: str) -> str:
    """Sadece OneDrive/SharePoint paylaşım linklerini direct-download formatına yaklaştırır.
    Diğer (örn. GitHub RAW) linklerde URL'e dokunmaz.

    - ...?e=XXX?download=1 -> ...?e=XXX&download=1
    - download=1 yoksa ekler (onedrive.live.com/download hariç)
    """
    url = (url or "").strip()
    if not url:
        return url

    if not _is_onedrive_or_sharepoint(url):
        return url  # GitHub RAW vb. dokunma

    # Çift '?' hatasını düzelt
    if "?download=1" in url and url.count("?") > 1:
        url = url.replace("?download=1", "&download=1")

    low = url.lower()

    # Direkt indirme parametresi yoksa ekle
    if "onedrive.live.com/download" not in low and "download=1" not in low:
        url += ("&download=1" if "?" in url else "?download=1")

    return url


def _ver_tuple(v: str):
    """'1.0.12' -> (1,0,12)"""
    try:
        return tuple(int(x) for x in v.strip().split("."))
    except Exception:
        return (0,)



def validate_manifest(data: dict, fallback_url: str = ""):
    """manifest.json içeriğini doğrular. Hata varsa (errors, version, url, notes) döner."""
    errors = []

    version = str(data.get("version", "")).strip()
    url = str(data.get("download_url", "")).strip() or (fallback_url or "")
    url = normalize_download_url(url)
    notes = str(data.get("notes", "")).strip()

    # version kontrolü: 1.0.3 gibi
    if not version:
        errors.append("version alanı boş")
    else:
        parts = version.split(".")
        if not parts or not all(p.isdigit() for p in parts):
            errors.append(f"version formatı hatalı: {version} (örn: 1.0.3)")

    # url kontrolü
    if not url:
        errors.append("download_url alanı boş")
    else:
        low = url.lower()

        if not (low.startswith("http://") or low.startswith("https://")):
            errors.append("download_url http/https ile başlamıyor")

        # URL içinde birden fazla '?' varsa genellikle hatalıdır (örn: ...?e=xxx?download=1)
        if url.count("?") > 1:
            errors.append("download_url içinde birden fazla '?' var (örn: ...?e=xxx&download=1)")

        # OneDrive direct link (onedrive.live.com/download) ise download=1 şart değil.
        # GitHub RAW / GitHub Releases gibi linklerde de download=1 olmaz; bunları kabul et.
        is_onedrive_direct = "onedrive.live.com/download" in low
        is_github_raw = "raw.githubusercontent.com" in low
        is_github_release = ("/releases/download/" in low)
        is_dropbox = ("dropbox.com" in low)

        if not is_onedrive_direct and not is_github_raw and not is_github_release:
            # Dropbox/Drive gibi servislerde çoğunlukla "download=1" / "dl=1" gerekir.
            if ("download=1" not in low) and ("dl=1" not in low):
                errors.append("download_url direkt indirme linki değil (download=1 / dl=1 yok).")

    return errors, version, url, notes
def _fetch_manifest_json(url: str, timeout: int = 8) -> dict:
    """Manifest.json içeriğini çeker.

    Notlar:
    - Bazı servisler (özellikle paylaşım linkleri) JSON yerine HTML döndürebilir (link RAW/indirilebilir değilse).
    - Bu fonksiyon, JSON değilse anlaşılır bir hata fırlatır.
    """
    url = normalize_download_url(url)
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"
        },
        method="GET",
    )
    with urllib.request.urlopen(req, timeout=timeout) as r:
        raw = r.read()

    # BOM/whitespace temizle
    raw_l = raw.lstrip()

    # HTML mi döndü?
    if raw_l.startswith(b"<"):
        raise ValueError("Manifest JSON yerine HTML döndürdü (manifest linki RAW/indirilebilir değil).")

    # JSON mı?
    if not raw_l.startswith((b"{", b"[")):
        raise ValueError("manifest.json indirildi ama JSON formatında değil.")

    try:
        return json.loads(raw.decode("utf-8", errors="ignore"))
    except Exception as e:
        raise ValueError(f"manifest.json JSON parse hatası: {e}")



def check_update_on_startup(root):
    """
    NOT: Güncellemeyi sadece WegaLauncher yönetir (garanti ve tek otorite).
    Bu yüzden uygulama başlangıcında güncelleme zorunlu tutulmaz.
    Kullanıcı isterse arayüzdeki "Güncellemeyi Kontrol Et" butonuyla güncellemeyi tetikleyebilir.
    """
    return



def check_update_manual(root):
    """Kullanıcı isteğiyle güncelleme kontrolü yapar.

    Garanti yaklaşım:
    - Güncellemeyi yalnızca WegaLauncher yönetir (tek otorite).
    - Buradaki buton, mümkünse WegaLauncher.exe'yi çalıştırıp güncellemeyi ona devreder.
    - Launcher yoksa download_url tarayıcıda açılır.
    """
    try:
        data = _fetch_manifest_json(MANIFEST_URL, timeout=8)
        errors, latest, url, notes = validate_manifest(data, fallback_url=EXE_FALLBACK_URL)

        if errors:
            messagebox.showerror(
                "Manifest Hatası",
                "manifest.json hatalı:\n\n" + "\n".join(f"- {e}" for e in errors),
                parent=root
            )
            return

        # Yeni sürüm var mı?
        if latest and _ver_tuple(latest) > _ver_tuple(APP_VERSION):
            # Önce launcher'ı dene
            app_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
            launcher_exe = os.path.join(app_dir, "WegaLauncher.exe")

            launched = False
            try:
                if os.path.exists(launcher_exe):
                    import subprocess
                    subprocess.Popen([launcher_exe], cwd=app_dir, shell=False)
                    launched = True
            except Exception:
                launched = False

            if launched:
                messagebox.showinfo(
                    "Güncelleme",
                    f"Yeni sürüm mevcut: v{latest}\n\nGüncelleme için Launcher açıldı. Uygulama kapanacak.",
                    parent=root
                )
                try:
                    root.destroy()
                except Exception:
                    pass
                os._exit(0)
            else:
                # Launcher yoksa tarayıcıdan indir
                try:
                    webbrowser.open(url)
                except Exception:
                    pass
                messagebox.showinfo(
                    "Güncelleme",
                    f"Yeni sürüm mevcut: v{latest}\n\nİndirme bağlantısı tarayıcıda açıldı. İndirdikten sonra uygulamayı Launcher ile tekrar açın.",
                    parent=root
                )
                return

        # Güncel
        messagebox.showinfo(
            "Güncel",
            f"Uygulama güncel. (v{APP_VERSION})",
            parent=root
        )

    except Exception as e:
        messagebox.showwarning(
            "Güncelleme Kontrolü",
            "Güncelleme kontrolü yapılamadı.\n\nDetay: " + str(e) +
            "\n\nİpucu: Manifest linkinizin RAW/indirilebilir (JSON dönen) bir link olduğundan emin olun.",
            parent=root
        )



def dismiss_any_alert(driver, max_tries=2):
    """Beklenmedik alert varsa kapatır."""
    for _ in range(max_tries):
        try:
            a = driver.switch_to.alert
            _ = a.text
            try:
                a.accept()
            except Exception:
                a.dismiss()
            time.sleep(0.3)
        except Exception:
            break

def find_element_any_frame(driver, by, value, timeout=12, max_depth=4):
    """Elementi default content + tüm iframe'lerde arar, bulduğu frame'de bırakır."""
    end = time.time() + timeout
    last_err = None
    while time.time() < end:
        try:
            driver.switch_to.default_content()
        except Exception:
            pass
        try:
            el = driver.find_element(by, value)
            return el
        except Exception as e:
            last_err = e

        frames = driver.find_elements(By.TAG_NAME, "iframe")
        for fr in frames:
            try:
                driver.switch_to.default_content()
                driver.switch_to.frame(fr)
                el = driver.find_element(by, value)
                return el
            except Exception as e:
                last_err = e
                continue
        time.sleep(0.3)
    raise last_err if last_err else Exception(f"Element bulunamadı: {by}={value}")


from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

try:
    from WegaLogHelper import append_wega_log
except Exception:
    append_wega_log = None


# =========================
# TIME HELPERS (LOG + WAIT)
# =========================
def format_duration(seconds: float) -> str:
    """Süreyi mm:ss (gerekirse hh:mm:ss) formatına çevirir."""
    try:
        seconds = float(seconds)
    except Exception:
        return str(seconds)
    total = int(round(seconds))
    h = total // 3600
    m = (total % 3600) // 60
    s = total % 60
    return f"{h:02d}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"

def wait_page_ready(driver, timeout: int = 20):
    """document.readyState interactive/complete olana kadar bekler.
    page_load_strategy='eager' ile uyumlu (complete yerine interactive yeterli olabilir).
    """
    try:
        WebDriverWait(driver, timeout, poll_frequency=0.2).until(
            lambda d: d.execute_script("return document.readyState") in ("interactive", "complete")
        )
    except Exception:
        # Bazı sayfalarda readyState takılabiliyor; kırılmasın.
        pass

def wait_present(driver, by, value, timeout: int = 10):
    return WebDriverWait(driver, timeout, poll_frequency=0.2).until(
        EC.presence_of_element_located((by, value))
    )

def wait_clickable(driver, by, value, timeout: int = 10):
    return WebDriverWait(driver, timeout, poll_frequency=0.2).until(
        EC.element_to_be_clickable((by, value))
    )

def timed_call(label: str, fn, *args, **kwargs):
    """Bir fonksiyonu çalıştırır, süresini log'a yazar."""
    t0 = time.perf_counter()
    out = fn(*args, **kwargs)
    dt = time.perf_counter() - t0
    try:
        log_yaz(f"⏱ {label} süre: {format_duration(dt)}")
    except Exception:
        pass
    return out


# =========================
# KULLANICI BİLGİLERİ
# =========================
KULLANICI_ADI = "smartkayit"
SIFRE = "2134090"

# ✅ EKLENDİ: siparis_id global saklanacak
siparis_id_global = None


def try_append_daily_wega_log(imei: str, teknisyen: str, siparis_id: str = "", durum: str = "Tamamlandı"):
    """Günlük Wega raporu için CSV log kaydı ekler. Helper yoksa sessiz geçer."""
    try:
        if append_wega_log is None:
            return
        append_wega_log(imei, teknisyen, siparis_id, durum)
    except Exception as e:
        try:
            log_yaz(f"⚠️ Günlük log yazılamadı: {repr(e)}")
        except Exception:
            pass



def teknisyen_ata_onayli_clicked():
    """Sadece teknisyen atama adımını çalıştırır. Kaydetmeden önce onay sorar."""
    def _job():
        try:
            veri = read_form_data()
            imei = veri.get("imei") or ""
            teknisyen = veri.get("teknisyen") or ""
            if not str(imei).strip() or not str(teknisyen).strip():
                root.after(0, lambda: messagebox.showwarning("Uyarı", "Lütfen IMEI ve Teknisyen seçin."))
                return
            ensure_driver()
            ensure_logged_in()
            timed_call("Teknisyen Ata (Onaylı)", teknisyen_ata_stabil, STATE["driver"], STATE["wait"], imei, teknisyen)
        except Exception as e:
            log_yaz(f"❌ Teknisyen Ata (Onaylı) HATA: {repr(e)}")
            try:
                save_artifacts("Teknisyen_Ata_Onayli", STATE.get("driver"))
            except Exception:
                pass
        finally:
            root.after(0, lambda: set_buttons_state(True))

    set_buttons_state(False)
    threading.Thread(target=_job, daemon=True).start()

# =========================
# GUI LOG
# =========================
def log_yaz(metin):
    log.insert(tk.END, metin + "\n")
    log.see(tk.END)
    root.update_idletasks()


def ui_confirm_save(message="Kaydetmeyi onaylıyor musunuz?", title="Onay"):
    """Worker thread içinden çağrılabilir: Tk ana thread'de Yes/No popup açar."""
    ev = threading.Event()
    result = {"ok": False}


def ui_prompt_serial(message="Devam etmek için lütfen seri numarası girin:", title="Seri No Girişi"):
    """Worker thread içinden çağrılabilir: Tk ana thread'de input popup açar."""
    ev = threading.Event()
    result = {"val": None}

    def _ask():
        try:
            result["val"] = simpledialog.askstring(title, message, parent=root)
        except Exception:
            try:
                result["val"] = simpledialog.askstring(title, message)
            except Exception:
                result["val"] = None
        finally:
            ev.set()

    try:
        root.after(0, _ask)
        ev.wait()
        if result["val"] is None:
            return None
        v = str(result["val"]).strip()
        return v if v else None
    except Exception:
        return None

    def _ask():
        try:
            result["ok"] = bool(messagebox.askyesno(title, message, parent=root))
        except Exception:
            try:
                result["ok"] = bool(messagebox.askyesno(title, message))
            except Exception:
                result["ok"] = False
        finally:
            ev.set()

    try:
        root.after(0, _ask)
        ev.wait()
        return result["ok"]
    except Exception:
        return False


# =========================
# POPUP KAPAT
# =========================
def popup_kapat(driver):
    try:
        driver.switch_to.default_content()
        close_btn = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "img.close_image"))
        )
        close_btn.click()
        time.sleep(2)
        log_yaz("❎ Popup kapatıldı")
    except TimeoutException:
        pass



# =========================
# ŞEHİR ALANI (BOŞSA DOLDUR)
# =========================

def sehir_bos_ise_doldur(driver, wait, timeout=8, sehir_kodu="34"):
    """Şehir alanı bazen boş gelebiliyor.
    Boşsa sehir_kodu yazıp ENTER gönderir (işleyişi bozmadan, bulamazsa sessiz geçer).
    Not: Alan ID/NAME değişebileceği için olası locator'lar denenir ve iframe'ler de taranır.
    """
    locators = [
        # Wega - Şehir (Zorunlu) alanı (ekrandaki gerçek ID)
        (By.ID, "SoldToPartyAddress_Region"),
        (By.NAME, "SoldToPartyAddress_Region"),

        # Olası diğer şehir alanları (farklı ekran/versiyonlar)
        (By.ID, "City"),
        (By.ID, "Sehir"),
        (By.ID, "SehirKodu"),
        (By.ID, "CityCode"),
        (By.ID, "HeaderInfo_City"),
        (By.ID, "HeaderInfo_CityCode"),
        (By.ID, "CustomerInfo_City"),
        (By.ID, "CustomerInfo_CityCode"),
        (By.ID, "Address_City"),
        (By.NAME, "City"),
        (By.NAME, "Sehir"),
        (By.NAME, "CityCode"),
        (By.NAME, "SehirKodu"),
    ]

    for by, val in locators:
        try:
            el = find_element_any_frame(driver, by, val, timeout=1.5, max_depth=4)
        except Exception:
            continue

        try:
            current = (el.get_attribute("value") or "").strip()
        except Exception:
            current = ""

        if current == "":
            try:
                driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
            except Exception:
                pass
            try:
                el.clear()
            except Exception:
                try:
                    driver.execute_script("arguments[0].value='';", el)
                except Exception:
                    pass

            try:
                el.send_keys(sehir_kodu)
                el.send_keys(Keys.ENTER)
                log_yaz(f"🏙️ Şehir boştu, '{sehir_kodu}' yazıldı ve ENTER gönderildi")
            except Exception:
                try:
                    driver.execute_script(
                        """
                        try{
                            var el = arguments[0];
                            el.focus();
                            el.value = arguments[1];
                            el.dispatchEvent(new Event('input',{bubbles:true}));
                            el.dispatchEvent(new Event('change',{bubbles:true}));
                            var e = new KeyboardEvent('keydown', {key:'Enter', code:'Enter', which:13, keyCode:13, bubbles:true});
                            el.dispatchEvent(e);
                        }catch(e){}
                        """,
                        el,
                        sehir_kodu,
                    )
                    log_yaz(f"🏙️ Şehir boştu, '{sehir_kodu}' JS ile yazıldı")
                except Exception:
                    pass

            # seçim/autocomplete otursun diye çok kısa bekle
            try:
                time.sleep(0.4)
            except Exception:
                pass
        return  # ilk bulunan şehir alanı ile işi bitir

# =========================
# DRIVER
# =========================

def driver_olustur():
    options = webdriver.ChromeOptions()

    # ✅ Yöntem A: Arka planda çalıştır (pencere açmadan)
    # Headless seçimi GUI'den

    try:

        _show = bool(show_browser_var.get()) if show_browser_var is not None else False

    except Exception:

        _show = False

    if not _show:

        options.add_argument("--headless=new")
    else:
        options.add_argument("--start-maximized")
    options.add_argument("--window-size=1920,1080")

    # Daha hızlı ama stabil yükleme: DOM hazır olunca devam et (explicit wait'ler zaten var)
    try:
        options.page_load_strategy = "eager"
    except Exception:
        pass

    # Stabil + ufak hız kazanımları
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    # Otomasyon barı / bazı ekstra uyarıları azalt
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

        # ✅ Selenium Manager (Selenium 4.6+) ile driver'ı otomatik bul/indir.
    # webdriver_manager /.wdm cache hatalarını tamamen ortadan kaldırır.
    try:
        driver = webdriver.Chrome(options=options)
    except Exception:
        # Fallback: uygulama klasöründe chromedriver.exe varsa onu kullan
        local_cd = get_local_chromedriver_path()
        if not local_cd:
            raise
        driver = webdriver.Chrome(service=Service(local_cd), options=options)
    wait = WebDriverWait(driver, 60)
    return driver, wait

# =========================
# LOGIN
# =========================


def menuye_tikla_ve_git(driver, wait, href, text_icinde=None, timeout=30):
    """Sol menüden linke tıklayarak sayfaya gider.
    Eski filtre/MemoryFilter kalıntılarını azaltmak için URL yerine tıklama tercih edilir.
    Bulamazsa driver.get ile fallback yapar.
    """
    try:
        driver.switch_to.default_content()
    except Exception:
        pass

    xpath = f"//a[contains(@href, '{href}')]" if not text_icinde else f"//a[contains(@href, '{href}') and contains(normalize-space(.), '{text_icinde}')]"
    try:
        el = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((By.XPATH, xpath)))
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
        el.click()
        # sayfa geçişini bekle
        WebDriverWait(driver, timeout).until(lambda d: href.lower() in d.current_url.lower())
        return
    except Exception:
        # Fallback: cache/param kırmak için rnd ekle
        try:
            base = "https://destekwega.com" + href
            driver.get(base + ("?rnd=" + str(int(time.time()*1000))))
        except Exception:
            driver.get("https://destekwega.com" + href)
        time.sleep(2)

def memory_filter_temizle(driver):
    """Sayfadaki MemoryFilter inputlarını temizler (varsa)."""
    try:
        driver.execute_script("""
            document.querySelectorAll('input.MemoryFilter').forEach(function(x){
                try{ x.value=''; x.dispatchEvent(new Event('input', {bubbles:true})); x.dispatchEvent(new Event('change', {bubbles:true})); }catch(e){}
            });
        """)
    except Exception:
        pass

def login(driver, wait):
    log_yaz("🔐 Login yapılıyor")
    driver.get("https://destekwega.com/")
    try:
        driver.set_window_size(1920, 1080)
    except Exception:
        pass
    wait.until(EC.presence_of_element_located((By.ID, "UserName"))).send_keys(KULLANICI_ADI)
    driver.find_element(By.NAME, "Password").send_keys(SIFRE + Keys.ENTER)
    time.sleep(4)
    log_yaz("✅ Login OK")


# =========================
# NAV (MENÜDEN TIKLAYARAK) - SADECE TEKNİSYEN ATA / FULL FLOW İÇİN
# =========================
def goto_repair_order_management_via_menu(driver, wait, timeout=25):
    """Login sonrası sol menüden tıklama ile 'Tamir siparişi yönetimi' sayfasına gider:
    1) 'Servis işlemleri' (ShowHide('CSOperations'))
    2) 'Tamir siparişi yönetimi' (/CustomerService/RepairOrderManagement.aspx)
    """
    try:
        driver.switch_to.default_content()
    except Exception:
        pass

    # 1) Servis işlemleri menüsünü aç
    try:
        servis_el = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((
                By.XPATH,
                "//a[contains(@onclick,'ShowHide') and contains(@onclick,'CSOperations') and contains(normalize-space(.),'Servis işlemleri')]"
            ))
        )
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", servis_el)
        try:
            servis_el.click()
        except Exception:
            driver.execute_script("arguments[0].click();", servis_el)
        time.sleep(0.4)
    except Exception:
        pass

    # 2) Tamir siparişi yönetimi
    tamir_el = WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((
            By.XPATH,
            "//a[contains(@href,'/CustomerService/RepairOrderManagement.aspx') and contains(normalize-space(.),'Tamir siparişi yönetimi')]"
        ))
    )
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", tamir_el)
    try:
        tamir_el.click()
    except Exception:
        driver.execute_script("arguments[0].click();", tamir_el)

    # IMEI input gelene kadar bekle (iframe olasılığı için fallback)
    try:
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.ID, "RepairOrderAssignments_SerialNo"))
        )
    except Exception:
        try:
            WebDriverWait(driver, 5).until(
                EC.frame_to_be_available_and_switch_to_it((By.TAG_NAME, "iframe"))
            )
        except Exception:
            pass
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.ID, "RepairOrderAssignments_SerialNo"))
        )
        try:
            driver.switch_to.default_content()
        except Exception:
            pass


# =========================
# KAYIT BUL
# =========================

def kayit_bul(driver, wait, imei):
    global siparis_id_global  # ✅ EKLENDİ

    log_yaz("📦 Ürün Kabul Listesi")

    driver.find_element(By.LINK_TEXT, "Servis işlemleri").click()
    wait.until(
        EC.element_to_be_clickable((By.XPATH, "//a[text()='Ürün Kabul Listesi']"))
    ).click()
    time.sleep(5)

    wait.until(EC.frame_to_be_available_and_switch_to_it((By.TAG_NAME, "iframe")))

    driver.execute_script("""
        var cb = document.getElementById('RepairOrderList_ViewLocalRepairOrders');
        if(cb){
            cb.checked = true;
            cb.dispatchEvent(new Event('change',{bubbles:true}));
        }
    """)
    time.sleep(2)

    box = driver.find_element(By.ID, "RepairOrderList_SerialNo")
    box.clear()
    box.send_keys(imei + Keys.ENTER)
    time.sleep(6)

    try:
        link = WebDriverWait(driver, 12, poll_frequency=0.2).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href*='RepairOrder.aspx?ID=']"))
        )
    except TimeoutException:
        # IMEI arama sonucu gelmediyse süreç durdurulsun
        try:
            driver.switch_to.default_content()
        except Exception:
            pass
        uyari = "Aktarım Henüz Tamamlanmamış. Lütfen Daha Sonra Tekrar Deneyin. "
        try:
            log_yaz("⚠️ " + uyari)
        except Exception:
            pass
        try:
            messagebox.showwarning("Uyarı", uyari)
        except Exception:
            pass
        raise Exception(uyari)

    siparis_id = link.get_attribute("href").split("ID=")[-1]

    # ✅ EKLENDİ: siparis id global sakla
    siparis_id_global = siparis_id
    log_yaz(f"🆔 Sipariş ID kaydedildi: {siparis_id_global}")

    driver.switch_to.default_content()
    driver.get(f"https://destekwega.com/CustomerService/RepairOrderEdit.aspx?ID={siparis_id}")
    time.sleep(6)


# =========================
# SERİ NO. YARAT (IMEI sistemde yoksa)
# =========================
def ensure_serial_created_if_needed(driver, wait, imei, timeout=10):
    """IMEI girildikten sonra 'Seri numarası bulunamadı' çıkarsa teknisyenden seri no ister,
    'Seri No. Yarat' akışını otomatik tamamlar ve tekrar IMEI'yi okutmayı dener.

    - Link/uyarı iframe içinde olabilir (any-frame arar)
    - 'Kaydet' butonuna basınca ekran kendi kendine kapanabilir; bunu doğru yönetir.
    """
    # Ana DOM
    try:
        driver.switch_to.default_content()
    except Exception:
        pass

    # Tetik var mı? (Seri No. Yarat linki veya kırmızı uyarı)
    link_el = None
    red_hit = False
    try:
        link_el = find_element_any_frame(
            driver, By.XPATH, "//a[contains(normalize-space(.),'Seri No. Yarat')]",
            timeout=2.5, max_depth=5
        )
    except Exception:
        link_el = None

    if link_el is None:
        try:
            _ = find_element_any_frame(
                driver, By.XPATH,
                "//*[contains(translate(normalize-space(.),'İI','ii'),'seri numarası bulunamadı')]",
                timeout=1.5, max_depth=5
            )
            red_hit = True
        except Exception:
            red_hit = False

    if (link_el is None) and (not red_hit):
        return  # ihtiyaç yok

    seri_no = ui_prompt_serial()
    if not seri_no:
        raise Exception("Seri numarası girilmedi (Seri No. Yarat gerekli).")

    # Popup yönetimi için handle'ları LINK'e basmadan önce al
    base_handle = None
    handles_before = None
    try:
        base_handle = driver.current_window_handle
        handles_before = set(driver.window_handles)
    except Exception:
        base_handle = None
        handles_before = None

    # Linki tıkla (yeniden yakala)
    try:
        link_click = find_element_any_frame(
            driver, By.XPATH, "//a[contains(normalize-space(.),'Seri No. Yarat')]",
            timeout=6, max_depth=5
        )
        try:
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", link_click)
            driver.execute_script("arguments[0].click();", link_click)
        except Exception:
            link_click.click()
    except Exception:
        return

    # Yeni pencere açıldıysa ona geç (5 sn bekle)
    popup_handle = None
    if handles_before is not None:
        for _ in range(25):
            try:
                handles_now = set(driver.window_handles)
                new_handles = list(handles_now - handles_before)
                if new_handles:
                    popup_handle = new_handles[0]
                    break
            except Exception:
                pass
            time.sleep(0.2)

    if popup_handle:
        try:
            driver.switch_to.window(popup_handle)
        except Exception:
            pass

    # iframe olabilir
    try:
        wait.until(EC.frame_to_be_available_and_switch_to_it((By.TAG_NAME, "iframe")))
    except Exception:
        pass

    # Cep Telefonu Seri No alanı çıkarsa doldur
    try:
        mpn = find_element_any_frame(driver, By.ID, "ManufacturerPartNumber", timeout=timeout, max_depth=5)
        try:
            mpn.clear()
        except Exception:
            pass
        mpn.send_keys(seri_no)
        log_yaz(f"🧾 Seri No girildi: {seri_no}")

        # Kaydet butonu: id=ItemDetailButton
        btn = find_element_any_frame(driver, By.ID, "ItemDetailButton", timeout=timeout, max_depth=5)

        # Kaydet'e bas — bu tıklama bazı sayfalarda popup'ı otomatik kapatır
        try:
            driver.execute_script("arguments[0].click();", btn)
        except Exception:
            btn.click()

        # Kaydet sonrası: alert/popup kapanması bekle
        try:
            WebDriverWait(driver, 2).until(EC.alert_is_present())
            dismiss_any_alert(driver)
        except Exception:
            pass

        # Pencere kendi kendine kapandı mı?
        if handles_before is not None:
            for _ in range(20):
                try:
                    if set(driver.window_handles) == handles_before:
                        break
                except Exception:
                    break
                time.sleep(0.2)

        time.sleep(0.4)
    except Exception:
        # Alan çıkmadıysa yoksay (bazı hesaplarda bu ekran gelmeyebilir)
        pass

    # Eğer popup hala açıksa kapat ve ana pencereye dön
    try:
        if base_handle and driver.current_window_handle != base_handle:
            try:
                driver.close()
            except Exception:
                pass
            try:
                driver.switch_to.window(base_handle)
            except Exception:
                pass
    except Exception:
        pass

    try:
        driver.switch_to.default_content()
    except Exception:
        pass

    # IMEI'yi tekrar okut
    try:
        sn = driver.find_element(By.ID, "MaterialInfo_SerialNo")
        try:
            sn.clear()
        except Exception:
            pass
        sn.send_keys(str(imei) + Keys.ENTER)
        time.sleep(1.0)
    except Exception:
        pass

def kayit_kaydet(driver, wait, imei, garanti_gui):
    log_yaz("📝 Kayıt dolduruluyor")

    driver.find_element(By.ID, "MaterialInfo_SerialNo").clear()
    driver.find_element(By.ID, "MaterialInfo_SerialNo").send_keys(imei + Keys.ENTER)
    time.sleep(2)

    # IMEI sistemde yoksa 'Seri No. Yarat' akışını otomatik tamamla
    ensure_serial_created_if_needed(driver, wait, imei)
    garanti_map = {"Garanti İçi": "GI", "Garanti Dışı": "GD"}
    Select(driver.find_element(By.ID, "WarrantyStatus")) \
        .select_by_value(garanti_map.get(garanti_gui))

    Select(driver.find_element(By.ID, "ShippingConditions")) \
        .select_by_visible_text("01 - Elden Teslim")

    Select(driver.find_element(By.ID, "HeaderInfo_Priority")) \
        .select_by_index(1)

    
    # Şehir alanı boş gelirse otomatik doldur (34 + ENTER)
    sehir_bos_ise_doldur(driver, wait, timeout=8, sehir_kodu="34")
    log_yaz("💾 Kaydet")
    driver.execute_script("""
        $('#DefaultFormAction').val('SaveForm');
        SaveOrder(this);
    """)
    time.sleep(4)

    popup_kapat(driver)

    # ✅ Kaydet sonrası durum kontrolü (Ön bildirim -> Arıza kabul düzeltmesi)
    ensure_ariza_kabul_status_or_warn(driver, wait, timeout=25)

    log_yaz("✅ Kayıt kaydedildi")


# =========================
# DURUM KONTROL / ÖN BİLDİRİM FIX
# =========================

def get_order_status_text(driver, timeout=6):
    """Kayıt ekranındaki 'Durum' hücresindeki metni okur."""
    try:
        driver.switch_to.default_content()
    except Exception:
        pass

    xps = [
        "//*[self::td or self::th][normalize-space(.)='Durum']/following::td[1]",
        "//*[self::td or self::th][contains(normalize-space(.),'Durum')]/following::td[1]",
        "//td[contains(normalize-space(.),'Ön bildirim yapıldı') or contains(normalize-space(.),'Arıza kabul yapıldı')]",
    ]
    for xp in xps:
        try:
            el = find_element_any_frame(driver, By.XPATH, xp, timeout=timeout, max_depth=6)
            txt = (el.text or "").strip()
            if txt:
                return txt
        except Exception:
            continue

    # Son çare: HTML içinde ara
    try:
        html = driver.page_source or ""
        if "Ön bildirim yapıldı" in html:
            return "Ön bildirim yapıldı"
        if "Arıza kabul yapıldı" in html:
            return "Arıza kabul yapıldı"
    except Exception:
        pass

    return ""


def fix_on_bildirim_to_ariza_kabul(driver, wait, timeout=25):
    """Ön bildirim -> Arıza kabul düzeltmesi:
    Siparişi Değiştir -> Teslimat -> Tamir iadesi oluştur -> OLUŞTUR -> Kapat"""
    try:
        driver.switch_to.default_content()
    except Exception:
        pass

    # 1) Siparişi Değiştir
    edit_link = find_element_any_frame(
        driver,
        By.XPATH,
        "//a[contains(@href,'RepairOrderEdit.aspx?SAPID=') and contains(normalize-space(.),'Siparişi Değiştir')]",
        timeout=timeout,
        max_depth=6
    )
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", edit_link)
    driver.execute_script("arguments[0].click();", edit_link)
    time.sleep(0.8)
    dismiss_any_alert(driver)

    # 2) Teslimat
    teslimat = find_element_any_frame(
        driver,
        By.XPATH,
        "//a[normalize-space(.)='Teslimat' and (contains(@onclick,'return false') or @href='')] | //a[normalize-space(.)='Teslimat']",
        timeout=timeout,
        max_depth=6
    )
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", teslimat)
    driver.execute_script("arguments[0].click();", teslimat)
    time.sleep(0.6)

    # 2b) Tamir iadesi oluştur
    tamir = find_element_any_frame(
        driver,
        By.XPATH,
        "//*[self::a or self::button or self::input][contains(normalize-space(.),'Tamir iadesi oluştur') or @value='Tamir iadesi oluştur']",
        timeout=timeout,
        max_depth=6
    )
    driver.execute_script("arguments[0].click();", tamir)
    time.sleep(0.8)

    # 3) OLUŞTUR
    olustur = find_element_any_frame(
        driver,
        By.XPATH,
        "//input[@type='button' and contains(translate(@value,'abcçdefgğhıijklmnoöprsştuüvyz','ABCÇDEFGĞHIİJKLMNOÖPRSŞTUÜVYZ'),'OLUŞTUR')]"
        " | //button[contains(normalize-space(.),'OLUŞTUR')]",
        timeout=timeout,
        max_depth=6
    )
    driver.execute_script("arguments[0].click();", olustur)
    time.sleep(1.0)

    # 4) Popup kapat
    try:
        btn = find_element_any_frame(driver, By.CSS_SELECTOR, "img.close_image", timeout=3, max_depth=6)
        driver.execute_script("arguments[0].click();", btn)
    except Exception:
        try:
            btn = find_element_any_frame(driver, By.XPATH, "//img[contains(@src,'close.gif') or contains(@title,'close')]", timeout=3, max_depth=6)
            driver.execute_script("arguments[0].click();", btn)
        except Exception:
            pass

    time.sleep(0.6)
    dismiss_any_alert(driver)


def ensure_ariza_kabul_status_or_warn(driver, wait, timeout=25):
    st = get_order_status_text(driver)
    if not st:
        return

    if "Arıza kabul yapıldı" in st:
        return

    if "Ön bildirim yapıldı" in st:
        log_yaz("ℹ️ Durum 'Ön bildirim yapıldı'. Otomatik düzeltme deneniyor...")
        try:
            fix_on_bildirim_to_ariza_kabul(driver, wait, timeout=timeout)
        except Exception as e:
            log_yaz(f"⚠️ Otomatik düzeltme adımında hata: {repr(e)}")

        st2 = get_order_status_text(driver, timeout=8)
        if "Arıza kabul yapıldı" in (st2 or ""):
            log_yaz("✅ Durum düzeldi: Arıza kabul yapıldı")
            return

        uy = "Cihaz ön bildirimde kaldı, yöneticinize başvurun."
        log_yaz("⚠️ " + uy)
        try:
            messagebox.showwarning("Uyarı", uy)
        except Exception:
            pass
        raise Exception(uy)

    uy = f"Durum beklenenden farklı: {st}. Yöneticinize başvurun."
    log_yaz("⚠️ " + uy)
    try:
        messagebox.showwarning("Uyarı", uy)
    except Exception:
        pass
    raise Exception(uy)

# =========================
# DEPARTMANA YOLLA
# =========================

def departmana_yolla(driver, wait, imei, timeout=20):
    """Departmana yolla adımı (hızlandırılmış).
    - IMEI'yi JS ile basar (send_keys gecikmesini azaltır)
    - Input gelir gelmez window.stop() ile kalan yüklemeleri durdurur
    - Search/Send işlemlerini DefaultFormAction + submit ile tetikler
    """
    log_yaz("📤 Departmana Yolla")

    sn = open_status_page_and_wait_input(
        driver,
        status_code="0002",
        input_id="CollectiveStatusUpdate_SerialNo",
        timeout=timeout
    )

    # IMEI'yi çok hızlı set et
    fast_set_value_js(driver, sn, imei)

    # Search
    driver.execute_script("""
        try{
            if(window.$ && $('#DefaultFormAction').length){ $('#DefaultFormAction').val('Search'); }
            if(document.DefaultForm){ document.DefaultForm.submit(); }
        }catch(e){}
    """)

    # Sonuç gelinceye kadar bekle
    find_element_any_frame(driver, By.XPATH, "//input[@value='Tümünü Seç']", timeout=timeout, max_depth=6)

    # Tümünü seç + Departmana gönder
    driver.execute_script("""
        try{
            var btn = document.querySelector('input[value="Tümünü Seç"]');
            if(btn){ CheckAll(btn); }
        }catch(e){}
        try{
            if(window.$ && $('#DefaultFormAction').length){ $('#DefaultFormAction').val('SendToDepartment'); }
            if(document.DefaultForm){ document.DefaultForm.submit(); }
        }catch(e){}
    """)

    try:
        driver.switch_to.default_content()
    except Exception:
        pass

    popup_kapat(driver)
    dismiss_any_alert(driver)
    log_yaz("✅ Departmana gönderildi")


# =========================
# DEPARTMAN KABUL (TEK CHECKBOX – STABİL + YÖNETİME DÖN)
# =========================

def departman_kabul(driver, wait, imei, timeout=20):
    """Departman kabul adımı (hızlandırılmış).
    - IMEI'yi JS ile basar
    - Input gelir gelmez window.stop()
    - Search/Accept işlemlerini submit ile tetikler
    """
    log_yaz("📥 Departman Kabul")

    sn = open_status_page_and_wait_input(
        driver,
        status_code="0003",
        input_id="CollectiveStatusUpdate_SerialNo",
        timeout=timeout
    )

    fast_set_value_js(driver, sn, imei)

    # Search
    driver.execute_script("""
        try{
            if(window.$ && $('#DefaultFormAction').length){ $('#DefaultFormAction').val('Search'); }
            if(document.DefaultForm){ document.DefaultForm.submit(); }
        }catch(e){}
    """)

    # Checkbox gelene kadar bekle
    cb = find_element_any_frame(driver, By.CSS_SELECTOR, "input.CanSelectForAll[type='checkbox']", timeout=timeout, max_depth=6)

    # Kabul et
    driver.execute_script("""
        try{
            var cb = arguments[0];
            if(cb){
                cb.checked = true;
                cb.dispatchEvent(new Event('change', {bubbles:true}));
            }
            if(window.$ && $('#DefaultFormAction').length){ $('#DefaultFormAction').val('AcceptToDepartment'); }
            if(document.DefaultForm){ document.DefaultForm.submit(); }
        }catch(e){}
    """, cb)

    try:
        driver.switch_to.default_content()
    except Exception:
        pass

    popup_kapat(driver)
    dismiss_any_alert(driver)
    log_yaz("✅ Departman Kabul başarıyla yapıldı")


# =========================
# TEKNİSYEN ATA (v2 - ARAMA + SEÇİM + KAYDET STABİL)
# =========================
# =========================
# TEKNİSYEN ATA (STABİL – TEK AKIŞ)
# =========================

def teknisyen_ata_stabil(driver, wait, imei, teknisyen, timeout=25, confirm_before_save=False):
    """Tamir siparişi yönetiminde IMEI'yi bulup seçer ve teknisyen ataması yapar.
    - GUI'de teknisyen bazen "KOD - Ad Soyad" gelir: KOD otomatik ayıklanır.
    - IMEI sadece rakama indirgenir.
    - Kullanıcı onayı kaldırıldı (tam otomatik).
    """
    import re as _re

    imei_raw = str(imei).strip()
    imei_digits = _re.sub(r"\D", "", imei_raw)

    teknisyen_raw = str(teknisyen).strip()
    teknisyen_kod = teknisyen_raw.split(" - ")[0].strip() if " - " in teknisyen_raw else teknisyen_raw
    if " " in teknisyen_kod:
        first = teknisyen_kod.split()[0].strip()
        if first:
            teknisyen_kod = first

    log_yaz(f"👨‍🔧 Teknisyen atanıyor: {teknisyen_raw} (kod: {teknisyen_kod})")

    if not imei_digits:
        raise Exception("IMEI boş/uygunsuz")
    if not teknisyen_kod:
        raise Exception("Teknisyen seçilmedi")

    try:
        driver.switch_to.default_content()
    except Exception:
        pass
    dismiss_any_alert(driver)

    goto_home_page(driver, wait)
    dismiss_any_alert(driver)

    try:
        servis_el = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((By.XPATH, "//a[contains(@onclick,'ShowHide') and contains(@onclick,'CSOperations')]"))
        )
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", servis_el)
        driver.execute_script("arguments[0].click();", servis_el)
        time.sleep(0.35)
    except Exception:
        pass

    tamir_el = WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((By.XPATH, "//a[contains(@href,'/CustomerService/RepairOrderManagement.aspx') and contains(normalize-space(.),'Tamir siparişi yönetimi')]"))
    )
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", tamir_el)
    driver.execute_script("arguments[0].click();", tamir_el)
    time.sleep(0.9)
    dismiss_any_alert(driver)

    memory_filter_temizle(driver)


    # Sayfa/iframe tam açılsın: IMEI input görünene kadar bekle
    imei_input = find_element_any_frame(driver, By.ID, "RepairOrderAssignments_SerialNo", timeout=timeout, max_depth=5)

    memory_filter_temizle(driver)

    try:
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", imei_input)
        driver.execute_script("arguments[0].focus();", imei_input)
    except Exception:
        pass

    try:
        imei_input.clear()
    except Exception:
        try:
            driver.execute_script("arguments[0].value='';", imei_input)
        except Exception:
            pass

    imei_input.send_keys(imei_digits)
    imei_input.send_keys(Keys.ENTER)
    log_yaz("🔎 IMEI yazıldı ve ENTER gönderildi")
    time.sleep(1.2)
    dismiss_any_alert(driver)

    # Sonuç tablosu gelsin
    # (satır bulunamazsa Search submit fallback aşağıda devreye girer)

    row_xpath = (
        "//tr[.//input[@type='checkbox' and (contains(@name,'Assign_') or @rel='RepairOrderAssignments' or contains(@class,'CanSelectForAll'))]"
        f" and (.//td[normalize-space(.)='{imei_digits}' or contains(normalize-space(.), '{imei_digits}')]"
        f"      or .//td[contains(normalize-space(.), '{imei_raw}')])]"
    )

    try:
        WebDriverWait(driver, 8).until(EC.presence_of_element_located((By.XPATH, row_xpath)))
    except Exception:
        log_yaz("⚠️ ENTER sonuç geç geldi, Search submit (tek sefer) deneniyor")
        try:
            js = (
                "try{"
                "var el=document.getElementById('RepairOrderAssignments_SerialNo');"
                "if(el){el.focus();el.value=arguments[0];"
                "el.dispatchEvent(new Event('input',{bubbles:true}));"
                "el.dispatchEvent(new Event('change',{bubbles:true}));}"
                "if(window.$ && $('#DefaultFormAction').length){$('#DefaultFormAction').val('Search');}"
                "if(document.DefaultForm){document.DefaultForm.submit();}"
                "}catch(e){}"
            )
            driver.execute_script(js, imei_digits)
        except Exception:
            pass
        time.sleep(1.8)
        dismiss_any_alert(driver)

    try:
        row = WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.XPATH, row_xpath)))
    except Exception:
        row = find_element_any_frame(driver, By.XPATH, row_xpath, timeout=timeout, max_depth=4)

    try:
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", row)
    except Exception:
        pass
    time.sleep(0.2)

    row_cb = row.find_element(By.XPATH, ".//input[@type='checkbox' and (@rel='RepairOrderAssignments' or contains(@name,'Assign_') or contains(@class,'CanSelectForAll'))]")
    if not row_cb.is_selected():
        try:
            driver.execute_script("arguments[0].click();", row_cb)
        except Exception:
            row_cb.click()

    log_yaz(f"☑️ Yazılan IMEI satırı seçildi: {imei_digits}")

    tech_row_xpath = (
        f"//table[@id='table2']//tr[.//td[normalize-space(.)='{teknisyen_kod}' or contains(normalize-space(.), '{teknisyen_kod}')]]"
        f" | //tr[.//td[normalize-space(.)='{teknisyen_kod}' or contains(normalize-space(.), '{teknisyen_kod}')]]"
    )

    try:
        tech_row = WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.XPATH, tech_row_xpath)))
    except Exception:
        tech_row = find_element_any_frame(driver, By.XPATH, tech_row_xpath, timeout=timeout, max_depth=4)

    try:
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", tech_row)
    except Exception:
        pass
    time.sleep(0.2)

    try:
        tech_radio = tech_row.find_element(By.XPATH, f".//input[@type='radio' and @name='SelectedWorkCenter' and (@value='{teknisyen_kod}' or contains(@value,'{teknisyen_kod}'))]")
    except Exception:
        tech_radio = tech_row.find_element(By.XPATH, ".//input[@type='radio' and @name='SelectedWorkCenter']")

    if not tech_radio.is_selected():
        try:
            driver.execute_script("arguments[0].click();", tech_radio)
        except Exception:
            tech_radio.click()

    log_yaz("🧑‍🔧 Teknisyen seçildi")

    if confirm_before_save:
        msg = f"IMEI {imei_digits} için teknisyen '{teknisyen_raw}' atanacak. Kaydedilsin mi?"
        if not ui_confirm_save(message=msg):
            log_yaz("⏸ Teknisyen atama kaydı kullanıcı tarafından iptal edildi")
            return

    save_xpath = (
        "//a[contains(@onclick,\"$('#DefaultFormAction').val('SaveForm')\") and contains(@onclick,'SaveOrder')]"
        " | //a[.//img[contains(@src,'btnSaveForm.gif')] and contains(normalize-space(.),'Kaydet')]"
        " | //input[@type='image' and contains(@src,'btnSaveForm')]"
    )
    try:
        save_btn = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((By.XPATH, save_xpath)))
    except Exception:
        save_btn = find_element_any_frame(driver, By.XPATH, save_xpath, timeout=timeout, max_depth=4)

    try:
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", save_btn)
    except Exception:
        pass

    try:
        driver.execute_script("if(window.$ && $('#DefaultFormAction').length){$('#DefaultFormAction').val('SaveForm');}")
    except Exception:
        pass

    try:
        # Önce onclick içindeki akışı JS ile tetikle (en stabil)
        driver.execute_script(
            """
            try{ if(window.$ && $('#DefaultFormAction').length){ $('#DefaultFormAction').val('SaveForm'); } }catch(e){}
            try{ if(typeof SaveOrder === 'function'){ SaveOrder(arguments[0]); } }catch(e){}
            try{ arguments[0].click(); }catch(e){}
            """,
            save_btn,
        )
    except Exception:
        try:
            save_btn.click()
        except Exception:
            driver.execute_script("arguments[0].click();", save_btn)

    log_yaz("💾 Kaydet'e basıldı. Popup gelirse en fazla 10 sn bekleyip devam ediyorum...")
    # kısa postback bekle
    try:
        wait_page_ready(driver, timeout=min(10, timeout))
    except Exception:
        pass

    # Popup kapatma denemesi (maks 10 sn, bloklamaz)
    t_end = time.time() + 10
    closed = False
    while time.time() < t_end:
        try:
            driver.switch_to.default_content()
        except Exception:
            pass
        try:
            popup_kapat(driver)
            closed = True
            break
        except Exception:
            pass
        try:
            dismiss_any_alert(driver)
        except Exception:
            pass
        time.sleep(0.4)

    if closed:
        log_yaz("✅ Popup kapatıldı")
    else:
        log_yaz("ℹ️ Popup kapanmadı (10 sn doldu). İşlem büyük ihtimalle tamamlandı; devam ediliyor…")

    # defensif: IMEI alanını temizle
    try:
        driver.execute_script("""
            try{ var el=document.getElementById('RepairOrderAssignments_SerialNo'); if(el){el.value='';} }catch(e){}
        """)
    except Exception:
        pass
    log_yaz("✅ Teknisyen atama kaydedildi")
def goto_home_page(driver, wait, timeout=15):
    """Teknisyen Ata öncesi ana sayfaya dönüp sol menüyü garantiye alır.
    Önce UI'dan (logo / anasayfa linki) dener, olmazsa URL fallback.
    """
    try:
        driver.switch_to.default_content()
    except Exception:
        pass

    # UI denemeleri (logo/anasayfa)
    candidates = [
        "//a[contains(@href,'/Default') or contains(@href,'/default')]",
        "//a[contains(@href,'/Home') or contains(@href,'/home')]",
        "//a[contains(@href,'/') and (.//img or contains(@class,'logo') or contains(@id,'logo'))]"
    ]
    for xp in candidates:
        try:
            el = WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.XPATH, xp)))
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
            try:
                el.click()
            except Exception:
                driver.execute_script("arguments[0].click();", el)
            time.sleep(0.8)
            return
        except Exception:
            pass

    # Fallback: ana sayfa URL (taze param ile)
    base = "https://destekwega.com/"
    try:
        driver.get(base + ("?rnd=" + str(int(time.time()*1000))))
    except Exception:
        driver.get(base)
    time.sleep(1.2)

def ensure_driver():
    """Driver'ı hazırlar. Önceki süreçte pencere kapanmışsa otomatik yeniden oluşturur."""
    d = STATE.get("driver")
    w = STATE.get("wait")

    def _driver_ok(dd):
        try:
            _ = dd.window_handles  # NoSuchWindowException burada patlar
            return True
        except Exception:
            return False

    if d is None or w is None or (d is not None and not _driver_ok(d)):
        # eski driver bozuksa kapatmayı dene
        try:
            if d is not None:
                d.quit()
        except Exception:
            pass

        STATE["driver"], STATE["wait"] = None, None
        STATE["logged_in"] = False

        d2, w2 = driver_olustur()
        STATE["driver"], STATE["wait"] = d2, w2
        log_yaz("🧩 Driver hazır")

def ensure_logged_in():
    ensure_driver()
    if not STATE["logged_in"]:
        login(STATE["driver"], STATE["wait"])
        STATE["logged_in"] = True

def read_form_data():
    return {
        "imei": imei_entry.get().strip(),
        "teknisyen": teknisyen_combo.get(),
        "garanti": garanti_combo.get()
    }

def require_imei(veri):
    if not veri.get("imei"):
        raise Exception("IMEI boş olamaz")

def set_buttons_state(enabled: bool):
    state = "normal" if enabled else "disabled"
    btn_full.config(state=state)


def log_driver_debug_context(step_name, exc):
    """Hata anında sayfa / frame / URL bilgisini loglar."""
    try:
        d = STATE.get("driver")
        if d is None:
            log_yaz("ℹ️ Driver context yok")
            return

        try:
            log_yaz(f"🌐 URL: {d.current_url}")
        except Exception:
            pass

        try:
            title = d.title or ""
            if title:
                log_yaz(f"🪟 Başlık: {title}")
        except Exception:
            pass

        try:
            frame_count = len(d.find_elements(By.TAG_NAME, "iframe"))
            log_yaz(f"🧩 Sayfadaki iframe sayısı: {frame_count}")
        except Exception:
            pass

        try:
            html = d.page_source or ""
            if isinstance(exc, NoSuchElementException):
                hints = []
                for token in [
                    "RepairOrderAssignments_SerialNo",
                    "CollectiveStatusUpdate_SerialNo",
                    "SaveForm",
                    "Siparişi Değiştir",
                    "Teslimat",
                    "Tamir iadesi oluştur",
                    "OLUŞTUR",
                    "close_image",
                ]:
                    if token in html:
                        hints.append(token)
                if hints:
                    log_yaz("🔎 HTML içinde bulunan ilgili ipuçları: " + ", ".join(hints))
                else:
                    log_yaz("🔎 Beklenen ana element ipuçları HTML içinde bulunamadı")
        except Exception:
            pass

        if isinstance(exc, NoSuchElementException):
            log_yaz("💡 Olası neden: sayfa tam yüklenmedi, iframe değişti veya beklenen element id/xpath değişti.")
    except Exception:
        pass

def run_step(step_name, fn):
    """GUI donmasın diye step'i thread'de çalıştırır.
    Hata olursa detaylı log + ekran görüntüsü + html dump (mümkünse).
    Ayrıca toplam süreyi log'a yazar.
    """
    def _job():
        t0 = time.perf_counter()
        ok = False
        try:
            set_buttons_state(False)
            log_yaz(f"▶ {step_name} başladı")
            fn()
            ok = True
            log_yaz(f"✅ {step_name} bitti")
        except Exception as e:
            try:
                log_yaz(f"❌ {step_name} HATA: {repr(e)}")
                if isinstance(e, NoSuchElementException):
                    log_yaz("🚫 Element bulunamadı (NoSuchElementException)")
                try:
                    log_yaz(traceback.format_exc())
                except Exception:
                    pass
                try:
                    log_driver_debug_context(step_name, e)
                except Exception:
                    pass
            except Exception:
                pass

            # Selenium artefact
            try:
                d = STATE.get("driver")
                if d is not None:
                    import os
                    art_dir = get_artifacts_dir()
                    ss_dir = os.path.join(art_dir, "screenshots")
                    hd_dir = os.path.join(art_dir, "html_dumps")
                    os.makedirs(ss_dir, exist_ok=True)
                    os.makedirs(hd_dir, exist_ok=True)
                    ts = str(int(time.time() * 1000))
                    safe = step_name.replace(" ", "_")
                    sp = os.path.join(ss_dir, f"{safe}_{ts}.png")
                    hp = os.path.join(hd_dir, f"{safe}_{ts}.html")
                    try:
                        d.save_screenshot(sp)
                        log_yaz(f"🖼 Screenshot: {sp}")
                    except Exception:
                        pass
                    try:
                        with open(hp, "w", encoding="utf-8") as f:
                            f.write(d.page_source)
                        log_yaz(f"📄 HTML dump: {hp}")
                    except Exception:
                        pass
            except Exception:
                pass

            try:
                messagebox.showerror("Hata", f"{step_name}\n\n{repr(e)}\n\nDetay logu sol işlem ekranına yazıldı.")
            except Exception:
                pass
        finally:
            dt = time.perf_counter() - t0
            try:
                log_yaz(f"⏱ {step_name} toplam süre: {format_duration(dt)}")
            except Exception:
                pass

            # ✅ Yeni süreç başlatmayı kolaylaştır: işlem bittiğinde IMEI alanını temizle ve odakla
            if ok:
                try:
                    root.after(0, lambda: (imei_entry.delete(0, tk.END), imei_entry.focus_set()))
                except Exception:
                    pass

            # Driver pencere kapanmışsa sonraki işlem için STATE temizle

            try:

                d = STATE.get('driver')

                if d is not None:

                    _ = d.window_handles

            except Exception:

                STATE['driver'], STATE['wait'] = None, None

                STATE['logged_in'] = False


            set_buttons_state(True)

    threading.Thread(target=_job, daemon=True).start()

# =========================
# ANA AKIŞ (FULL)
# =========================
def ana_akis_full(veri=None):
    """Tüm süreci tek bir worker thread içinde çalıştırır.
    Kritik: Teknisyen atama ekranına geçiş, URL ile değil MENÜ tıklaması ile yapılır:
    Servis işlemleri -> Tamir siparişi yönetimi

    Ek: Adım sürelerini ve toplam süreyi log'lar.
    """
    t0_all = time.perf_counter()

    veri = veri or read_form_data()
    require_imei(veri)
    if not veri.get("teknisyen"):
        raise Exception("Teknisyen seçilmedi")

    ensure_logged_in()

    timed_call("Kayıt Bul", kayit_bul, STATE["driver"], STATE["wait"], veri["imei"])
    timed_call("Kayıt Kaydet", kayit_kaydet, STATE["driver"], STATE["wait"], veri["imei"], veri["garanti"])
    timed_call("Departmana Yolla", departmana_yolla, STATE["driver"], STATE["wait"], veri["imei"])
    timed_call("Departman Kabul", departman_kabul, STATE["driver"], STATE["wait"], veri["imei"])

    try:
        STATE["driver"].switch_to.default_content()
    except Exception:
        pass
    dismiss_any_alert(STATE["driver"])

    # KRİTİK: Teknisyen Ata öncesi ana sayfaya dön (menü tıklaması için)
    timed_call("Ana Sayfaya Dön", goto_home_page, STATE["driver"], STATE["wait"])

    timed_call("Teknisyen Ata", teknisyen_ata_stabil, STATE["driver"], STATE["wait"], veri["imei"], veri["teknisyen"])

    # ✅ Günlük rapor için log kaydı
    try_append_daily_wega_log(veri["imei"], veri["teknisyen"], siparis_id_global or "", "Tamamlandı")

    dt_all = time.perf_counter() - t0_all
    log_yaz("🎉 TÜM SÜREÇ BAŞARIYLA TAMAMLANDI")
    log_yaz(f"⏱ TÜM SÜREÇ TOPLAM: {format_duration(dt_all)}")

# =========================
# BUTON HANDLER'LARI
# =========================

def btn_full_click():
    veri = read_form_data()
    run_step("Tüm Süreç", lambda: ana_akis_full(veri))


def btn_update_click():
    # UI donmasın diye ayrı thread'de kontrol et
    def _job():
        try:
            check_update_manual(root)
        except Exception:
            pass
    threading.Thread(target=_job, daemon=True).start()



# =========================
# HIZLI INPUT / GÜNLÜK RAPOR HELPERS
# =========================
WEGA_ACTIVITY_LOG = "wega_activity_log.csv"

def fast_set_value_js(driver, element, value: str):
    """Input'a değeri JS ile çok hızlı yazar (send_keys gecikmesini bypass eder)."""
    driver.execute_script(
        """
        var el = arguments[0];
        var val = arguments[1];
        try{
            el.focus();
            el.value = val;
            el.dispatchEvent(new Event('input',{bubbles:true}));
            el.dispatchEvent(new Event('change',{bubbles:true}));
        }catch(e){}
        """,
        element,
        str(value),
    )

def stop_loading(driver):
    """Sayfanın kalan yüklemelerini durdurur (input hazırsa hız kazandırır)."""
    try:
        driver.execute_script("window.stop();")
    except Exception:
        pass

def open_status_page_and_wait_input(driver, status_code: str, input_id: str, timeout: int = 20):
    """CollectiveStatusUpdate sayfasını açar, input gelir gelmez yüklemeyi durdurur."""
    driver.get(f"https://destekwega.com/CustomerService/CollectiveStatusUpdate.aspx?Status={status_code}")
    el = find_element_any_frame(driver, By.ID, input_id, timeout=timeout, max_depth=6)
    stop_loading(driver)
    return el

def _log_file_path():
    try:
        return os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), WEGA_ACTIVITY_LOG)
    except Exception:
        return WEGA_ACTIVITY_LOG

def read_today_wega_logs():
    rows = []
    path = _log_file_path()
    if not os.path.exists(path):
        return rows
    try:
        today = time.strftime("%Y-%m-%d")
        import csv
        with open(path, "r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if str(row.get("tarih", "")).strip() == today:
                    rows.append(row)
    except Exception:
        return []
    return rows

def aggregate_logs_by_technician(rows):
    counts = {}
    for row in rows:
        tech = str(row.get("teknisyen", "")).strip() or "Bilinmiyor"
        counts[tech] = counts.get(tech, 0) + 1
    return sorted(counts.items(), key=lambda x: (-x[1], x[0]))

def refresh_daily_report():
    global REFRESH_AKTIF

    if not REFRESH_AKTIF:
        root.after(5000, refresh_daily_report)
        return
    """Sağ panelde günlük raporu yeniler."""
    try:
        rows = read_today_wega_logs()
        summary = aggregate_logs_by_technician(rows)

        total_var.set(str(len(rows)))
        tech_count_var.set(str(len(summary)))
        top_tech_var.set(f"{summary[0][0]} ({summary[0][1]})" if summary else "-")

        try:
            for item in summary_tree.get_children():
                summary_tree.delete(item)
            for tech, count in summary:
                summary_tree.insert("", "end", values=(tech, count))
        except Exception:
            pass

        try:
            for item in detail_tree.get_children():
                detail_tree.delete(item)
            for row in rows:
                detail_tree.insert(
                    "",
                    "end",
                    values=(
                        row.get("saat", ""),
                        row.get("teknisyen", ""),
                        row.get("imei", ""),
                        row.get("siparis_id", ""),
                        row.get("durum", ""),
                    ),
                )
        except Exception:
            pass

        info_count_var.set(f"Bugün {len(rows)} kayıt listelendi" if rows else "Bugün için kayıt bulunamadı")
    except Exception:
        pass
    finally:
        try:
            root.after(5000, refresh_daily_report)
        except Exception:
            pass


# =========================
# HIZLI INPUT / GÜNLÜK RAPOR HELPERS
# =========================
WEGA_ACTIVITY_LOG = "wega_activity_log.csv"

def fast_set_value_js(driver, element, value: str):
    driver.execute_script(
        """
        var el = arguments[0];
        var val = arguments[1];
        try{
            el.focus();
            el.value = val;
            el.dispatchEvent(new Event('input',{bubbles:true}));
            el.dispatchEvent(new Event('change',{bubbles:true}));
        }catch(e){}
        """,
        element,
        str(value),
    )

def stop_loading(driver):
    try:
        driver.execute_script("window.stop();")
    except Exception:
        pass

def open_status_page_and_wait_input(driver, status_code: str, input_id: str, timeout: int = 20):
    driver.get(f"https://destekwega.com/CustomerService/CollectiveStatusUpdate.aspx?Status={status_code}")
    el = find_element_any_frame(driver, By.ID, input_id, timeout=timeout, max_depth=6)
    stop_loading(driver)
    return el

def _log_file_path():
    try:
        return os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), WEGA_ACTIVITY_LOG)
    except Exception:
        return WEGA_ACTIVITY_LOG

def read_today_wega_logs():
    rows = []
    path = _log_file_path()
    if not os.path.exists(path):
        return rows
    try:
        import csv
        today = time.strftime("%Y-%m-%d")
        with open(path, "r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if str(row.get("tarih", "")).strip() == today:
                    rows.append(row)
    except Exception:
        return []
    return rows

def aggregate_logs_by_technician(rows):
    counts = {}
    for row in rows:
        tech = str(row.get("teknisyen", "")).strip() or "Bilinmiyor"
        counts[tech] = counts.get(tech, 0) + 1
    return sorted(counts.items(), key=lambda x: (-x[1], x[0]))

def refresh_daily_report():
    try:
        rows = read_today_wega_logs()
        summary = aggregate_logs_by_technician(rows)

        total_var.set(str(len(rows)))
        tech_count_var.set(str(len(summary)))
        top_tech_var.set(f"{summary[0][0]} ({summary[0][1]})" if summary else "-")

        for item in summary_tree.get_children():
            summary_tree.delete(item)
        for tech, count in summary:
            summary_tree.insert("", "end", values=(tech, count))

        for item in detail_tree.get_children():
            detail_tree.delete(item)
        for row in rows:
            detail_tree.insert(
                "",
                "end",
                values=(
                    row.get("saat", ""),
                    row.get("teknisyen", ""),
                    row.get("imei", ""),
                    row.get("siparis_id", ""),
                    row.get("durum", ""),
                ),
            )

        info_count_var.set(f"Bugün {len(rows)} kayıt listelendi" if rows else "Bugün için kayıt bulunamadı")
    except Exception:
        pass
    finally:
        root.after(5000, refresh_daily_report)

def show_placeholder(name: str):
    try:
        status_var.set(f"{name} modülü bu dosyada henüz eklenmedi")
        messagebox.showinfo("Bilgi", f"{name} modülü için alan hazır. İstersen bunu da aynı tek ekran yapısına ekleyebilirim.")
    except Exception:
        pass


# =========================
# UI HELPERS
# =========================
def clear_log_area():
    try:
        log.delete("1.0", tk.END)
        log_yaz("🧹 Log temizlendi")
    except Exception:
        pass

def copy_tree_selection(tree):
    try:
        selected = tree.selection()
        if not selected:
            return
        lines = []
        for item in selected:
            vals = tree.item(item, "values")
            lines.append("\t".join(str(v) for v in vals))
        text = "\n".join(lines)
        root.clipboard_clear()
        root.clipboard_append(text)
    except Exception:
        pass

def bind_copyable_tree(tree):
    def _copy(_event=None):
        copy_tree_selection(tree)
        return "break"
    tree.bind("<Control-c>", _copy)
    tree.bind("<Control-C>", _copy)

    menu = tk.Menu(tree, tearoff=0)
    menu.add_command(label="Kopyala", command=lambda: copy_tree_selection(tree))

    def _popup(event):
        try:
            row = tree.identify_row(event.y)
            if row:
                tree.selection_set(row)
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            try:
                menu.grab_release()
            except Exception:
                pass

    tree.bind("<Button-3>", _popup)
    return tree

def make_copyable_entry(widget):
    try:
        widget.bind("<Control-a>", lambda e: (widget.select_range(0, tk.END), "break"))
        widget.bind("<Control-A>", lambda e: (widget.select_range(0, tk.END), "break"))
    except Exception:
        pass
    return widget



# =========================
# SECURE CLEAR HELPERS
# =========================

def enable_refresh():
    global REFRESH_AKTIF
    REFRESH_AKTIF = True

def ask_clear_password():
    try:
        pwd = simpledialog.askstring("Şifre Gerekli", "Logları temizlemek için şifre girin:", parent=root, show="*")
    except Exception:
        pwd = None

    if pwd is None:
        return False

    if str(pwd).strip() != str(ADMIN_CLEAR_PASSWORD):
        try:
            messagebox.showerror("Hatalı Şifre", "Girilen şifre yanlış.")
        except Exception:
            pass
        return False
    return True

def clear_left_log_only():
    """Sadece sol taraftaki işlem logunu temizler."""
    if not ask_clear_password():
        return
    try:
        log.delete("1.0", tk.END)
    except Exception:
        pass
    try:
        log_yaz("🧹 Sol işlem logu temizlendi")
    except Exception:
        pass

def clear_right_report_only():
    """Sadece sağ taraftaki rapor / tablo / sayaç alanlarını temizler."""
    global REFRESH_AKTIF

    if not ask_clear_password():
        return

    REFRESH_AKTIF = False

    try:
        log_path = _log_file_path()
        if os.path.exists(log_path):
            with open(log_path, "w", encoding="utf-8-sig", newline="") as f:
                f.write("tarih,saat,imei,teknisyen,siparis_id,durum\n")
    except Exception as e:
        try:
            messagebox.showerror("Temizleme Hatası", f"CSV temizlenemedi:\n{e}")
        except Exception:
            pass

    try:
        for item in summary_tree.get_children():
            summary_tree.delete(item)
    except Exception:
        pass

    try:
        for item in detail_tree.get_children():
            detail_tree.delete(item)
    except Exception:
        pass

    try:
        total_var.set("0")
        tech_count_var.set("0")
        top_tech_var.set("-")
        info_count_var.set("Sağ rapor alanı temizlendi")
    except Exception:
        pass

    try:
        root.after(5000, enable_refresh)
    except Exception:
        pass



def open_son_test_link():
    """Son Test Takip için Google Sheet bağlantısını doğrudan açar."""
    try:
        webbrowser.open(SON_TEST_URL)
        try:
            status_var.set("Son Test Takip bağlantısı tarayıcıda açıldı")
        except Exception:
            pass
    except Exception as e:
        try:
            messagebox.showerror("Link Açma Hatası", str(e))
        except Exception:
            pass


# =========================
# GUI
# =========================
ensure_workdir()
root = tk.Tk()
show_browser_var = tk.BooleanVar(value=False)
root.after(300, lambda: check_update_on_startup(root))
root.title("Kontrol ve Takip Otomasyonu | Tek Ekran Entegre Wega")
try:
    root.state("zoomed")
except Exception:
    root.geometry("1600x900")
root.configure(bg="#EEF3F8")

style = ttk.Style()
try:
    if "vista" in style.theme_names():
        style.theme_use("vista")
except Exception:
    pass

# Dashboard vars
total_var = tk.StringVar(value="0")
tech_count_var = tk.StringVar(value="0")
top_tech_var = tk.StringVar(value="-")
info_count_var = tk.StringVar(value="Hazır")
time_var = tk.StringVar(value="")
status_var = tk.StringVar(value="Sistem hazır")

def update_clock():
    try:
        time_var.set(time.strftime("%d.%m.%Y  %H:%M:%S"))
    except Exception:
        pass
    root.after(1000, update_clock)

# Outer wrapper
wrapper = tk.Frame(root, bg="#EEF3F8")
wrapper.pack(fill="both", expand=True)

# Sidebar
sidebar = tk.Frame(wrapper, bg="#173A78", width=285)
sidebar.pack(side="left", fill="y")
sidebar.pack_propagate(False)

sb_top = tk.Frame(sidebar, bg="#102B5A", height=94)
sb_top.pack(fill="x")
sb_top.pack_propagate(False)

tk.Label(sb_top, text="Şirket Paneli", font=("Segoe UI", 15, "bold"), fg="white", bg="#102B5A").pack(anchor="w", padx=16, pady=(18, 0))
tk.Label(sb_top, text="Tek ekranda merkezi yönetim", font=("Segoe UI", 10), fg="#C9DAFF", bg="#102B5A").pack(anchor="w", padx=16)

tk.Label(sidebar, text="MODÜLLER", font=("Segoe UI", 10, "bold"), fg="#AFC8F8", bg="#173A78").pack(anchor="w", padx=16, pady=(16, 10))

def sidebar_btn(parent, text, sub, command, active=False):
    bg = "#214A95" if active else "#173A78"
    f = tk.Frame(parent, bg=bg, highlightthickness=1, highlightbackground="#2B5AA9", cursor="hand2")
    f.pack(fill="x", pady=6)
    t1 = tk.Label(f, text=text, font=("Segoe UI", 13, "bold"), fg="white", bg=bg, anchor="w", cursor="hand2")
    t1.pack(fill="x", padx=14, pady=(10, 0))
    t2 = tk.Label(f, text=sub, font=("Segoe UI", 9), fg="#D5E5FF", bg=bg, anchor="w", justify="left", wraplength=220, cursor="hand2")
    t2.pack(fill="x", padx=14, pady=(2, 10))
    for w in (f, t1, t2):
        w.bind("<Button-1>", lambda e: command())
    return f

menu_wrap = tk.Frame(sidebar, bg="#173A78")
menu_wrap.pack(fill="x", padx=12)

sidebar_btn(menu_wrap, "🗂  Wega Kaydı", "Entegre kayıt formu ve günlük rapor", lambda: status_var.set("Wega ekranı aktif"), active=True)
sidebar_btn(menu_wrap, "🧪  Son Test Takip", "Google Sheet bağlantısını doğrudan açar", open_son_test_link)
sidebar_btn(menu_wrap, "📋  NDF Takip", "NDF rapor ekranını ayrı pencerede açar", lambda: open_ndf_window(root))

tk.Label(sidebar, textvariable=status_var, font=("Segoe UI", 9, "bold"), fg="#1E4D1A", bg="#D8F5D1", padx=10, pady=7).pack(side="bottom", fill="x", padx=14, pady=16)

# Main host
host = tk.Frame(wrapper, bg="#EEF3F8")
host.pack(side="left", fill="both", expand=True)

# Header
top = tk.Frame(host, bg="#FFFFFF", height=95, highlightthickness=1, highlightbackground="#D8E2F0")
top.pack(fill="x", padx=18, pady=18)
top.pack_propagate(False)

top_left = tk.Frame(top, bg="#FFFFFF")
top_left.pack(side="left", fill="both", expand=True, padx=18, pady=14)

tk.Label(top_left, text="Wega Kayıt ve Günlük Rapor", font=("Segoe UI", 24, "bold"), fg="#1E3F7A", bg="#FFFFFF").pack(anchor="w")
tk.Label(top_left, text="Teknisyen aynı ekranda kayıt açar ve günlük raporu takip eder.", font=("Segoe UI", 11), fg="#6A7D9C", bg="#FFFFFF").pack(anchor="w")

top_right = tk.Frame(top, bg="#FFFFFF")
top_right.pack(side="right", padx=18, pady=14)

tk.Label(top_right, textvariable=time_var, font=("Segoe UI", 12, "bold"), fg="#1E3F7A", bg="#FFFFFF").pack(anchor="e")
tk.Label(top_right, textvariable=info_count_var, font=("Segoe UI", 10), fg="#6A7D9C", bg="#FFFFFF").pack(anchor="e")

# Content area
body = tk.Frame(host, bg="#EEF3F8")
body.pack(fill="both", expand=True, padx=18, pady=(0, 18))

# LEFT WEGA FORM + LOG
left_panel = tk.Frame(body, bg="#173A78", width=370)
left_panel.pack(side="left", fill="y")
left_panel.pack_propagate(False)

left_top = tk.Frame(left_panel, bg="#102B5A", height=88)
left_top.pack(fill="x")
left_top.pack_propagate(False)

tk.Label(left_top, text="Kayıt Formu", font=("Segoe UI", 18, "bold"), fg="white", bg="#102B5A").pack(anchor="w", padx=18, pady=(14, 0))
tk.Label(left_top, text="Formu doldur ve süreci başlat", font=("Segoe UI", 10), fg="#C9DAFF", bg="#102B5A").pack(anchor="w", padx=18)

form_wrap = tk.Frame(left_panel, bg="#173A78")
form_wrap.pack(fill="both", expand=True, padx=18, pady=18)

form_card = tk.Frame(form_wrap, bg="#F7FAFF", highlightthickness=1, highlightbackground="#D8E2F0", bd=0)
form_card.pack(fill="x")

form_head = tk.Frame(form_card, bg="#EAF1FB")
form_head.pack(fill="x")
tk.Label(
    form_head,
    text="Cihaz Bilgileri",
    font=("Segoe UI", 12, "bold"),
    fg="#1E3F7A",
    bg="#EAF1FB",
    padx=12,
    pady=10,
).pack(anchor="w")

form = tk.Frame(form_card, bg="#F7FAFF")
form.pack(fill="x", padx=14, pady=12)
form.grid_columnconfigure(1, weight=1)

tk.Label(form, text="IMEI", font=("Segoe UI", 11, "bold"), fg="#173A78", bg="#F7FAFF").grid(row=0, column=0, padx=(0,10), pady=8, sticky="w")
imei_entry = tk.Entry(form, width=30, font=("Segoe UI", 12), relief="solid", bd=1)
imei_entry.grid(row=0, column=1, padx=0, pady=8, sticky="ew")
make_copyable_entry(imei_entry)

tk.Label(form, text="Teknisyen", font=("Segoe UI", 11, "bold"), fg="#173A78", bg="#F7FAFF").grid(row=1, column=0, padx=(0,10), pady=8, sticky="w")
teknisyen_combo = ttk.Combobox(
    form,
    values=[
        "T0000012","T0000045","T0000197","T0000269",
        "T0000296","T0000338","T0000366","T0000379","T0000489"
    ],
    state="readonly",
    width=27
)
teknisyen_combo.current(0)
teknisyen_combo.grid(row=1, column=1, padx=0, pady=8, sticky="ew")

tk.Label(form, text="Garanti", font=("Segoe UI", 11, "bold"), fg="#173A78", bg="#F7FAFF").grid(row=2, column=0, padx=(0,10), pady=8, sticky="w")
garanti_combo = ttk.Combobox(
    form,
    values=["Garanti İçi", "Garanti Dışı"],
    state="readonly",
    width=27
)
garanti_combo.current(0)
garanti_combo.grid(row=2, column=1, padx=0, pady=8, sticky="ew")

btn_bar = tk.Frame(form_wrap, bg="#173A78")
btn_bar.pack(fill="x", pady=(12, 8))

btn_full = tk.Button(
    btn_bar,
    text="▶ Süreci Başlat",
    command=btn_full_click,
    font=("Segoe UI", 12, "bold"),
    fg="white",
    bg="#ED7D31",
    activebackground="#F2954D",
    activeforeground="white",
    bd=0,
    padx=14,
    pady=10,
    cursor="hand2",
)
btn_full.pack(fill="x")

btn_row2 = tk.Frame(form_wrap, bg="#173A78")
btn_row2.pack(fill="x", pady=(4, 8))

btn_update = tk.Button(
    btn_row2,
    text="🔄 Güncelleme Kontrol",
    command=btn_update_click,
    font=("Segoe UI", 10, "bold"),
    fg="#173A78",
    bg="#DCE7F8",
    activebackground="#C9DBF7",
    bd=0,
    padx=10,
    pady=8,
    cursor="hand2",
)
btn_update.pack(side="left", fill="x", expand=True)

btn_tech = tk.Button(
    btn_row2,
    text="👨‍🔧 Teknisyen Ata",
    command=teknisyen_ata_onayli_clicked,
    font=("Segoe UI", 10, "bold"),
    fg="#173A78",
    bg="#DCE7F8",
    activebackground="#C9DBF7",
    bd=0,
    padx=10,
    pady=8,
    cursor="hand2",
)
btn_tech.pack(side="left", fill="x", expand=True, padx=(8, 0))

extra_row = tk.Frame(form_wrap, bg="#173A78")
extra_row.pack(fill="x", pady=(2, 10))

chk_show = ttk.Checkbutton(extra_row, text="🖥 Tarayıcıyı göster (debug)", variable=show_browser_var)
chk_show.pack(side="left")

right_actions = tk.Frame(extra_row, bg="#173A78")
right_actions.pack(side="right")

clear_left_btn = tk.Button(
    right_actions,
    text="🧹 Sol Log",
    command=clear_left_log_only,
    font=("Segoe UI", 7, "bold"),
    fg="#173A78",
    bg="#DCE7F8",
    activebackground="#C9DBF7",
    bd=0,
    padx=7,
    pady=6,
    cursor="hand2",
)
clear_left_btn.pack(side="left")

clear_right_btn = tk.Button(
    right_actions,
    text="🧹 Sağ Rapor",
    command=clear_right_report_only,
    font=("Segoe UI", 7, "bold"),
    fg="#173A78",
    bg="#DCE7F8",
    activebackground="#C9DBF7",
    bd=0,
    padx=7,
    pady=6,
    cursor="hand2",
)
clear_right_btn.pack(side="left", padx=(8, 0))

log_head = tk.Frame(form_wrap, bg="#173A78")
log_head.pack(fill="x", pady=(6, 6))
tk.Label(log_head, text="İşlem Logu", font=("Segoe UI", 11, "bold"), fg="white", bg="#173A78").pack(side="left")
tk.Label(log_head, text="Ctrl+C ile kopyalanabilir", font=("Segoe UI", 9), fg="#C9DAFF", bg="#173A78").pack(side="right")

log = tk.Text(form_wrap, height=21, bg="#0f172a", fg="#e5e7eb", insertbackground="white", undo=True)
log.pack(fill="both", expand=True)

# RIGHT DAILY REPORT
right_panel = tk.Frame(body, bg="#EEF3F8")
right_panel.pack(side="left", fill="both", expand=True, padx=(16, 0))

content = tk.Frame(right_panel, bg="#EEF3F8")
content.pack(fill="both", expand=True, pady=(16, 0))

summary_panel = tk.Frame(content, bg="#FFFFFF", highlightthickness=1, highlightbackground="#D8E2F0")
summary_panel.pack(side="left", fill="both", expand=True, padx=(0, 8))
tk.Label(summary_panel, text="Teknisyen Özeti", font=("Segoe UI", 16, "bold"), fg="#1E3F7A", bg="#FFFFFF").pack(anchor="w", padx=18, pady=(16, 10))

summary_tree = bind_copyable_tree(ttk.Treeview(summary_panel, columns=("teknisyen", "adet"), show="headings", height=16))
summary_tree.heading("teknisyen", text="Teknisyen")
summary_tree.heading("adet", text="Bugünkü Kayıt")
summary_tree.column("teknisyen", width=260, anchor="w")
summary_tree.column("adet", width=120, anchor="center")
summary_tree.pack(fill="both", expand=True, padx=18, pady=(0, 18))

detail_panel = tk.Frame(content, bg="#FFFFFF", highlightthickness=1, highlightbackground="#D8E2F0")
detail_panel.pack(side="left", fill="both", expand=True, padx=(8, 0))
tk.Label(detail_panel, text="Bugünkü İş Listesi", font=("Segoe UI", 16, "bold"), fg="#1E3F7A", bg="#FFFFFF").pack(anchor="w", padx=18, pady=(16, 10))

detail_tree = bind_copyable_tree(ttk.Treeview(detail_panel, columns=("saat", "teknisyen", "imei", "siparis_id", "durum"), show="headings", height=16))
for col, title, width, anchor in [
    ("saat", "Saat", 90, "center"),
    ("teknisyen", "Teknisyen", 170, "w"),
    ("imei", "IMEI", 160, "center"),
    ("siparis_id", "Sipariş ID", 140, "center"),
    ("durum", "Durum", 130, "w"),
]:
    detail_tree.heading(col, text=title)
    detail_tree.column(col, width=width, anchor=anchor)
detail_tree.pack(fill="both", expand=True, padx=18, pady=(0, 18))

# Kopyalama kısayolları
try:
    log.bind("<Control-a>", lambda e: (log.tag_add("sel", "1.0", "end-1c"), "break"))
    log.bind("<Control-A>", lambda e: (log.tag_add("sel", "1.0", "end-1c"), "break"))
except Exception:
    pass

log_yaz("🟢 Sistem hazır – tek ekranda entegre Wega paneli aktif")
update_clock()
refresh_daily_report()


root.mainloop()
