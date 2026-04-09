@echo off
title WEGA BUILD SYSTEM
color 0A

echo ============================
echo WEGA BUILD BASLADI
echo ============================

REM HATA DURDURMA
setlocal enabledelayedexpansion

REM Python kontrol
echo [1] Python kontrol ediliyor...
python --version
IF %ERRORLEVEL% NEQ 0 (
    echo ❌ Python bulunamadi!
    pause
    exit
)

REM PyInstaller kontrol
echo [2] PyInstaller kontrol ediliyor...
pip show pyinstaller >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo PyInstaller yok, yukleniyor...
    pip install pyinstaller
)

REM ESKI BUILD TEMIZLE
echo [3] Eski build temizleniyor...
rmdir /s /q build 2>nul
rmdir /s /q dist 2>nul

REM DOSYA KONTROL
echo [4] Dosyalar kontrol ediliyor...

IF NOT EXIST "WegaApp.py" (
    IF NOT EXIST "WegaApp.py" (
        echo ❌ WegaApp bulunamadi!
        pause
        exit
    ) ELSE (
        set MAIN=WegaApp.py
    )
) ELSE (
    set MAIN=WegaApp.py
)

IF NOT EXIST "TesknisyenPortal.py" (
    IF NOT EXIST "TesknisyenPortal.py" (
        echo ❌ Launcher bulunamadi!
        pause
        exit
    ) ELSE (
        set LAUNCHER=TesknisyenPortal.py
    )
) ELSE (
    set LAUNCHER=TesknisyenPortal.py
)

echo Ana dosya: %MAIN%
echo Launcher: %LAUNCHER%

REM ICON VAR MI
set ICON=
IF EXIST "wega.ico" set ICON=--icon=wega.ico
IF EXIST "wega.ico" set ICON=--icon=wega.ico

REM BUILD APP
echo.
echo [5] WegaApp build ediliyor...
pyinstaller --onefile --noconsole %ICON% --name WegaApp %MAIN%
IF %ERRORLEVEL% NEQ 0 (
    echo ❌ WegaApp build HATA!
    pause
    exit
)

REM BUILD LAUNCHER
echo.
echo [6] Launcher build ediliyor...
pyinstaller --onefile --noconsole %ICON% --name TesknisyenPortal %LAUNCHER%
IF %ERRORLEVEL% NEQ 0 (
    echo ❌ Launcher build HATA!
    pause
    exit
)

REM DOSYA KOPYALA
echo.
echo [7] Ek dosyalar kopyalaniyor...
copy app_version*.txt dist\ >nul 2>&1
copy wega_activity_log*.csv dist\ >nul 2>&1

echo.
echo ============================
echo BUILD TAMAMLANDI
echo ============================
echo dist klasorune bak!

pause