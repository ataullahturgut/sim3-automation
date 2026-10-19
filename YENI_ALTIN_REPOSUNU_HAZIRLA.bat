@echo off
setlocal
title GOLD - YENI REPO HAZIRLIGI
cd /d "%~dp0"
echo Altin modeli icin yeni temiz klasor olusturuluyor...
echo Eski sim3-automation dosyalari silinmeyecek.
echo.
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0GOLD_REPO_MIGRATION_PREPARE_20261019.ps1"
if errorlevel 1 (
  echo.
  echo HATA: Tasima hazirligi tamamlanamadi veya testler basarisiz.
  echo Yeni repo'yu henuz yayinlamayin. Hata ekranini paylasin.
) else (
  echo.
  echo HAZIR: GitHub Desktop ile yeni klasoru repository olarak olusturup PRIVATE publish yapabilirsiniz.
)
echo.
pause
