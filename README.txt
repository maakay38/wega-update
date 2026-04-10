WEGA AUTO BUILD + RELEASE v2

YENILIKLER:
- GUI ile version girme
- TeknisyenPortal build kontrol
- Hata yakalama

KULLANIM:
1. GitHub CLI kur:
   winget install GitHub.cli
   gh auth login

2. Python:
   pip install pyinstaller

3. Aynı klasöre koy:
   - TeknisyenPortal.py
   - WegaApp.py

4. build_release.bat çalıştır

SİSTEM:
- Version popup gelir
- EXE build edilir
- ZIP oluşturulur
- GitHub release atılır
