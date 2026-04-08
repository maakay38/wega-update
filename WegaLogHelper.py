import os
import csv
import sys
from datetime import datetime


def app_dir() -> str:
    return os.path.dirname(os.path.abspath(sys.argv[0]))


def wega_log_path() -> str:
    return os.path.join(app_dir(), "wega_activity_log.csv")


def append_wega_log(imei: str, teknisyen: str, siparis_id: str = "", durum: str = "Tamamlandı"):
    path = wega_log_path()
    now = datetime.now()

    row = {
        "tarih": now.strftime("%Y-%m-%d"),
        "saat": now.strftime("%H:%M:%S"),
        "imei": str(imei or "").strip(),
        "teknisyen": str(teknisyen or "").strip(),
        "siparis_id": str(siparis_id or "").strip(),
        "durum": str(durum or "").strip(),
    }

    new_file = not os.path.exists(path)
    with open(path, "a", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["tarih", "saat", "imei", "teknisyen", "siparis_id", "durum"])
        if new_file:
            writer.writeheader()
        writer.writerow(row)
