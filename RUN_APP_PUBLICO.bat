@echo off
setlocal
cd /d "%~dp0"
title ORBIT - Plataforma Publica (Internet)

echo ====================================================
echo   ORBIT ^| TIENDA PERFECTA - ACCESO PUBLICO
echo   La app estara disponible desde CUALQUIER lugar
echo ====================================================
echo.

REM Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no encontrado.
    pause
    exit /b 1
)

REM Instalar pyngrok si falta
python -c "import pyngrok" >nul 2>&1
if errorlevel 1 (
    echo Instalando pyngrok...
    pip install pyngrok --quiet
)

REM Lanzar
python start_public.py

pause
