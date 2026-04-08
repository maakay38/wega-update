import tkinter as tk
from tkinter import scrolledtext, messagebox
import subprocess
from datetime import datetime

REPO_URL = "https://github.com/maakay38/wega-update-new.git"

class GitUploaderApp:
def **init**(self, root):
self.root = root
self.root.title("Wega PRO Upload Panel")
self.root.geometry("750x520")

```
    tk.Label(root, text="Versiyon Notu:", font=("Arial", 10, "bold")).pack(pady=5)

    self.msg_entry = tk.Entry(root, width=90)
    self.msg_entry.pack(pady=5)

    tk.Button(root, text="🚀 Build + Release Upload",
              command=self.run_all,
              bg="#2ecc71", fg="white", height=2).pack(pady=10)

    self.log = scrolledtext.ScrolledText(root, height=22, bg="black", fg="lime")
    self.log.pack(fill="both", expand=True)

def log_yaz(self, text):
    self.log.insert(tk.END, text + "\n")
    self.log.see(tk.END)
    self.root.update()

def komut_calistir(self, komut):
    self.log_yaz(f"> {komut}")
    sonuc = subprocess.run(komut, shell=True, capture_output=True, text=True)

    if sonuc.stdout:
        self.log_yaz(sonuc.stdout)

    if sonuc.stderr:
        self.log_yaz("HATA: " + sonuc.stderr)

    return sonuc.returncode == 0

def run_all(self):
    mesaj = self.msg_entry.get()

    if not mesaj:
        messagebox.showwarning("Uyarı", "Versiyon notu gir!")
        return

    # EXE oluştur
    self.log_yaz("=== EXE OLUŞTURULUYOR ===")
    if not self.komut_calistir("pyinstaller --onefile --noconsole WegaApp.py"):
        return

    # Git işlemleri
    self.log_yaz("=== GIT PUSH (SADECE KOD) ===")
    self.komut_calistir("git remote set-url origin " + REPO_URL)
    self.komut_calistir("git add .")
    self.komut_calistir(f'git commit -m "{mesaj}"')
    self.komut_calistir("git push --set-upstream origin main")

    # Release oluştur
    self.log_yaz("=== GITHUB RELEASE ===")
    version = datetime.now().strftime("%Y%m%d_%H%M")

    komut = f'gh release create v{version} dist/WegaApp.exe --title "WegaApp v{version}" --notes "{mesaj}"'
    self.komut_calistir(komut)

    self.log_yaz("=== TAMAMLANDI ===")
    messagebox.showinfo("Bitti", "Release oluşturuldu!")
```

if **name** == "**main**":
root = tk.Tk()
app = GitUploaderApp(root)
root.mainloop()
