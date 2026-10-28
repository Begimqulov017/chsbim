@echo off
chcp 65001 >nul
echo CHSB_PRO test platformasi ishga tushirilmoqda...
where python >nul 2>nul
if %errorlevel%==0 (
    start "" http://localhost:8000
    python server.py
    goto :eof
)
where py >nul 2>nul
if %errorlevel%==0 (
    start "" http://localhost:8000
    py server.py
    goto :eof
)
echo Python topilmadi — index.html to'g'ridan-to'g'ri brauzerda ochilmoqda...
start "" index.html
