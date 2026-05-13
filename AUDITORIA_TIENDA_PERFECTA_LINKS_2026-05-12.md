# Auditoría — Links Vendedores Tienda Perfecta
**Fecha:** 2026-05-12  
**Proyecto:** `C:\Users\usuario\OneDrive\Desktop\TP_PYP`  
**Autor:** Claude Code · Orbit PyP

---

## 1. Diagnóstico — Mapa del Proyecto

### Arquitectura actual

```
TP_PYP/
├── inputs/                        ← Excel de GESCOM (gescom.xlsx, ventas.csv, objetivos)
├── output/
│   ├── APPSHEET/                  ← CSVs exportados para el portal
│   │   ├── clientes_oportunidad.csv
│   │   ├── foco_productos.csv
│   │   ├── pdf_index.csv
│   │   ├── tp_facturacion_comparativa.csv
│   │   └── tp_objetivos_resumen.csv
│   ├── PDF_VENDEDORES/            ← PDFs por vendedor y fecha (p.ej. Vendedor_2_VI.pdf)
│   └── PDF_GERENCIAL/             ← PDFs de resumen gerencial
├── portal/                        ← App web Astro SSR (Node.js, puerto 4321)
│   ├── src/lib/data.ts            ← LEE LOS CSVs DE output/APPSHEET vía fs.readFileSync
│   ├── src/lib/config.ts          ← LEE config_app.json vía fs.readFileSync
│   ├── src/pages/api/pdf.ts       ← Sirve PDFs desde output/ vía fs.readFileSync
│   └── dist/                      ← Build producción (ya compilado)
├── app_orbit_tp.py                ← App Streamlit principal (puerto 8501)
├── tp_pyp_run_fast_ORBIT_appsheet.py ← Pipeline: procesa Excel → genera CSVs + PDFs
├── sync_tp_appsheet_drive.py      ← Sube CSVs a Google Sheets + PDFs a Google Drive
├── start_public.py                ← Expone Streamlit con ngrok (pyngrok)
├── config_app.json                ← Contraseñas, nombres vendedores, token ngrok
└── google_sync_config.json        ← IDs de carpetas Drive y Spreadsheet
```

### Flujo de datos

```
[GESCOM Excel] → tp_pyp_run_fast_ORBIT_appsheet.py
                 → output/APPSHEET/*.csv
                 → output/PDF_VENDEDORES/*.pdf
                 → output/PDF_GERENCIAL/*.pdf
                 
[output/APPSHEET/*.csv] → portal/src/lib/data.ts (fs.readFileSync local)
                         → portal web en localhost:4321

[output/*] → sync_tp_appsheet_drive.py
             → Google Sheets (ID: 1TzGQSnvb3SIBJwAHyy92x3JaCgeEHh1xuR7mgCemrn0)
             → Google Drive carpeta PDFs vendedores (ID: 1Qmk8-LcNt0f_MQR_4kip7Ni_iUUL9MZa)
             → Google Drive carpeta PDFs gerencial (ID: 1tlBd2GrWuJAjYX0dwn6dsfbnDh6gM8PQ)
```

---

## 2. Estado Actual — Links Detectados

| Tipo | URL / Ruta | Accesible hoy | Requiere PC |
|------|-----------|--------------|-------------|
| Portal Astro (SSR) | `http://localhost:4321` | Solo en la PC local | ✅ Sí |
| Streamlit principal | `http://localhost:8501` | Solo en la PC local | ✅ Sí |
| ngrok (configurado) | `estanque-itunes-morbidamente.ngrok-free.app` | Sí, mientras PC está encendida | ✅ Sí |
| ngrok (último token) | `https://pond-itunes-morbidly.ngrok-free.dev` | Probablemente caducó | ✅ Sí |
| Google Sheets | ID `1TzGQSnvb3SIBJwAHyy92x3JaCgeEHh1xuR7mgCemrn0` | Sí, si se corrió sync | ❌ No |
| Google Drive PDFs | ID `1Qmk8-LcNt0f_MQR_4kip7Ni_iUUL9MZa` | Sí, si se corrió sync | ❌ No |

---

## 3. Problema Principal

**El portal web (Astro SSR) lee datos directamente del sistema de archivos local** (`fs.readFileSync`) desde rutas absolutas en la PC de desarrollo. Esto significa:

1. El servidor Node.js **debe estar corriendo en la misma máquina donde están los archivos**.
2. Si se intenta desplegar el portal en cualquier hosting externo, los CSVs y PDFs no existen allí.
3. El túnel ngrok es una solución válida temporalmente pero frágil: si la PC se apaga, se reinicia, o ngrok se cae, el link muere.
4. No hay mecanismo de reconexión automática ni watchdog.

