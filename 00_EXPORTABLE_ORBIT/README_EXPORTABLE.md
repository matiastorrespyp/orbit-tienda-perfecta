# Orbit Tienda Perfecta — Kit Exportable V2

## Qué es este kit

Este directorio contiene todo lo necesario para implementar Orbit Tienda Perfecta en una nueva distribuidora, usando el **motor común** del sistema y reemplazando solo la **configuración específica** de cada cliente.

El principio es: **el código nunca cambia entre distribuidoras. Solo cambia la configuración.**

---

## Estructura del kit

```
00_EXPORTABLE_ORBIT/
├── README_EXPORTABLE.md            → este archivo
├── CONFIG_DISTRIBUIDORA_TEMPLATE.json  → plantilla de configuración completa
├── CHECKLIST_NUEVA_DISTRIBUIDORA.md    → checklist operativo de implementación
├── SETUP_DISTRIBUIDORA_PLAN.md         → diseño del script de setup automático
└── VALIDADORES_REQUERIDOS.md           → validaciones previas al deploy
```

Para documentación técnica detallada, ver `00_DOCS_ORBIT/`.

---

## Motor común vs. configuración por distribuidora

### Lo que es igual en todas las distribuidoras

| Componente | Descripción |
|---|---|
| `tp_pyp_run_fast_ORBIT_appsheet.py` | Pipeline de análisis y generación de PDFs |
| `clean_venta.py` | Normalización de ventas |
| `sync_tp_appsheet_drive.py` | Sincronización Google Sheets + Drive |
| `portal/` | Portal web completo (Astro + React) |
| Estructura de hojas Google Sheets | Mismos nombres y columnas |
| Diseño de PDFs | Layout, colores, branding Orbit |
| Lógica de Tienda Perfecta | Reglas de cumplimiento, taxonomía P/A/B/C |

### Lo que cambia por distribuidora

| Qué cambia | Dónde se configura |
|---|---|
| Nombre de la distribuidora | `CONFIG_DISTRIBUIDORA_TEMPLATE.json` |
| Logo / branding | `assets/logo_distrib.png` |
| Vendedores (IDs y nombres) | `config_app.json` + `VENDOR_NAMES` en Render |
| Objetivos por vendedor/zona | `inputs/objetivo_vendedor_tp.xlsx` |
| Portafolio de SKUs TP | `inputs/Portafolio Infaltable - Argentina.pptx` |
| Spreadsheet ID de Google | `google_sync_config.json` + `SPREADSHEET_ID` en Render |
| Carpetas Drive | `google_sync_config.json` |
| Contraseñas del portal | `config_app.json` + variables Render |
| Service Account | Variable `GOOGLE_SERVICE_ACCOUNT_JSON` en Render |
| URL del portal | Asignada por Render al crear el Web Service |

---

## Proceso de implementación resumido

```
1. DISTRIBUIDORA entrega sus datos fuente
        ↓
2. IMPLEMENTADOR completa CONFIG_DISTRIBUIDORA_TEMPLATE.json
        ↓
3. IMPLEMENTADOR corre validaciones (VALIDADORES_REQUERIDOS.md)
        ↓
4. IMPLEMENTADOR sigue CHECKLIST_NUEVA_DISTRIBUIDORA.md
        ↓
5. Pipeline de prueba con datos reales
        ↓
6. Deploy portal en Render
        ↓
7. Capacitación al operador (runbook: 00_DOCS_ORBIT/05_RUNBOOK_OPERATIVO_DIARIO.md)
        ↓
8. GO LIVE
```

---

## Entregables que la distribuidora debe proveer

| Archivo / dato | Formato | Quién lo entrega |
|---|---|---|
| Ventas históricas (30–90 días) | CSV o Excel | Área de sistemas / administración |
| Padrón de clientes con TAXONOMIA | Excel (.xlsx) | Área comercial |
| Portafolio de SKUs TP | PowerPoint (.pptx) | Gerencia / marca |
| Lista de precios | Excel (.xlsx) | Área de precios |
| Objetivos por vendedor | Excel (.xlsx) | Gerencia comercial |
| Logo de la distribuidora | PNG fondo transparente | Marketing |
| Nombres de vendedores | Lista texto | Gerencia |
| Cuenta Google con Drive y Sheets | Acceso | IT / gerencia |

---

## Tiempo estimado de implementación

| Etapa | Tiempo |
|---|---|
| Recepción y revisión de datos fuente | 2–4 horas |
| Configuración Google Cloud + credenciales | 1–2 horas |
| Primer pipeline de validación | 1–2 horas |
| Ajustes de datos (corrección de errores) | 2–8 horas (varía) |
| Deploy portal + variables de entorno | 1 hora |
| Capacitación operador | 30–60 minutos |
| **Total** | **1–2 días hábiles** |

---

## Referencia cruzada

| Necesidad | Archivo |
|---|---|
| Entender la arquitectura completa | `00_DOCS_ORBIT/02_ARQUITECTURA_TECNICA.md` |
| Saber qué columnas requiere cada input | `00_DOCS_ORBIT/07_MAPEO_DATOS_REQUERIDOS.md` |
| Configurar Google Cloud y Render | `00_DOCS_ORBIT/06_CONFIGURACION_GOOGLE_RENDER.md` |
| Rutina diaria del operador | `00_DOCS_ORBIT/05_RUNBOOK_OPERATIVO_DIARIO.md` |
| Errores comunes | `00_DOCS_ORBIT/08_PLAN_EXPORTABLE_V2.md` |
