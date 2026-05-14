# 05 — Runbook Operativo Diario

## Rutina diaria estándar

El operador corre el pipeline una vez por día, antes de que los vendedores salgan a la calle (idealmente entre 06:00 y 08:00).

---

## Paso a paso normal

### 1. Actualizar el archivo de ventas

Exportar las ventas del día anterior desde GESCOM (u otro sistema):

- Guardar como `inputs/ventas.csv`
- Formato: UTF-8, separador coma
- Si el sistema exporta en otro formato, revisar `clean_venta.py` para ver las transformaciones que aplica

### 2. Ejecutar el BAT

Doble clic en `RUN_TP_FAST_ORBIT_APPSHEET_SYNC.bat`

El sistema pregunta:
```
Zona a procesar: _
```

Ingresar el código de la zona correspondiente al día siguiente:

| Día siguiente | Código |
|---|---|
| Lunes | LU |
| Martes | MA |
| Miércoles | MI |
| Jueves | JU |
| Viernes | VI |
| Sábado | SA |

Si se presiona ENTER sin escribir nada, usa automáticamente la zona de mañana.

### 3. Esperar que complete

El BAT ejecuta 4 pasos:

```
[1] Limpiando ventas...          → clean_venta.py
[2] Ejecutando TP ORBIT...       → pipeline principal (30–90 segundos)
[3] Sincronizando Drive/Sheets...→ sync_tp_appsheet_drive.py
[4] Actualizando app en la nube  → sync_excel_to_gsheets.py
```

Al final aparece:
```
PROCESO FINALIZADO

Ya están actualizados:
- output\PDF_VENDEDORES
- output\PDF_GERENCIAL
- Google Drive / Google Sheets
- App en la nube
```

### 4. Verificación rápida

Abrir el portal en el browser y verificar que los datos son del día correcto:

- Gerencia: ver la fecha en el bloque de objetivos
- Vendedor 2 (o cualquiera): ver fecha en encabezado

---

## Flujo del BAT en detalle

```
ventas.csv
    ↓ clean_venta.py
venta_limpia.csv
    ↓ tp_pyp_run_fast_ORBIT_appsheet.py
    ├─→ output/PDF_VENDEDORES/[fecha]/Vendedor_2_JU.pdf  (uno por vendedor)
    ├─→ output/PDF_GERENCIAL/[fecha]/Gerencial_JU.pdf
    ├─→ output/APPSHEET/pdf_index.csv
    ├─→ output/APPSHEET/clientes_oportunidad.csv
    ├─→ output/APPSHEET/foco_productos.csv
    ├─→ output/APPSHEET/tp_objetivos_resumen.csv
    └─→ output/Control_TP_Portafolio_PyP.xlsx (backup local)
    ↓ sync_tp_appsheet_drive.py
    ├─→ Google Sheets ← CSVs actualizados
    └─→ Google Drive  ← PDFs subidos
    ↓ sync_excel_to_gsheets.py
    └─→ Streamlit Cloud actualizado
```

---

## Situaciones especiales

### No hay ventas del día anterior

El pipeline puede correr igual con el último archivo `ventas.csv` disponible. Los datos de ventas son acumulados; lo que cambia es la fecha del informe.

### Vendedor con zona distinta al calendario

Ingresar manualmente el código de zona cuando el BAT pregunta.

### Se corrió con zona incorrecta

Correr el BAT de nuevo con la zona correcta. El pipeline sobreescribe los outputs y el sync actualiza Google Sheets y Drive.

### Google Sync falló (paso 3)

El pipeline local termina OK (PDFs generados), pero los datos no llegaron a la nube. Pasos:

1. Verificar conexión a internet
2. Ejecutar manualmente: `python sync_tp_appsheet_drive.py --config google_sync_config.json`
3. Si falla con error de autenticación OAuth, el token puede haber vencido → correr el comando y autorizar desde el browser

### Portal no muestra los datos actualizados

El portal tiene cache de 5 minutos en memoria. Esperar 5 minutos y recargar. Si persiste:

1. Verificar que el sync terminó OK (paso 3 del BAT)
2. Verificar en Google Sheets que la hoja `clientes_oportunidad` tiene fecha de hoy
3. Si el portal está en Render, verificar el log del servicio

---

## Salida esperada del pipeline

```
Fecha zona: 2026-05-15 (JU)
Vendedores activos: 5
Clientes procesados: 312
PDFs generados: 6 (5 vendedor + 1 gerencial)
CSVs exportados: 4
Sync Google Sheets: OK
Sync Google Drive: 6 PDFs subidos
```

---

## Archivos de salida por ejecución

| Archivo | Ubicación | Descripción |
|---|---|---|
| Vendedor_2_JU.pdf | output/PDF_VENDEDORES/2026-05-15/ | PDF individual vendedor |
| Gerencial_JU.pdf | output/PDF_GERENCIAL/2026-05-15/ | PDF gerencial |
| pdf_index.csv | output/APPSHEET/ | Índice de PDFs para el portal |
| clientes_oportunidad.csv | output/APPSHEET/ | Clientes con KPIs TP |
| foco_productos.csv | output/APPSHEET/ | Productos foco por vendedor |
| tp_objetivos_resumen.csv | output/APPSHEET/ | Objetivos con cumplimiento |
| Control_TP_Portafolio_PyP.xlsx | output/ | Excel completo (backup) |

---

## Contacto ante problemas

- Desarrollador: Matías Torres — matiastorres.pyp@gmail.com
- Repositorio: `C:\Orbit\TP_PYP_CLEAN` (git)
- Logs del portal: Render dashboard → Logs