**Resultado para el vendedor:** el link que reciben deja de funcionar periódicamente, sin aviso.

---

## 4. Evaluación de Opciones de Publicación

### Opción 1 — AppSheet

| Aspecto | Detalle |
|---------|---------|
| Costo | Gratis (1 app, 10 usuarios) / $10 usuario/mes plan Core |
| Dificultad | Media — hay que construir la app en la UI de AppSheet |
| Estabilidad | Alta — infraestructura de Google |
| Seguridad | Media — control por dominio Google |
| Actualización diaria | Automática si el sync corre (ya sube a Sheets) |
| Requiere PC encendida | No (solo para correr el pipeline) |
| Recomendación | Sirve para datos tabulares (clientes, focos). **No sirve bien para mostrar PDFs inline.** |

### Opción 2 — Apps Script Web App ⭐ (camino más corto)

| Aspecto | Detalle |
|---------|---------|
| Costo | Gratis |
| Dificultad | Baja-media — el sync YA sube datos a Sheets |
| Estabilidad | Alta — Google Cloud |
| Seguridad | Control por Google account o dominio |
| Actualización diaria | Automática — lee de Sheets que ya se sincronizan |
| Requiere PC encendida | No (solo para correr el pipeline diario) |
| Recomendación | **Muy viable como puente.** Se puede hacer una Web App que lea las hojas ya existentes y muestre dashboard + links a PDFs de Drive. Tiempo estimado: 1-2 días de desarrollo. |

### Opción 3 — Portal estático hospedado (Astro static)

| Aspecto | Detalle |
|---------|---------|
| Costo | Gratis (Vercel, Netlify, Cloudflare Pages) |
| Dificultad | Alta — el portal actual es SSR (server-side), no estático |
| Estabilidad | Muy alta |
| Seguridad | Necesita auth implementada en el cliente |
| Actualización diaria | Requiere rebuild + deploy en cada corrida del pipeline |
| Requiere PC encendida | No, pero sí para hacer el deploy diario |
| Recomendación | No aplica sin refactorizar la arquitectura del portal. |

### Opción 4 — Cloudflare Tunnel permanente con cuenta

| Aspecto | Detalle |
|---------|---------|
| Costo | Gratis con cuenta Cloudflare |
| Dificultad | Baja — instalar cloudflared como servicio de Windows |
| Estabilidad | Alta mientras PC esté encendida |
| Seguridad | Alta — TLS nativo |
| Actualización diaria | N/A — el tunnel solo expone |
| Requiere PC encendida | **Sí — mismo problema que ngrok** |
| Recomendación | Descartado como solución final per instrucciones. |

### Opción 5 — VPS / Hosting (Railway, Render, Fly.io) ⭐⭐ (RECOMENDADA)

| Aspecto | Detalle |
|---------|---------|
| Costo | Gratis (Render free tier) / $5-7/mes (Railway Starter) |
| Dificultad | Media — cambiar `data.ts` para leer de Google Sheets API en lugar de `fs` |
| Estabilidad | Muy alta — servidor 24/7 |
| Seguridad | Alta — HTTPS nativo, auth ya implementada en el portal |
| Actualización diaria | Automática — el pipeline actualiza Sheets, el portal lee Sheets |
| Requiere PC encendida | **No** |
| Recomendación | **Opción recomendada a largo plazo.** El portal Astro ya está construido y funciona. Solo necesita cambiar la fuente de datos de `fs` a Google Sheets API. |

### Opción 6 — Google Drive + Apps Script (híbrido)

| Aspecto | Detalle |
|---------|---------|
| Costo | Gratis |
| Dificultad | Baja — la infra de sync ya existe |
| Estabilidad | Alta |
| Seguridad | Media — links de Drive son compartibles sin login |
| Actualización diaria | Automática si sync corre |
| Requiere PC encendida | No |
| Recomendación | Excelente para acceso a PDFs individuales. Combinado con Apps Script para el índice. |

### Opción 7 — GitHub Actions + Render (deploy automático)

| Aspecto | Detalle |
|---------|---------|
| Costo | Gratis (GitHub Actions) + $0-7/mes Render |
| Dificultad | Media-alta — requiere GitHub Actions workflow |
| Estabilidad | Alta |
| Seguridad | Alta |
| Actualización diaria | Pipeline corre, pushea a GitHub, Actions re-deploya el portal |
| Requiere PC encendida | Solo para correr el pipeline de datos |
| Recomendación | Ideal si se quiere automatizar el deploy completo. |

---

## 5. Opción Recomendada

### Ruta en dos fases

#### Fase 1 — Corto plazo (1-2 días, costo cero): Apps Script Web App desde Sheets existentes

