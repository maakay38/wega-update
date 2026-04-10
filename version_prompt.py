import json
import tkinter as tk
from tkinter import simpledialog

root = tk.Tk()
root.withdraw()

version = simpledialog.askstring("Versiyon Güncelle", "Yeni versiyon gir (örn: 1.0.2)")

if not version:
    exit()

with open("manifest.json", "r") as f:
    data = json.load(f)

data["version"] = version

with open("manifest.json", "w") as f:
    json.dump(data, f, indent=2)

with open("version.txt", "w") as f:
    f.write(version)

with open("app_version.txt", "w") as f:
    f.write(version)

print("Versiyon guncellendi:", version)
