@echo off
setlocal ENABLEDELAYEDEXPANSION
cd /d "%~dp0"

echo ==========================================
echo TP_PYP - ORBIT + APPSHEET + GOOGLE SYNC
echo ==========================================
echo.
echo Elegi la zona a procesar:
echo   LU = Lunes
echo   MA = Martes
echo   MI = Miercoles
echo   JU = Jueves
echo   VI = Viernes
echo   SA = Sabado
echo.
echo Si presionas ENTER sin escribir nada:
echo el sistema usara automaticamente la zona de manana.
echo.

set /p DIA=Zona a procesar: 

if not "%DIA%"=="" (
    set "DIA=%DIA: =%"
    set "DIA=%DIA:"=%"
    set "DIA=%DIA:'=%"
)

if /I "%DIA%"=="LU" goto okdia
if /I "%DIA%"=="MA" goto okdia
if /I "%DIA%"=="MI" goto okdia
if /I "%DIA%"=="JU" goto okdia
if /I "%DIA%"=="VI" goto okdia
if /I "%DIA%"=="SA" goto okdia
if "%DIA%"=="" goto okdia

echo.
echo ERROR: zona invalida. Usa solo LU, MA, MI, JU, VI o SA.
pause
exit /b 1

:okdia
echo.
echo ==========================================
echo [1] Limpiando ventas...
echo ==========================================
python clean_venta.py --in "inputs\ventas.csv" --out "inputs\venta_limpia.csv"
if errorlevel 1 (
    echo.
    echo ERROR en clean_venta.py
    pause
    exit /b 1
)

echo.
echo ==========================================
echo [2] Ejecutando TP ORBIT + APPSHEET...
echo ==========================================
if "%DIA%"=="" (
    python tp_pyp_run_fast_ORBIT_appsheet.py ^
      --ventas "inputs\venta_limpia.csv" ^
      --gescom "inputs\gescom.xlsx" ^
      --portafolio "inputs\Portafolio Infaltable - Argentina.pptx" ^
      --out "output\Control_TP_Portafolio_PyP.xlsx" ^
      --lista-precios "inputs\lista_precios.xlsx" ^
      --objetivos-tp "inputs\objetivo_vendedor_tp.xlsx" ^
      --export-pdfs ^
      --export-gerencial
) else (
    python tp_pyp_run_fast_ORBIT_appsheet.py ^
      --ventas "inputs\venta_limpia.csv" ^
      --gescom "inputs\gescom.xlsx" ^
      --portafolio "inputs\Portafolio Infaltable - Argentina.pptx" ^
      --out "output\Control_TP_Portafolio_PyP.xlsx" ^
      --lista-precios "inputs\lista_precios.xlsx" ^
      --objetivos-tp "inputs\objetivo_vendedor_tp.xlsx" ^
      --dia-manana "%DIA%" ^
      --export-pdfs ^
      --export-gerencial
)

if errorlevel 1 (
    echo.
    echo ERROR en tp_pyp_run_fast_ORBIT_appsheet.py
    pause
    exit /b 1
)

if not exist "google_sync_config.json" (
    echo.
    echo ==========================================
    echo [3] Google Sync omitido
    echo ==========================================
    echo No existe google_sync_config.json en esta carpeta.
    echo.
    pause
    exit /b 0
)

if not exist "sync_tp_appsheet_drive.py" (
    echo.
    echo ==========================================
    echo [3] Google Sync omitido
    echo ==========================================
    echo No existe sync_tp_appsheet_drive.py en esta carpeta.
    echo.
    pause
    exit /b 0
)

echo.
echo ==========================================
echo [3] Sincronizando Drive y Google Sheets...
echo ==========================================
python sync_tp_appsheet_drive.py --config "google_sync_config.json"
if errorlevel 1 (
    echo.
    echo ERROR en sync_tp_appsheet_drive.py
    pause
    exit /b 1
)

echo.
echo ==========================================
echo [4] Actualizando app en la nube...
echo ==========================================
python sync_excel_to_gsheets.py
if errorlevel 1 (
    echo.
    echo AVISO: No se pudo actualizar la app en la nube.
)

echo.
echo ==========================================
echo PROCESO FINALIZADO
echo ==========================================
echo.
echo Ya estan actualizados:
echo - output\PDF_VENDEDORES
echo - output\PDF_GERENCIAL
echo - Google Drive / Google Sheets
echo - App en la nube (Streamlit Cloud)
echo.
pause
exit /b 0