El pipeline **ya** sube datos a Google Sheets (ID `1TzGQSnvb3SIBJwAHyy92x3JaCgeEHh1xuR7mgCemrn0`).  
Los PDFs **ya** están en Google Drive (carpeta `1Qmk8-LcNt0f_MQR_4kip7Ni_iUUL9MZa`).

**Lo que hay que hacer:**
1. Crear un Apps Script ligado al Spreadsheet existente.
2. Escribir una Web App que:
   - Autentique al vendedor por número (o contraseña simple).
   - Lea la hoja `pdf_index` y muestre el link al PDF del día en Drive.
   - Muestre clientes/focos desde `clientes_oportunidad` y `foco_productos`.
3. Publicar como Web App con acceso "Anyone with the link".
4. El URL resultante (`https://script.google.com/macros/s/XXXXX/exec`) es **permanente y no requiere PC encendida**.

**Ventaja clave:** No modifica el portal existente. No cambia el pipeline. Se usa lo que ya funciona.

#### Fase 2 — Mediano plazo (3-5 días, costo $0-7/mes): Portal Astro en Render/Railway

**Lo que hay que hacer:**
1. Modificar `portal/src/lib/data.ts`:  
   - Reemplazar `fs.readFileSync` por llamadas a Google Sheets API (`googleapis` npm package).  
   - El Spreadsheet ID ya está en `google_sync_config.json`.
2. Modificar `portal/src/pages/api/pdf.ts`:  
   - En lugar de `fs.readFileSync`, redirigir al link de Google Drive del PDF (ya en `pdf_index.csv → RutaPDF`).
3. Deploy en Render.com (gratis, auto-deploy desde GitHub).
4. El vendedor accede a `https://orbit-tp.onrender.com` — permanente, sin PC.

---

## 6. Pasos Para Implementar (Fase 1)

```
1. Abrir Google Sheets: https://docs.google.com/spreadsheets/d/1TzGQSnvb3SIBJwAHyy92x3JaCgeEHh1xuR7mgCemrn0
2. Ir a Extensiones > Apps Script
3. Crear archivo: webapp.gs
4. Escribir doGet(e) que:
   a) Lee pdf_index sheet
   b) Filtra por VendedorID del parámetro
   c) Devuelve HTML con link al PDF en Drive
5. Publicar: Deploy > New Deployment > Web App
   - Execute as: Me (usuario Google de PyP)
   - Who has access: Anyone
6. Copiar URL y distribuir a vendedores
7. En cada corrida del pipeline: sync_tp_appsheet_drive.py actualiza Sheets
   → la Web App ya muestra datos nuevos sin ningún paso extra
```

---

## 7. Riesgos

| Riesgo | Mitigación |
|--------|-----------|
| sync_tp_appsheet_drive.py no corre → datos desactualizados | Agregar el sync al final del pipeline BAT; eventualmente automatizar con Task Scheduler |
| Google OAuth token expira | El token se renueva automáticamente; documentar el proceso de re-auth |
| PDFs en Drive con permisos incorrectos | Verificar que la carpeta tenga acceso "Anyone with link" o restringir por dominio |
| Apps Script hit quota (límite gratuito) | Con 5-6 vendedores y uso diario, no hay riesgo. Límite: 30,000 llamadas/día |
| Render free tier duerme después de 15 min inactividad | Upgrade a $7/mes o usar Railway $5/mes para evitar cold start |

---

## 8. Archivos que NO deben tocarse

- `tp_pyp_run_fast_ORBIT_appsheet.py` — pipeline de datos productivo
- `output/APPSHEET/*.csv` — generados por el pipeline, no editar a mano
- `output/PDF_VENDEDORES/` — generados por el pipeline
- `inputs/*.xlsx` — fuente de datos de GESCOM
- `credenciales/` — tokens OAuth de Google
- `config_app.json` — configuración de contraseñas (no commitear)
- `portal/src/` — no tocar hasta tener plan de Fase 2 acordado

---

## 9. Siguiente Prompt Sugerido

```
PROMPT_TP_002_APPS_SCRIPT_WEBAPP.md

Contexto: El sync ya sube datos a Google Sheets (ID: 1TzGQSnvb3SIBJwAHyy92x3JaCgeEHh1xuR7mgCemrn0)
y PDFs a Google Drive (carpeta: 1Qmk8-LcNt0f_MQR_4kip7Ni_iUUL9MZa).

Tarea: Crear un Apps Script Web App que permita a cada vendedor:
1. Ingresar con su número (VendedorID: 2-6) y contraseña "tp2026"
2. Ver su PDF del día desde Google Drive
3. Ver sus clientes objetivo y focos del día desde las hojas de Sheets

No modificar el portal Astro existente.
No modificar el pipeline Python.
Solo crear el Apps Script y documentar el URL resultante.
```

---

*Generado por Claude Code · Orbit PyP · 2026-05-12*
