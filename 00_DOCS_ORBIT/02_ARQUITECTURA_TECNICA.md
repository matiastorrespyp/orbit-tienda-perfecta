# 02 — Arquitectura Técnica

## Stack completo

```
┌────────────────────────────────────────────────────────────────────┐
│  PC LOCAL (Windows 10)                                             │
│                                                                    │
│  inputs/              → Excel/CSV fuente (GESCOM, ventas, obj.)   │
│  clean_venta.py       → limpia ventas.csv → venta_limpia.csv      │
│  tp_pyp_run_fast_     → pipeline principal Python                 │
│    ORBIT_appsheet.py  → genera PDFs + CSVs para Sheets            │
│  sync_tp_appsheet_    → sube CSVs a Sheets y PDFs a Drive         │
│    drive.py                                                        │
│  RUN_TP_FAST_ORBIT_   → BAT orquestador de los 3 pasos            │
│    APPSHEET_SYNC.bat                                               │
│                                                                    │
│  Streamlit app (app_orbit_tp.py) — uso interno, no producción     │
└─────────────────────────┬──────────────────────────────────────────┘
                          │ sube datos
              ┌───────────▼──────────────┐
              │  Google Cloud            │
              │                          │
              │  Google Sheets           │  ← fuente de datos portal
              │  ├─ pdf_index            │
              │  ├─ clientes_oportunidad │
              │  ├─ foco_productos       │
              │  └─ tp_objetivos_resumen │
              │                          │
              │  Google Drive            │  ← PDFs
              │  ├─ PDF_GERENCIAL/       │
              │  └─ PDF_VENDEDORES/      │
              └───────────┬──────────────┘
                          │ lee en cada request
              ┌───────────▼──────────────┐
              │  Render (Node.js 24/7)   │
              │                          │
              │  Portal Astro + React    │
              │  ├─ /gerencia            │
              │  ├─ /vendedor            │
              │  ├─ /api/login           │
              │  ├─ /api/logout          │
              │  └─ /api/pdf             │
              └──────────────────────────┘
```

---

## Componentes Python (pipeline local)

| Archivo | Propósito |
|---|---|
| `clean_venta.py` | Normaliza el CSV de ventas exportado de GESCOM |
| `tp_pyp_run_fast_ORBIT_appsheet.py` | Núcleo: carga datos, calcula TP, genera PDFs, exporta CSVs |
| `sync_tp_appsheet_drive.py` | Sube CSVs a Google Sheets y PDFs a Google Drive |
| `sync_excel_to_gsheets.py` | Actualiza app Streamlit Cloud (uso secundario) |
| `app_orbit_tp.py` | Interfaz Streamlit para uso interno (no producción) |

### Dependencias Python

```
streamlit>=1.30.0
pandas>=2.0.0
plotly>=5.18.0
openpyxl>=3.1.0
gspread>=6.0.0
google-auth>=2.28.0
google-auth-oauthlib>=1.2.0
google-api-python-client
reportlab
```

Instalar: `pip install -r requirements.txt -r requirements_google_sync.txt`

---

## Componentes del portal (Astro + React)

```
portal/
├── src/
│   ├── pages/
│   │   ├── index.astro          → landing / login
│   │   ├── gerencia.astro       → dashboard gerencial (SSR)
│   │   ├── vendedor.astro       → dashboard vendedor (SSR)
│   │   └── api/
│   │       ├── login.ts         → valida contraseña, setea cookie
│   │       ├── logout.ts        → borra cookie
│   │       └── pdf.ts           → redirige a Google Drive view URL
│   ├── components/
│   │   ├── Login.tsx            → formulario de acceso
│   │   ├── GerenciaDashboard.tsx → vista gerencial React
│   │   └── VendedorDashboard.tsx → vista vendedor React
│   ├── lib/
│   │   ├── config.ts            → lee variables de entorno
│   │   ├── google.ts            → auth SA + readSheet() + getDriveViewUrl()
│   │   └── data.ts              → getClientes(), getObjetivos(), getPdfs(), etc.
│   └── middleware.ts            → protege rutas con cookie de sesión
├── astro.config.mjs             → output:server, adapter:node, port:4321
└── playwright.config.ts         → tests E2E (7 smoke tests)
```

### Variables de entorno del portal

| Variable | Descripción |
|---|---|
| `GOOGLE_SERVICE_ACCOUNT_JSON` | JSON completo de la cuenta de servicio (una sola línea) |
| `SPREADSHEET_ID` | ID del Google Spreadsheet con los datos |
| `MGMT_PASSWORD` | Contraseña para acceso de gerencia |
| `VENDOR_PASSWORD` | Contraseña para acceso de vendedores |
| `VENDOR_NAMES` | JSON `{"2":"Nombre","3":"Nombre"}` — override de nombres por VendedorID |
| `HOST` | `0.0.0.0` (requerido en Render) |
| `PORT` | Inyectado automáticamente por Render |

---

## Flujo de datos en el portal

```
Request a /gerencia
        ↓
middleware.ts → verifica cookie de sesión
        ↓
gerencia.astro (SSR) → llama data.ts
        ↓
data.ts → getObjetivos(), getClientes(), getPdfs(), getFocos()
        ↓
google.ts → readSheet(sheetName)
        ↓
Google Sheets API v4 (Service Account)
        ↓
Cache 5 min en memoria → respuesta JSON al componente React
        ↓
GerenciaDashboard.tsx → renderiza KPIs, tablas, PDFs
```

---

## Google Sheets — hojas requeridas

| Hoja | Origen | Modo escritura |
|---|---|---|
| `pdf_index` | `output/APPSHEET/pdf_index.csv` | Desde B1 (columna A = fórmula ID) |
| `clientes_oportunidad` | `output/APPSHEET/clientes_oportunidad.csv` | Desde B1 |
| `foco_productos` | `output/APPSHEET/foco_productos.csv` | Desde B1 |
| `tp_objetivos_resumen` | `output/APPSHEET/tp_objetivos_resumen.csv` | Desde A1 (full overwrite) |

---

## Autenticación

- **Pipeline local** → OAuth user (browser en primer uso, token guardado)
- **Portal en Render** → Service Account JSON (sin browser, 24/7)
- **Acceso usuario portal** → contraseña simple + cookie `httpOnly` de sesión

---

## Deployment

- **Hosting**: Render (Web Service, Node runtime)
- **Build**: `npm install && npm run build` desde `/portal`
- **Start**: `node dist/server/entry.mjs`
- **Plan B**: Railway (misma configuración)
- **CI**: sin pipeline automático — build local + Playwright antes de push
