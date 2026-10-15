@echo off
setlocal
title GOLD PORTFOLIO GUARD - BASLATICI
cd /d "%~dp0"
if errorlevel 1 (
  echo HATA: Uygulama klasoru acilamadi.
  pause
  exit /b 1
)
if not exist "server.js" (
  echo HATA: server.js bulunamadi. Program dosyalari eksik.
  pause
  exit /b 1
)
where node.exe >nul 2>&1
if errorlevel 1 (
  echo HATA: Node.js bulunamadi. Node.js kurulu olmali.
  echo https://nodejs.org/
  pause
  exit /b 1
)
echo.
echo GOLD PORTFOLIO GUARD - OCAK 2026
echo Veri ve model kontrol ediliyor...
node server.js --verify
if errorlevel 1 (
  echo.
  echo HATA: Kaynak dosya veya referans sonuc kontrolu basarisiz.
  echo Uygulama baslatilmadi. Bu pencerenin goruntusunu paylasin.
  pause
  exit /b 1
)
echo.
echo Dogrulama basarili. Uygulama aciliyor...
start "GOLD PORTFOLIO GUARD - SUNUCU" cmd /k "node server.js"
timeout /t 3 /nobreak >nul
start "" "http://127.0.0.1:8787"
exit /b 0
