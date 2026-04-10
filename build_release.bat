@echo off
title WEGA BUILD SYSTEM
color 0A

echo ============================
echo VERSION GIRISI
echo ============================

python version_prompt.py

echo ============================
echo BUILD BASLIYOR...
echo ============================

rmdir /s /q build
rmdir /s /q dist
del *.spec

echo TeknisyenPortal build...
pyinstaller --onefile --noconsole TeknisyenPortal.py
if errorlevel 1 pause

echo WegaApp build...
pyinstaller --onefile --noconsole WegaApp.py
if errorlevel 1 pause

echo ============================
echo DOSYALAR KONTROL
echo ============================

if not exist dist\TeknisyenPortal.exe (
    echo HATA: TeknisyenPortal.exe olusmadi!
    pause
    exit
)

if not exist dist\WegaApp.exe (
    echo HATA: WegaApp.exe olusmadi!
    pause
    exit
)

echo ============================
echo ZIP OLUSTURULUYOR
echo ============================

rmdir /s /q release
mkdir release

copy dist\TeknisyenPortal.exe release\
copy dist\WegaApp.exe release\
copy app_version.txt release\

powershell Compress-Archive -Path release\* -DestinationPath wega_release.zip -Force

echo ============================
echo GITHUB RELEASE
echo ============================

for /f "tokens=2 delims=:," %%a in ('findstr version manifest.json') do set VERSION=%%a
set VERSION=%VERSION:"=%

set TAG=v%VERSION%

gh release create %TAG% dist\WegaApp.exe --title "Wega %VERSION%" --notes "Auto release"

echo ============================
echo TAMAMLANDI
echo ============================

pause
