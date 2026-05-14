# 01 — Proyecto Tienda Perfecta

## Qué es

Tienda Perfecta (TP) es un modelo comercial de la distribuidora PyP que define un estándar de presencia mínima de productos en cada cliente. Un cliente "tiene TP activo" cuando compra el set de SKUs acordados con la marca.

El proyecto Orbit Tienda Perfecta es el sistema que mide, visualiza y gestiona ese cumplimiento de forma diaria.

---

## Problema que resuelve

| Antes | Con Orbit TP |
|---|---|
| La gerencia no sabía qué vendedores cumplían el estándar | Dashboard gerencial en tiempo real por vendedor y taxonomía |
| Los vendedores no sabían qué clientes priorizar | Panel individual con lista ordenada por urgencia |
| Los informes eran manuales en Excel | Pipeline automatizado que genera PDFs y actualiza la nube |
| Los datos tardaban días en procesarse | BAT diario de 2–3 minutos que actualiza todo |

---

## Actores del sistema

| Actor | Rol | Acceso |
|---|---|---|
| **Matías Torres** | Propietario / desarrollador | Acceso total, corre el pipeline |
| **Gerencia** | Supervisión y toma de decisiones | Portal gerencial (contraseña `MGMT_PASSWORD`) |
| **Vendedores** | Ejecución en campo | Portal individual (contraseña `VENDOR_PASSWORD`) |
| **Distribuidora** | Dueña del negocio | Recibe reportes y PDFs |

---

## Flujo general

```
DATOS FUENTE (Excel/CSV)
        ↓
  PIPELINE PYTHON
  tp_pyp_run_fast_ORBIT_appsheet.py
        ↓
  ┌─────────────────────────────────┐
  │  output/PDF_VENDEDORES/         │  → Drive (vendedores)
  │  output/PDF_GERENCIAL/          │  → Drive (gerencia)
  │  output/APPSHEET/*.csv          │  → Google Sheets (portal)
  │  output/Control_TP_*.xlsx       │  → local (backup)
  └─────────────────────────────────┘
        ↓
  SYNC GOOGLE (sync_tp_appsheet_drive.py)
        ↓
  PORTAL WEB (Render/Railway)
  ┌──────────────────┐  ┌──────────────────┐
  │  Gerencia        │  │  Vendedor         │
  │  /gerencia       │  │  /vendedor        │
  └──────────────────┘  └──────────────────┘
```

---

## Hitos del proyecto

| Fecha | Hito |
|---|---|
| 2026-04 | Pipeline Python funcional, generación de PDFs |
| 2026-04 | Portal Astro/React con autenticación y datos locales |
| 2026-05 | Migración a Google Sheets + Google Drive |
| 2026-05 | Deploy en Render (Playwright QA 7/7) |
| 2026-05 | Dashboard gerencial con objetivos, taxonomía, PDFs |

---

## Estado actual

- Pipeline: operativo, corre diario con `RUN_TP_FAST_ORBIT_APPSHEET_SYNC.bat`
- Portal: desplegado en Render (pendiente Service Account real en producción)
- Datos: Google Sheets como fuente de verdad para el portal
- PDFs: almacenados en Google Drive, accedidos vía redirect

---

## Archivos NO tocar sin revisión

- `inputs/` — datos fuente de la distribuidora
- `credenciales/` — claves OAuth y Service Account
- `config_app.json` — contraseñas y nombres de vendedores
- `google_sync_config.json` — IDs de Spreadsheet y carpetas Drive
