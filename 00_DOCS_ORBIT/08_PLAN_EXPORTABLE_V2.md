# 08 — Plan Exportable V2

## Propuesta de valor

Orbit TP es un sistema de gestión de Tienda Perfecta que una distribuidora puede adoptar para:

- Medir el cumplimiento de estándares de exhibición en tiempo real
- Dar a cada vendedor una lista diaria priorizada de clientes a visitar
- Dar a gerencia visibilidad de avance por vendedor y por taxonomía de cliente
- Automatizar la generación de informes diarios (PDFs + portal web)

---

## Componentes del sistema

### 1. Pipeline de análisis (Python, local)
- Procesa ventas, padrón de clientes y objetivos
- Calcula cumplimiento de Tienda Perfecta por cliente y vendedor
- Genera PDFs individuales para vendedores
- Genera PDF gerencial de resumen
- Exporta datos a Google Sheets y Drive

### 2. Portal web (Astro + React, Render)
- Dashboard de gerencia: KPIs, objetivos, ranking de vendedores, acceso a PDFs
- Dashboard de vendedor: lista de clientes por urgencia, SKUs a reponer, PDF propio
- Autenticación por contraseña, sin registro de usuarios
- Datos actualizados sin redeploy (Google Sheets como fuente)

### 3. Sync Google (Python, incluido en BAT)
- Sube CSVs a Google Sheets automáticamente
- Sube PDFs a Google Drive automáticamente
- No requiere intervención manual más allá de correr el BAT

---

## Modelo operativo para una nueva distribuidora

```
Cada día hábil:
  1. Exportar ventas del sistema (2 minutos)
  2. Correr RUN_TP_FAST_ORBIT_APPSHEET_SYNC.bat (2–3 minutos)
  3. Verificar portal (1 minuto)
  Total: ~6 minutos de trabajo manual

Vendedores:
  - Acceden al portal desde celular o PC
  - Ven su lista de clientes ordenada por urgencia
  - Descargan o ven su PDF del día

Gerencia:
  - Dashboard disponible 24/7 en la URL del portal
  - No depende del operador para consultar datos
```

---

## Prerrequisitos por distribuidora

| Requisito | Descripción |
|---|---|
| Sistema de ventas | Que permita exportar CSV de ventas diarias |
| Padrón de clientes | Con clasificación TAXONOMIA (P/A/B/C) |
| Portafolio de SKUs | Lista de productos que componen TP |
| Objetivos por vendedor | Cantidad de clientes TP objetivo por zona/día |
| PC Windows con Python | Para correr el pipeline diario |
| Cuenta Google Workspace | Para Sheets, Drive y Google Cloud |
| Repositorio GitHub | Para deploy en Render |

---

## Tiempos de implementación estimados

| Fase | Tiempo | Dependencia |
|---|---|---|
| Datos fuente y formato | 1–2 días | Disponibilidad de los datos |
| Configuración Google Cloud | 1 hora | Acceso a Google Cloud Console |
| Primer pipeline de prueba | 2 horas | Datos fuente listos |
| Validación de PDFs | 1 hora | Pipeline OK |
| Deploy portal en Render | 1 hora | Repo en GitHub |
| Capacitación operador | 30 minutos | Portal OK |
| **Total** | **2–4 días hábiles** | |

---

## Errores comunes y soluciones

### Pipeline

| Error | Causa probable | Solución |
|---|---|---|
| `FileNotFoundError: inputs/ventas.csv` | Archivo no existe o nombre incorrecto | Verificar nombre exacto del archivo |
| `KeyError: 'VendedorID'` | Columna no encontrada en CSV | Verificar nombres de columnas en `clean_venta.py` |
| `No existe google_sync_config.json` | Archivo faltante o en otra carpeta | Crear el archivo con los IDs correctos |
| `HttpError 400: Unable to parse range` | Nombre de hoja incorrecto en Sheets | Verificar que el nombre de la hoja existe en el Spreadsheet |
| PDFs generados pero vacíos | Sin ventas para esa zona/fecha | Normal si no hay actividad ese día |
| `ValueError: NaN` en objetivos | objetivo_vendedor_tp.xlsx con celdas vacías | Completar todas las filas del archivo |

### Google Sync

| Error | Causa probable | Solución |
|---|---|---|
| `Token expired` / `invalid_grant` | Token OAuth vencido | Borrar `google-oauth-token.json` y re-autorizar |
| `The caller does not have permission` | Spreadsheet o Drive no compartido con la cuenta | Compartir con el email del OAuth user |
| `403 Forbidden` (Service Account) | Spreadsheet no compartido con SA | Compartir con el email del Service Account |
| `File not found` en Drive | Carpeta Drive con ID incorrecto | Verificar IDs en `google_sync_config.json` |

### Portal

| Error | Causa probable | Solución |
|---|---|---|
| Dashboard vacío (sin datos) | GSheets no actualizados o SA sin acceso | Verificar sync + permisos SA |
| PDF no abre (404) | Archivo no subido a Drive o SA sin acceso a Drive | Verificar sync Drive + permisos SA |
| Login siempre falla | `MGMT_PASSWORD` o `VENDOR_PASSWORD` no definidas | Verificar variables de entorno en Render |
| Portal no arranca en Render | Error en build o start command | Revisar logs en Render dashboard |
| `GOOGLE_SERVICE_ACCOUNT_JSON no está definida` | Variable de entorno faltante | Agregar en Render → Environment |

### Datos

| Problema | Causa probable | Solución |
|---|---|---|
| Vendedor no aparece en portal | VendedorID no coincide entre ventas y config | Verificar `VENDOR_NAMES` en config |
| Cliente sin % de cumplimiento | ClienteID no existe en gescom.xlsx | Verificar padrón de clientes |
| Taxonomía P/A/B/C sin datos | Columna TAXONOMIA vacía o con valores distintos | Verificar valores exactos: P, A, B, C |
| Objetivos en 0 | objetivo_vendedor_tp.xlsx no tiene esa zona | Completar todas las combinaciones vendedor/zona |

---

## Roadmap V2 — Mejoras planificadas

| Funcionalidad | Descripción | Prioridad |
|---|---|---|
| Facturación comparativa | KPI de facturación TP vs no-TP en portal | Alta |
| Histórico de cumplimiento | Gráfico de evolución diaria/mensual | Media |
| AppSheet activo | CRUD de clientes TP desde celular | Media |
| Notificaciones | WhatsApp/email con resumen diario | Baja |
| Multi-distribuidora | Un portal con múltiples distribuidoras | Baja |
| API pública | Webhook para integrar con otros sistemas | Baja |

---

## Modelo de entrega para nuevas distribuidoras

### Entregables

1. Código fuente completo (repositorio GitHub privado)
2. Documentación `00_DOCS_ORBIT/` (este conjunto de archivos)
3. Sesión de configuración inicial (2–3 horas)
4. Soporte durante primer mes de operación

### Personalización incluida

- Nombres de vendedores y contraseñas
- IDs de Spreadsheet y Drive
- Portafolio de SKUs TP específico de la distribuidora
- Objetivos por vendedor

### Lo que la distribuidora provee

- Datos fuente en los formatos descritos en `07_MAPEO_DATOS_REQUERIDOS.md`
- Cuenta Google con acceso a Drive y Sheets
- PC Windows con Python 3.10+ instalado
- Repositorio GitHub (puede ser el mismo fork)
