@echo off
title WEGA FINAL SYSTEM
color 0A

echo =========================
echo VERSION ARTIR
echo =========================

for /f %%i in (version.txt) do set VERSION=%%i

for /f "tokens=1,2,3 delims=." %%a in ("%VERSION%") do (
 set MAJOR=%%a
 set MINOR=%%b
 set PATCH=%%c
)

set /a PATCH+=1
set NEW_VERSION=%MAJOR%.%MINOR%.%PATCH%
echo %NEW_VERSION% > version.txt

set TAG=v%NEW_VERSION%

echo =========================
echo BUILD TEMIZLE
echo =========================

rmdir /s /q build 2>nul
rmdir /s /q dist 2>nul
rmdir /s /q release 2>nul

mkdir release

echo =========================
echo EXE BUILD
echo =========================

pyinstaller --onefile --noconsole --icon=wega.ico TeknisyenPortal.py
pyinstaller --onefile --noconsole --icon=wega.ico WegaApp.py

echo =========================
echo DOSYALARI HAZIRLA
echo =========================

copy dist\WegaApp.exe release\WegaApp.exe
copy dist\TeknisyenPortal.exe release\TeknisyenPortal.exe

echo =========================
echo ZIP OLUSTUR
echo =========================

powershell Compress-Archive -Path release\* -DestinationPath wega_release.zip -Force

echo =========================
echo GIT PUSH
echo =========================

git add .
git commit -m "release %NEW_VERSION%"
git push origin main

echo =========================
echo RELEASE SIL + YENI YUKLE
echo =========================

gh release delete %TAG% -y 2>nul

gh release create %TAG% wega_release.zip release\WegaApp.exe ^
--title "Wega %NEW_VERSION%" ^
--notes "Version %NEW_VERSION%"

echo =========================
echo ESKI SURUMLERI SIL (SON 3)
echo =========================

powershell -Command ^
"$rels = gh release list --limit 100 | ForEach-Object { ($_ -split '\s+')[0] }; ^
$keep = $rels | Select-Object -First 3; ^
foreach ($r in $rels) { ^
 if ($keep -notcontains $r) { ^
   gh release delete $r -y ^
 } ^
}"

echo =========================
echo TAMAMLANDI
echo =========================

pause