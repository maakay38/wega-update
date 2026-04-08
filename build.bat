@echo off
setlocal
cd /d "%~dp0"

echo ========================================
echo WEGA CLEAN + BUILD SCRIPT
echo Working dir: %CD%
echo ========================================

echo ---- Python kontrol ----
where python
python -c "import sys,struct; print('Python:', sys.executable); print('Python bit:', struct.calcsize('P')*8)"
IF ERRORLEVEL 1 (
    echo HATA: Python calismiyor!
    pause
    exit /b
)

REM ---- Dosya kontrolleri ----
IF NOT EXIST "WegaLauncher.py" (
    echo HATA: WegaLauncher.py bulunamadi
    pause
    exit /b
)
IF NOT EXIST "WegaApp.py" (
    echo HATA: WegaApp.py bulunamadi
    pause
    exit /b
)

set "ICON_ARG="
IF EXIST "wega.ico" (
    set "ICON_ARG=--icon=wega.ico"
) else (
    echo UYARI: wega.ico yok, ikon olmadan build edilecek.
)

echo.
echo ---- TEMIZLIK ----
rmdir /s /q build 2>nul
rmdir /s /q dist 2>nul
rmdir /s /q WegaKayit 2>nul
del /q *.spec 2>nul

echo.
echo ---- LAUNCHER BUILD ----
python -m PyInstaller --onefile --noconsole --clean %ICON_ARG% WegaLauncher.py
IF ERRORLEVEL 1 (
    echo Launcher build HATA!
    pause
    exit /b
)

echo.
echo ---- APP BUILD ----
python -m PyInstaller --onefile --noconsole --clean WegaApp.py
IF ERRORLEVEL 1 (
    echo App build HATA!
    pause
    exit /b
)

echo.
echo ---- WegaKayit PAKETI ----
mkdir WegaKayit
copy /y "dist\WegaLauncher.exe" "WegaKayit\WegaLauncher.exe" >nul
copy /y "dist\WegaApp.exe" "WegaKayit\WegaApp.exe" >nul

REM Launcher'in sürüm takibi için dosya
IF NOT EXIST "app_version.txt" (
    echo 0.0.0> app_version.txt
)
copy /y "app_version.txt" "WegaKayit\app_version.txt" >nul

echo.
echo ========================================
echo BUILD TAMAMLANDI
echo Paket: %CD%\WegaKayit
echo ========================================
pause
