@echo off
setlocal
cd /d "%~dp0"

echo ==========================================
echo  ORBIT ^| TIENDA PERFECTA - Plataforma Web
echo ==========================================
echo.

REM Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no encontrado. Instala Python 3.10+
    pause
    exit /b 1
)

REM Verificar streamlit
python -c "import streamlit" >nul 2>&1
if errorlevel 1 (
    echo Instalando dependencias...
    pip install streamlit plotly --quiet
)

REM Abrir puerto 8501 en el Firewall de Windows (permite acceso desde la red local)
netsh advfirewall firewall show rule name="Orbit Streamlit 8501" >nul 2>&1
if errorlevel 1 (
    echo Configurando acceso de red ^(Firewall^)...
    netsh advfirewall firewall add rule name="Orbit Streamlit 8501" dir=in action=allow protocol=TCP localport=8501 >nul 2>&1
    echo    OK - Puerto 8501 habilitado en Firewall.
) else (
    echo    Firewall: puerto 8501 ya configurado.
)

REM Obtener IP local
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /i "IPv4" ^| findstr /v "127.0.0.1"') do (
    set LOCAL_IP=%%a
    goto :found_ip
)
:found_ip
set LOCAL_IP=%LOCAL_IP: =%

echo.
echo  Accede desde cualquier dispositivo en la misma red WiFi:
echo.
echo    Este equipo:   http://localhost:8501
echo    Red local:     http://%LOCAL_IP%:8501
echo.
echo  Compartí ese link con tu celular o tablet conectados a la misma red.
echo  Presiona Ctrl+C para detener la plataforma.
echo.

streamlit run app_orbit_tp.py --server.port 8501 --server.address 0.0.0.0 --server.headless true --browser.gatherUsageStats false --theme.base dark --theme.primaryColor "#6EC531" --theme.backgroundColor "#0A0A0A" --theme.secondaryBackgroundColor "#111111" --theme.textColor "#FFFFFF"

pause
