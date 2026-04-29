@echo off
setlocal
cd /d "%~dp0"

echo ==========================================
echo INSTALANDO DEPENDENCIAS GOOGLE SYNC TP_PYP
echo ==========================================
echo.

where python >nul 2>nul
if errorlevel 1 (
    echo ERROR: Python no esta disponible en PATH.
    pause
    exit /b 1
)

python -m pip install --upgrade pip
if errorlevel 1 (
    echo ERROR actualizando pip.
    pause
    exit /b 1
)

python -m pip install -r requirements_google_sync.txt
if errorlevel 1 (
    echo ERROR instalando requirements_google_sync.txt
    pause
    exit /b 1
)

echo.
echo ==========================================
echo DEPENDENCIAS INSTALADAS
echo ==========================================
echo.
pause
exit /b 0
